"""Home screen: the live KPI rollup for a period.

One whitelisted call (`home`) returns everything the Home tab renders: the hero
order count + sales value with deltas, the 7-day bar sparkline, the order funnel,
the four rate cards, the COD collection split, and the late/stuck strip. All from
live `tabSales Order` data via the shared pipeline predicates in _base.py.
"""
import frappe
from frappe.utils import flt, get_datetime, now_datetime

from ops_dashboard.api import _base as B


def _agg(start, end, company):
    """Count, value, and each pipeline stage for one date window — one pass."""
    params = {}
    where = B.base_where(start, end, company, params)
    row = frappe.db.sql(
        f"""
        SELECT
          COUNT(*)                                                     AS orders,
          -- sales value counts only REAL demand (excludes Cancelled/Duplicated),
          -- so it agrees with the rate denominators and AOV below
          ROUND(SUM(CASE WHEN {B.IS_REAL} THEN so.grand_total ELSE 0 END)) AS value,
          SUM({B.IS_REAL})                                             AS real_orders,
          SUM(CASE WHEN {B.IS_CONFIRMED} THEN 1 ELSE 0 END)            AS confirmed,
          SUM(CASE WHEN {B.IS_DISPATCHED} THEN 1 ELSE 0 END)           AS dispatched,
          SUM(CASE WHEN {B.IS_DELIVERED} THEN 1 ELSE 0 END)            AS delivered,
          SUM(CASE WHEN {B.IS_RETURNED} THEN 1 ELSE 0 END)             AS returned
        FROM `tabSales Order` so
        WHERE {where}
        """,
        params, as_dict=True,
    )[0]
    for k in row:
        row[k] = flt(row[k])
    return row


def _rate(num, den):
    return round(100.0 * num / den, 1) if den else 0.0


def _week_bars(company):
    """Daily order counts for the trailing 7 days (today last)."""
    params = {}
    cond = B.company_cond(company, params)
    rows = frappe.db.sql(
        f"""
        SELECT so.transaction_date AS d, COUNT(*) AS n
        FROM `tabSales Order` so
        WHERE so.docstatus = 1
          AND so.transaction_date >= CURDATE() - INTERVAL 6 DAY
          AND so.transaction_date <= CURDATE(){cond}
        GROUP BY so.transaction_date
        """,
        params, as_dict=True,
    )
    by_day = {str(r.d): int(r.n) for r in rows}
    from frappe.utils import add_days, getdate, nowdate
    out = []
    for i in range(6, -1, -1):
        day = str(getdate(add_days(getdate(nowdate()), -i)))
        out.append({"date": day, "count": by_day.get(day, 0)})
    return out


def _cod(company):
    """Collected (carrier remitted) vs pending at courier (delivered, not yet
    collected), current fiscal year. Ported from accounting_portal/api/cod.py.

    "Collected" = a carrier remittance ref (CATH…/RDF…) is present on the Sales
    Order OR on its Sales Invoice. The invoice side is essential: the book's
    matching process stamps the INVOICE (tens of thousands of orders), while the
    portal's reconcile stamps the order — counting only the order ref (the
    original port) undercounts collected and inflates pending. docstatus<2 on the
    invoice: a ref stamped on a still-draft invoice already means collected."""
    params = {}
    comp = B.company_cond(company, params)
    # Orders whose collecting ref lives on their Sales Invoice.
    inv_join = (
        "LEFT JOIN (SELECT sii.sales_order so "
        "FROM `tabSales Invoice Item` sii JOIN `tabSales Invoice` si ON si.name = sii.parent "
        f"WHERE si.docstatus < 2 AND {B.ref_present('si.custom_reference_number')} "
        "AND IFNULL(sii.sales_order,'') != '' GROUP BY sii.sales_order) inv ON inv.so = so.name"
    )
    collected = "(" + B.ref_present("so.custom_reference_number") + " OR inv.so IS NOT NULL)"
    notcoll = "(" + B.ref_absent("so.custom_reference_number") + " AND inv.so IS NULL)"
    row = frappe.db.sql(
        f"""
        SELECT
          ROUND(SUM(CASE WHEN {collected} THEN so.grand_total ELSE 0 END))       AS collected,
          ROUND(SUM(CASE WHEN {notcoll} AND {B.IS_DELIVERED}
                         THEN so.grand_total ELSE 0 END))                        AS pending,
          ROUND(SUM(CASE WHEN {notcoll} AND {B.IS_DELIVERED}
                          AND DATEDIFF(CURDATE(), so.transaction_date) > 7
                         THEN so.grand_total ELSE 0 END))                        AS overdue
        FROM `tabSales Order` so {inv_join}
        WHERE so.docstatus = 1 AND {B.IS_REAL}
          AND so.transaction_date >= MAKEDATE(YEAR(CURDATE()), 1){comp}
        """,
        params, as_dict=True,
    )[0]
    return {k: flt(v) for k, v in row.items()}


