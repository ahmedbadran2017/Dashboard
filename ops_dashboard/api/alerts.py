"""Alerts tab: operational exceptions computed live against thresholds.

Each alert is only emitted when its condition actually fires, so the bell badge
count reflects real problems. Severity: red (money/SLA at risk), orange (queue
health), blue (informational). Copy/thresholds are tuned for Justyol ops.
"""
import frappe
from frappe.utils import flt

from ops_dashboard.api import _base as B
from ops_dashboard.api.kpis import _cod, _late


@frappe.whitelist()
def list_alerts(company=None):
    B.assert_access()
    out = []

    # 1. Orders stuck in dispatch > 48h (red)
    stuck = _late(company)
    if stuck:
        out.append({"key": "stuck", "severity": "red", "count": stuck,
                    "value": None, "hours_ago": 1})

    # 2. COD overdue > 7 days (red)
    cod = _cod(company)
    if cod["overdue"] > 0:
        out.append({"key": "cod_overdue", "severity": "red", "count": None,
                    "value": cod["overdue"], "hours_ago": 2})

    # 3. Pending confirmation, no first reminder, older than 4h (orange)
    params = {}
    comp = B.company_cond(company, params)
    no_call = frappe.db.sql(
        f"""SELECT COUNT(*) FROM `tabSales Order` so
            WHERE so.docstatus=1 AND {B.IS_REAL} AND NOT {B.IS_CONFIRMED}
              AND IFNULL(so.custom_first_reminder,0)=0
              AND so.creation < NOW() - INTERVAL 4 HOUR
              AND so.transaction_date >= CURDATE() - INTERVAL 2 DAY{comp}""",
        params)[0][0]
    if no_call:
        out.append({"key": "no_confirm_call", "severity": "orange",
                    "count": int(no_call), "value": None, "hours_ago": 3})

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
                    "value": rate, "hours_ago": 5})

    # 5. SKUs near stock-out (blue) — best effort from Bin actual_qty
    try:
        low = frappe.db.sql(
            """SELECT COUNT(*) FROM `tabBin`
               WHERE actual_qty > 0 AND actual_qty <= 5""")[0][0]
        if low:
            out.append({"key": "low_stock", "severity": "blue", "count": int(low),
                        "value": None, "hours_ago": 6})
    except Exception:
        pass

    return out


@frappe.whitelist()
def badge_count(company=None):
    """Just the count, for the header bell."""
    B.assert_access()
    return len(list_alerts(company=company))
