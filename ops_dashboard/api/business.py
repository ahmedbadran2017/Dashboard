"""Company-cockpit metrics beyond the order pipeline: products, cash, profit,
and the storefront top-of-funnel.

Design notes grounded in the live data (verified 2026-07):
- Live P&L from GL is NOT reliable intraday — invoice posting lags, so a fixed
  "this month" reads near-zero early in the month, and multi-company GL mixes
  intercompany. So `profit` uses a TRAILING 30-DAY window scoped to the operating
  company (income + COGS post there). The live revenue signal for "today" stays
  the Sales-Order value in kpis.py.
- `cash` sums only positive bank balances (accounts that actually hold money);
  a naive all-accounts sum goes negative because loans/overdrafts/FX accounts are
  also account_type=Bank.
- `storefront` calls Shopify (ShopifyQL) — sessions/conversion live outside
  ERPNext. Needs a token in site config; returns needs_config when absent.
"""
import frappe
from frappe.utils import flt

from ops_dashboard.api import _base as B

# Income + COGS post to the operating company; cash/banks span all companies.
OPERATING_COMPANY = "Justyol Morocco"


@frappe.whitelist()
def top_products(period="today", company=None, from_date=None, to_date=None, limit=6):
    """Best-selling items in the period, by units, with revenue."""
    B.assert_access()
    start, end, _, _, _ = B.resolve_period(period, from_date, to_date)
    params = {"start": str(start), "end": str(end), "limit": min(int(limit or 6), 20)}
    comp = B.company_cond(company, params)
    rows = frappe.db.sql(
        f"""
        SELECT soi.item_code, MAX(soi.item_name) AS name,
               ROUND(SUM(soi.qty)) AS qty, ROUND(SUM(soi.amount)) AS value
        FROM `tabSales Order Item` soi JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE so.docstatus = 1 AND so.transaction_date >= %(start)s
          AND so.transaction_date <= %(end)s AND {B.IS_REAL}{comp}
        GROUP BY soi.item_code ORDER BY qty DESC LIMIT %(limit)s
        """,
        params, as_dict=True,
    )
    for r in rows:
        r["qty"] = int(flt(r["qty"]))
        r["value"] = flt(r["value"])
    return rows


@frappe.whitelist()
def low_stock(company=None, threshold=30, limit=10):
    """Best-sellers (last 30 days) whose total on-hand quantity is low — the SKUs
    that cost real revenue if they stock out, ranked by how fast they sell."""
    B.assert_access()
    ck = f"ops_kpi:lowstock:{threshold}"

    def build():
        rows = frappe.db.sql(
            """
            SELECT b.item_code, MAX(i.item_name) AS name,
                   ROUND(SUM(b.actual_qty)) AS qty, s.sold
            FROM `tabBin` b JOIN `tabItem` i ON i.name = b.item_code
            JOIN (SELECT soi.item_code, SUM(soi.qty) AS sold
                  FROM `tabSales Order Item` soi JOIN `tabSales Order` so ON so.name = soi.parent
                  WHERE so.transaction_date >= CURDATE() - INTERVAL 30 DAY AND so.docstatus = 1
                  GROUP BY soi.item_code) s ON s.item_code = b.item_code
            GROUP BY b.item_code HAVING qty <= %(t)s ORDER BY s.sold DESC LIMIT %(limit)s
            """,
            {"t": int(threshold or 30), "limit": min(int(limit or 10), 30)}, as_dict=True,
        )
        for r in rows:
            r["qty"] = int(flt(r["qty"]))
            r["sold"] = int(flt(r["sold"]))
        return rows

    return B.cached(ck, build)


@frappe.whitelist()
def cash(company=None):
    """Cash position: operating bank accounts that hold money, plus COD cash still
    held by the carriers ('… Transactions' accounts). Only positive balances are
    summed — loans/overdrafts/FX accounts are also account_type=Bank and would
    drag a naive total negative."""
    B.assert_access()
    ck = "ops_kpi:cash"

    def build():
        rows = frappe.db.sql(
            """
            SELECT a.account_name AS name, ROUND(SUM(g.debit - g.credit)) AS bal,
                   CASE WHEN a.account_name LIKE '%%Transaction%%' THEN 'carrier'
                        WHEN a.account_name LIKE '%%Card%%' THEN 'card'
                        ELSE 'bank' END AS kind
            FROM `tabGL Entry` g JOIN `tabAccount` a ON a.name = g.account
            WHERE a.account_type = 'Bank' AND g.is_cancelled = 0
            GROUP BY a.account_name HAVING bal > 1000 ORDER BY bal DESC LIMIT 14
            """,
            as_dict=True,
        )
        for r in rows:
            r["bal"] = flt(r["bal"])
        bank = sum(r["bal"] for r in rows if r["kind"] == "bank")
        carrier = sum(r["bal"] for r in rows if r["kind"] == "carrier")
        card = sum(r["bal"] for r in rows if r["kind"] == "card")
        return {
            "currency": "MAD",
            "bank_total": bank,
            "carrier_float": carrier,
            "card_total": card,
            "total": bank + card + carrier,
            "accounts": rows[:8],
        }

    return B.cached(ck, build)


