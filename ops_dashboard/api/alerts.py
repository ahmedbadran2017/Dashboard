"""Alerts tab: operational exceptions computed live against thresholds.

Each alert is only emitted when its condition actually fires, so the bell badge
count reflects real problems. Severity: red (money/SLA at risk), orange (queue
health), blue (informational). Copy/thresholds are tuned for Justyol ops.
"""
import frappe
from frappe.utils import add_to_date, flt, now_datetime

from ops_dashboard.api import _base as B
from ops_dashboard.api.kpis import _cod, _late


@frappe.whitelist()
def list_alerts(company=None):
    B.assert_access()
    # Cached briefly (busted when an order changes): the bell badge fetches this
    # on every app load, and each alert is its own aggregate scan of tabSales Order.
    return B.cached(f"ops_alerts:{company or ''}", lambda: _build_alerts(company))


def _build_alerts(company=None):
    out = []

    # 1. Orders overdue in transit (red) + the unreconciled backlog (blue).
    #    These are two different jobs and used to be one number: an order that
    #    left three days ago needs the carrier chased today, while one that left
    #    eight months ago needs its status closed out. Merged, the daily queue of
    #    about a thousand sat inside a 14,330 red alert that nobody could act on.
    late = _late(company, detail=True)
    if late["overdue"]:
        out.append({"key": "stuck", "severity": "red", "count": late["overdue"],
                    "value": None})
    if late["stale"]:
        out.append({"key": "stale_shipments", "severity": "blue",
                    "count": late["stale"], "value": None})

    # 2. COD overdue > 7 days (red)
    cod = _cod(company)
    if cod["overdue"] > 0:
        out.append({"key": "cod_overdue", "severity": "red", "count": None,
                    "value": cod["overdue"]})

    # 3. Pending confirmation, no first reminder, older than 4h (orange)
    params = {}
    comp = B.company_cond(company, params)
    params["cutoff"] = add_to_date(now_datetime(), hours=-4)
    no_call = frappe.db.sql(
        f"""SELECT COUNT(*) FROM `tabSales Order` so
            WHERE so.docstatus=1 AND {B.IS_REAL} AND NOT {B.IS_CONFIRMED}
              AND IFNULL(so.custom_first_reminder,0)=0
              AND so.creation < %(cutoff)s
              AND so.transaction_date >= CURDATE() - INTERVAL 2 DAY{comp}""",
        params)[0][0]
    if no_call:
        out.append({"key": "no_confirm_call", "severity": "orange",
                    "count": int(no_call), "value": None})

    # 4. Return rate this month (orange if > 8%)
    params = {}
    comp = B.company_cond(company, params)
    mrow = frappe.db.sql(
        f"""SELECT SUM(CASE WHEN {B.IS_RETURNED} THEN 1 ELSE 0 END) ret,
                   SUM({B.IS_REAL}) real_o
            FROM `tabSales Order` so
            WHERE so.docstatus=1 AND so.transaction_date >= MAKEDATE(YEAR(CURDATE()),1)
              AND MONTH(so.transaction_date)=MONTH(CURDATE()){comp}""",
        params, as_dict=True)[0]
    if mrow.real_o and flt(mrow.ret) / flt(mrow.real_o) * 100 > 8:
        rate = round(100.0 * flt(mrow.ret) / flt(mrow.real_o), 1)
        out.append({"key": "return_rate", "severity": "orange", "count": None,
                    "value": rate})

    # 5. SKUs near stock-out (blue) — best effort from Bin actual_qty
    try:
        low = frappe.db.sql(
            """SELECT COUNT(*) FROM `tabBin`
               WHERE actual_qty > 0 AND actual_qty <= 5""")[0][0]
        if low:
            out.append({"key": "low_stock", "severity": "blue", "count": int(low),
                        "value": None})
    except Exception:
        pass

    return out


@frappe.whitelist()
def badge_count(company=None):
    """Just the count, for the header bell."""
    B.assert_access()
    return len(list_alerts(company=company))


# ── "Needs you today" ──────────────────────────────────────────────────────
# The home screen's first block. Each item is a queue somebody can work this
# morning, with the actual orders in it — a count alone tells you there is a
# problem, the list tells you where to start. Only queues that are actionable
# TODAY belong here: the stale >30-day shipment backlog is real but it is a
# reconciliation job, so it stays on the Alerts page.
NEEDS_YOU_ROWS = 8


def _rows(sql, params):
    try:
        return frappe.db.sql(sql, params, as_dict=True)
    except Exception:
        frappe.log_error(title="ops needs_you query failed",
                         message=frappe.get_traceback()[:1500])
        return []


@frappe.whitelist()
def needs_you(company=None):
    B.assert_access()
    return B.cached(f"ops_alerts:needs:{company or ''}", lambda: _build_needs_you(company))


