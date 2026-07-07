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


def _overview():
    """The accounting portal's authoritative multi-company finance overview
    (per-company cash_bank / receivable / payable / income_ytd / expense_ytd /
    net_ytd + consolidated totals). It already handles the multi-company,
    multi-currency, intercompany and overdraft/FX complexity that raw GL
    aggregation gets wrong — so we reuse it rather than re-derive. Returns None
    when the accounting portal isn't installed (dev/standalone)."""
    def build():
        try:
            if "accounting_portal" in frappe.get_installed_apps():
                ov = frappe.get_attr("accounting_portal.api.dashboard.get_overview")()
                if isinstance(ov, dict) and ov.get("companies"):
                    return ov
        except Exception:
            pass
        return None
    return B.cached("ops_kpi:overview", build)


def _supplier_payable():
    """Open supplier obligation = unbilled value of submitted POs."""
    v = frappe.db.sql(
        """SELECT ROUND(SUM(grand_total * (100 - IFNULL(per_billed, 0)) / 100))
           FROM `tabPurchase Order`
           WHERE docstatus = 1 AND status IN ('To Bill', 'To Receive and Bill')"""
    )[0][0]
    return flt(v)


@frappe.whitelist()
def cash(company=None):
    """Cash position, sourced from the accounting portal's overview (authoritative):
    net cash & bank per company + consolidated. On this book the operating banks
    net NEGATIVE (overdrafts / intercompany / FX), which raw positive-only summing
    hid — so we surface the real figures. Falls back to a positive-bank sum when
    the accounting portal isn't present."""
    B.assert_access()
    ov = _overview()
    if ov:
        comps = ov.get("companies") or []
        tot = ov.get("totals") or {}
        op = next((c for c in comps if c.get("company") == OPERATING_COMPANY), comps[0] if comps else {})
        return {
            "source": "accounting_portal",
            "currency": op.get("currency", "MAD"),
            "cash_bank": flt(op.get("cash_bank")),
            "total_cash_bank": flt(tot.get("cash_bank")),
            "receivable": flt(op.get("receivable")),
            "payable": flt(op.get("payable")),
            "operating": op.get("company"),
            "companies": [
                {"company": c.get("company"), "currency": c.get("currency"),
                 "cash_bank": flt(c.get("cash_bank")), "net_ytd": flt(c.get("net_ytd"))}
                for c in comps
            ],
        }
    # Fallback (no accounting portal): positive bank balances only.
    def build():
        rows = frappe.db.sql(
            """
            SELECT a.account_name AS name, ROUND(SUM(g.debit - g.credit)) AS bal
            FROM `tabGL Entry` g JOIN `tabAccount` a ON a.name = g.account
            WHERE a.account_type = 'Bank' AND g.is_cancelled = 0
            GROUP BY a.account_name HAVING bal > 1000 ORDER BY bal DESC LIMIT 10
            """, as_dict=True)
        for r in rows:
            r["bal"] = flt(r["bal"])
        return {"source": "fallback", "currency": "MAD",
                "cash_bank": sum(r["bal"] for r in rows), "total_cash_bank": sum(r["bal"] for r in rows),
                "accounts": rows[:8]}
    return B.cached("ops_kpi:cash", build)


@frappe.whitelist()
def profit(company=None):
    """Profitability from the accounting portal overview — YEAR-TO-DATE for the
    operating company (revenue, expenses, net, net margin) + open supplier
    payables. YTD (not intraday GL) because invoice posting lags; the live today
    revenue signal stays the Sales-Order value on Home."""
    B.assert_access()
    ov = _overview()
    if ov:
        comps = ov.get("companies") or []
        op = next((c for c in comps if c.get("company") == OPERATING_COMPANY), comps[0] if comps else {})
        rev = flt(op.get("income_ytd"))
        exp = flt(op.get("expense_ytd"))
        net = flt(op.get("net_ytd"))
        return {
            "source": "accounting_portal", "company": op.get("company"), "window": "ytd",
            "currency": op.get("currency", "MAD"),
            "revenue": rev, "expenses": exp, "net": net,
            "margin": round(100.0 * net / rev, 1) if rev else 0,
            "receivable": flt(op.get("receivable")), "payable": flt(op.get("payable")),
            "supplier_payable": _supplier_payable(),
        }
    # Fallback: trailing-30d GL P&L for the operating company.
    def build():
        rows = frappe.db.sql(
            """SELECT a.root_type AS rt,
                      ROUND(SUM(CASE WHEN a.root_type='Income' THEN g.credit-g.debit
                                     ELSE g.debit-g.credit END)) AS amt
               FROM `tabGL Entry` g JOIN `tabAccount` a ON a.name=g.account
               WHERE g.is_cancelled=0 AND g.company=%(c)s AND a.root_type IN ('Income','Expense')
                 AND g.posting_date >= CURDATE()-INTERVAL 30 DAY GROUP BY a.root_type""",
            {"c": OPERATING_COMPANY}, as_dict=True)
        rev = sum(flt(r["amt"]) for r in rows if r["rt"] == "Income")
        exp = sum(flt(r["amt"]) for r in rows if r["rt"] == "Expense")
        return {"source": "fallback", "company": OPERATING_COMPANY, "window": "30d", "currency": "MAD",
                "revenue": rev, "expenses": exp, "net": rev - exp,
                "margin": round(100.0 * (rev - exp) / rev, 1) if rev else 0,
                "supplier_payable": _supplier_payable()}
    return B.cached("ops_kpi:profit", build)


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