@frappe.whitelist()
def profit(company=None):
    """Trailing-30-day P&L for the operating company: revenue, COGS, gross margin,
    operating expenses, net — plus the top expense lines and open supplier
    payables (unbilled POs). 30-day rolling because GL posting lags intraday."""
    B.assert_access()
    ck = "ops_kpi:profit"

    def build():
        rows = frappe.db.sql(
            """
            SELECT a.account_name AS name, a.root_type AS rt,
                   ROUND(SUM(CASE WHEN a.root_type = 'Income' THEN g.credit - g.debit
                                  ELSE g.debit - g.credit END)) AS amt
            FROM `tabGL Entry` g JOIN `tabAccount` a ON a.name = g.account
            WHERE g.is_cancelled = 0 AND g.company = %(c)s
              AND a.root_type IN ('Income', 'Expense')
              AND g.posting_date >= CURDATE() - INTERVAL 30 DAY
            GROUP BY a.account_name
            """,
            {"c": OPERATING_COMPANY}, as_dict=True,
        )
        income = sum(flt(r["amt"]) for r in rows if r["rt"] == "Income")
        cogs = sum(flt(r["amt"]) for r in rows if r["rt"] == "Expense" and "Goods Sold" in (r["name"] or ""))
        opex = sum(flt(r["amt"]) for r in rows if r["rt"] == "Expense" and "Goods Sold" not in (r["name"] or ""))
        gross = income - cogs
        net = gross - opex
        top_exp = sorted(
            [r for r in rows if r["rt"] == "Expense" and flt(r["amt"]) > 0],
            key=lambda r: -flt(r["amt"]))[:5]
        payable = frappe.db.sql(
            """SELECT ROUND(SUM(grand_total * (100 - IFNULL(per_billed, 0)) / 100))
               FROM `tabPurchase Order`
               WHERE docstatus = 1 AND status IN ('To Bill', 'To Receive and Bill')"""
        )[0][0]
        return {
            "currency": "MAD", "company": OPERATING_COMPANY, "window": "30d",
            "revenue": flt(income), "cogs": flt(cogs), "opex": flt(opex),
            "gross": flt(gross), "net": flt(net),
            "margin": round(100.0 * gross / income, 1) if income else 0,
            "top_expenses": [{"name": r["name"], "amount": flt(r["amt"])} for r in top_exp],
            "supplier_payable": flt(payable),
        }

    return B.cached(ck, build)


# ── Storefront (Shopify) ─────────────────────────────────────────
_SINCE = {"today": "-0d", "d7": "-7d", "d30": "-30d", "custom": "-7d"}


def _shopify_creds():
    """Domain + Admin API token. Reuses the EXISTING ERPNext Shopify integration
    (the `Shopify Setting` single — its `password` field holds the access token,
    decrypted server-side), so no separate credentials need to be configured.
    Falls back to explicit site config (`shopify_domain`/`shopify_token`)."""
    try:
        if frappe.db.exists("DocType", "Shopify Setting"):
            s = frappe.get_single("Shopify Setting")
            url = (getattr(s, "shopify_url", "") or "").strip()
            if url and int(getattr(s, "enable_shopify", 0) or 0):
                token = s.get_password("password", raise_exception=False)
                if token:
                    return url, token
    except Exception:
        pass
    return frappe.conf.get("shopify_domain"), frappe.conf.get("shopify_token")


@frappe.whitelist()
def storefront(period="today", from_date=None, to_date=None):
    """Top-of-funnel from Shopify: sessions → cart → checkout → conversion.
    Credentials come from the existing ERPNext Shopify integration (see
    _shopify_creds). Returns {needs_config: true} when Shopify isn't reachable so
    the card shows a prompt instead of erroring. Requires the token to have the
    `read_reports` scope (ShopifyQL analytics)."""
    B.assert_access()
    domain, token = _shopify_creds()
    if not (domain and token):
        return {"needs_config": True}
    # Cache the external call (Shopify analytics update slowly and the API is
    # rate-limited) so page loads don't each make a 15s round-trip.
    return B.cached(f"ops_kpi:storefront:{period}", lambda: _fetch_storefront(domain, token, period))


def _fetch_storefront(domain, token, period):
    since = _SINCE.get(period, "-7d")
    shopifyql = (
        "FROM sessions SHOW sessions, sessions_with_cart_additions, "
        f"sessions_that_reached_checkout, conversion_rate SINCE {since} UNTIL today"
    )
    gql = "query($q: String!) { shopifyqlQuery(query: $q) { __typename ... on TableResponse { tableData { rowData } } parseErrors { message } } }"
    try:
        import requests
        resp = requests.post(
            f"https://{domain}/admin/api/2024-10/graphql.json",
            headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"},
            json={"query": gql, "variables": {"q": shopifyql}}, timeout=15,
        )
        data = (resp.json().get("data") or {}).get("shopifyqlQuery") or {}
        rows = (data.get("tableData") or {}).get("rowData") or []
        if not rows:
            # empty (e.g. token lacks read_reports, or no traffic) → show the prompt
            return {"needs_config": True}
        r = rows[0]
        sessions = int(float(r[0] or 0))
        carts = int(float(r[1] or 0))
        checkouts = int(float(r[2] or 0))
        conv = round(float(r[3] or 0) * 100, 2)
        return {
            "needs_config": False,
            "sessions": sessions, "carts": carts, "checkouts": checkouts,
            "conversion": conv,
            "cart_rate": round(100.0 * carts / sessions, 1) if sessions else 0,
            "checkout_rate": round(100.0 * checkouts / sessions, 1) if sessions else 0,
        }
    except Exception as e:
        frappe.log_error(f"Shopify storefront query failed: {e}", "ops_dashboard")
        return {"needs_config": True}