def _build_needs_you(company=None):
    from ops_dashboard.api.kpis import LATE_AFTER_DAYS, STALE_AFTER_DAYS
    out = []
    # Site-time "now". The DB clock is UTC while creation timestamps are written
    # in site time (Istanbul), so NOW() inside SQL is three hours off.
    now = now_datetime()

    # 1. Overdue with the courier — left the warehouse (Delivery Note) more than
    #    the 2-3 day promise ago, still not delivered, and recent enough to chase.
    p = {"late": LATE_AFTER_DAYS, "stale": STALE_AFTER_DAYS}
    comp = B.company_cond(company, p)
    rows = _rows(f"""
        SELECT so.name, so.customer_name AS customer, so.custom_shipping_city AS city,
               so.grand_total AS value, so.custom_track_shipment_status AS carrier_status,
               DATEDIFF(CURDATE(), MIN(dn.posting_date)) AS days
        FROM `tabSales Order` so
        JOIN `tabDelivery Note Item` dni ON dni.against_sales_order = so.name
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent AND dn.docstatus = 1
        WHERE so.docstatus = 1 AND {B.IS_REAL}
          AND {B.IS_DISPATCHED} AND NOT {B.IS_DELIVERED} AND NOT {B.IS_RETURNED}{comp}
        GROUP BY so.name
        HAVING days > %(late)s AND days <= %(stale)s
        -- Where to start: parcels the carrier itself has flagged come first —
        -- an exception is a call that resolves today — then the oldest.
        ORDER BY (carrier_status = 'Delivery Exception') DESC, days DESC
    """, p)
    if rows:
        out.append({"key": "overdue_courier", "severity": "red", "count": len(rows),
                    "value": sum(flt(r.value) for r in rows),
                    "rows": [_row(r, unit="days") for r in rows[:NEEDS_YOU_ROWS]]})

    # 2. Delivered but unpaid past the carrier's 7-day settlement. Same
    #    "collected" definition as the COD card (ref on the order OR its invoice).
    p = {}
    comp = B.company_cond(company, p)
    inv_join = (
        "LEFT JOIN (SELECT sii.sales_order so "
        "FROM `tabSales Invoice Item` sii JOIN `tabSales Invoice` si ON si.name = sii.parent "
        f"WHERE si.docstatus < 2 AND {B.ref_present('si.custom_reference_number')} "
        "AND IFNULL(sii.sales_order,'') != '' GROUP BY sii.sales_order) inv ON inv.so = so.name"
    )
    rows = _rows(f"""
        SELECT so.name, so.customer_name AS customer, so.custom_shipping_city AS city,
               so.grand_total AS value, DATEDIFF(CURDATE(), so.transaction_date) AS days
        FROM `tabSales Order` so {inv_join}
        WHERE so.docstatus = 1 AND {B.IS_REAL} AND {B.IS_DELIVERED}
          AND {B.ref_absent('so.custom_reference_number')} AND inv.so IS NULL
          AND DATEDIFF(CURDATE(), so.transaction_date) > 7
          AND so.transaction_date >= MAKEDATE(YEAR(CURDATE()), 1){comp}
        ORDER BY so.grand_total DESC
    """, p)
    if rows:
        out.append({"key": "cod_overdue", "severity": "red", "count": len(rows),
                    "value": sum(flt(r.value) for r in rows),
                    "rows": [_row(r, unit="days") for r in rows[:NEEDS_YOU_ROWS]]})

    # 3. New orders nobody has called yet — the confirmation queue. Oldest first.
    p = {"cutoff": add_to_date(now, hours=-4), "now": now}
    comp = B.company_cond(company, p)
    rows = _rows(f"""
        SELECT so.name, so.customer_name AS customer, so.custom_shipping_city AS city,
               so.grand_total AS value,
               TIMESTAMPDIFF(HOUR, so.creation, %(now)s) AS hours
        FROM `tabSales Order` so
        WHERE so.docstatus = 1 AND {B.IS_REAL} AND NOT {B.IS_CONFIRMED}
          AND IFNULL(so.custom_first_reminder, 0) = 0
          AND so.creation < %(cutoff)s
          AND so.transaction_date >= CURDATE() - INTERVAL 2 DAY{comp}
        ORDER BY so.creation ASC
    """, p)
    if rows:
        out.append({"key": "not_contacted", "severity": "orange", "count": len(rows),
                    "value": sum(flt(r.value) for r in rows),
                    "rows": [_row(r, unit="hours") for r in rows[:NEEDS_YOU_ROWS]]})

    return out


def _row(r, unit):
    age = r.get("days") if unit == "days" else r.get("hours")
    return {"name": r.name, "customer": (r.customer or "").strip(),
            "city": (r.city or "").strip(), "value": flt(r.value),
            "age": int(age or 0), "age_unit": unit,
            "carrier_status": r.get("carrier_status") or ""}