def _late(company):
    """Dispatched but not delivered, and moving for > 48h. The 'stuck' count."""
    params = {}
    comp = B.company_cond(company, params)
    n = frappe.db.sql(
        f"""
        SELECT COUNT(*) FROM `tabSales Order` so
        WHERE so.docstatus = 1 AND {B.IS_REAL}
          AND {B.IS_DISPATCHED} AND NOT {B.IS_DELIVERED} AND NOT {B.IS_RETURNED}
          AND COALESCE(so.custom_shipped_at, so.modified) < NOW() - INTERVAL 48 HOUR{comp}
        """,
        params,
    )[0][0]
    return int(n or 0)


def _forecast(count_today):
    """Project end-of-day volume from the current hourly rate over a 12h business
    day (09:00–21:00). Only meaningful for the 'today' period."""
    now = now_datetime()
    open_h, close_h = 9, 21
    elapsed = max(0.5, (now.hour + now.minute / 60.0) - open_h)
    elapsed = min(elapsed, close_h - open_h)
    if elapsed <= 0:
        return count_today
    rate = count_today / elapsed
    return int(round(rate * (close_h - open_h)))


@frappe.whitelist()
def sources(period="today", company=None, from_date=None, to_date=None):
    """Per-channel breakdown for the period: count, value, share of orders, and
    the QUALITY signals — confirmation rate and return rate — so each channel's
    lead quality is visible next to its volume."""
    B.assert_access()
    ck = f"ops_kpi:sources:{period}:{company or ''}:{from_date or ''}:{to_date or ''}"

    def build():
        start, end, _, _, _ = B.resolve_period(period, from_date, to_date)
        params = {}
        where = B.base_where(start, end, company, params)
        rows = frappe.db.sql(
            f"""
            SELECT {B.SOURCE_CASE} AS source,
                   COUNT(*) AS orders,
                   ROUND(SUM(so.grand_total)) AS value,
                   SUM({B.IS_REAL}) AS real_orders,
                   SUM(CASE WHEN {B.IS_CONFIRMED} THEN 1 ELSE 0 END) AS confirmed,
                   SUM(CASE WHEN {B.IS_RETURNED} THEN 1 ELSE 0 END) AS returned
            FROM `tabSales Order` so
            WHERE {where}
            GROUP BY source ORDER BY orders DESC
            """,
            params, as_dict=True,
        )
        total = sum(int(r.orders) for r in rows) or 1
        out = []
        for r in rows:
            out.append({
                "id": r.source,
                "orders": int(r.orders),
                "value": flt(r.value),
                "share": round(100.0 * r.orders / total, 1),
                "conf_rate": _rate(flt(r.confirmed), flt(r.real_orders)),
                "ret_rate": _rate(flt(r.returned), flt(r.real_orders)),
            })
        return out

    return B.cached(ck, build)


@frappe.whitelist()
def home(period="today", company=None, from_date=None, to_date=None):
    B.assert_access()
    ck = f"ops_kpi:home:{period}:{company or ''}:{from_date or ''}:{to_date or ''}"

    def build():
        start, end, ps, pe, _ = B.resolve_period(period, from_date, to_date)
        cur = _agg(start, end, company)
        prev = _agg(ps, pe, company)

        conf = _rate(cur["confirmed"], cur["real_orders"])
        conf_prev = _rate(prev["confirmed"], prev["real_orders"])
        deliv = _rate(cur["delivered"], cur["dispatched"])
        deliv_prev = _rate(prev["delivered"], prev["dispatched"])
        ret = _rate(cur["returned"], cur["real_orders"])
        ret_prev = _rate(prev["returned"], prev["real_orders"])
        # AOV over real orders, matching the real-only sales value
        aov = round(cur["value"] / cur["real_orders"]) if cur["real_orders"] else 0
        aov_prev = round(prev["value"] / prev["real_orders"]) if prev["real_orders"] else 0

        def delta(a, b):
            return round(a - b, 1)

        def pct_delta(a, b):
            return round(100.0 * (a - b) / b, 1) if b else 0.0

        cod = _cod(company)
        return {
            "period": period,
            "currency": "MAD",
            "orders": int(cur["orders"]),
            "orders_delta_pct": pct_delta(cur["orders"], prev["orders"]),
            "value": cur["value"],
            "value_delta_pct": pct_delta(cur["value"], prev["value"]),
            "funnel": {
                "new": int(cur["orders"]),
                "confirmed": int(cur["confirmed"]),
                "dispatched": int(cur["dispatched"]),
                "delivered": int(cur["delivered"]),
            },
            "rates": {
                "confirmation": {"value": conf, "delta": delta(conf, conf_prev)},
                "delivery": {"value": deliv, "delta": delta(deliv, deliv_prev)},
                "aov": {"value": aov, "delta": delta(aov, aov_prev)},
                "returns": {"value": ret, "delta": delta(ret, ret_prev)},
            },
            "cod": cod,
            "late": _late(company),
            "week": _week_bars(company),
            "forecast": _forecast(int(cur["orders"])) if period == "today" else None,
        }

    return B.cached(ck, build)
