"""Departments tab: 7 operational departments with live headline KPIs + a detail
view (2×2 stats, 7-day trend, top performers).

Each department reads from the same Sales Order pipeline. Targets are ops-defined
(config below) — edit TARGETS to retune, or move them to a Settings doctype later.
"""
import frappe
from frappe.utils import flt

from ops_dashboard.api import _base as B
from ops_dashboard.api.kpis import _agg, _cod, _rate, _week_bars

# Daily targets per department (edit to retune; label is shown under the bar).
TARGETS = {
    "conf": {"pct_of": "confirmation", "target": 85, "unit": "%"},
    "wh": {"target": 120, "unit": "orders"},
    "disp": {"target": 130, "unit": "orders"},
    "del": {"pct_of": "delivery", "target": 80, "unit": "%"},
    "ret": {"target": 8, "unit": "%", "lower_is_better": True},
    "cod": {"target": 48, "unit": "h"},
    "mkt": {"target": 35000, "unit": "MAD"},
}

ORDER = ["conf", "wh", "disp", "del", "ret", "cod", "mkt"]


def _clip(pct):
    return max(0, min(100, round(pct)))


@frappe.whitelist()
def list_departments(period="today", company=None, from_date=None, to_date=None):
    B.assert_access()
    ck = f"ops_dept:list:{period}:{company or ''}:{from_date or ''}:{to_date or ''}"

    def build():
        start, end, ps, pe, _ = B.resolve_period(period, from_date, to_date)
        cur = _agg(start, end, company)
        prev = _agg(ps, pe, company)
        cod = _cod(company)
        late = _late_count(company)

        conf = _rate(cur["confirmed"], cur["real_orders"])
        conf_prev = _rate(prev["confirmed"], prev["real_orders"])
        deliv = _rate(cur["delivered"], cur["dispatched"])
        deliv_prev = _rate(prev["delivered"], prev["dispatched"])
        ret = _rate(cur["returned"], cur["real_orders"])
        ret_prev = _rate(prev["returned"], prev["real_orders"])
        aov = round(cur["value"] / cur["orders"]) if cur["orders"] else 0

        d = {
            "conf": {
                "kpi": conf, "kpi_unit": "%",
                "count": int(cur["confirmed"]), "total": int(cur["real_orders"]),
                "trend": round(conf - conf_prev, 1),
                "target_pct": _clip(conf / 85 * 100), "on_track": conf >= 85,
            },
            "wh": {
                "kpi": int(cur["dispatched"]), "kpi_unit": "",
                "trend": int(cur["dispatched"] - prev["dispatched"]),
                "target_pct": _clip(cur["dispatched"] / 120 * 100), "on_track": cur["dispatched"] >= 120,
            },
            "disp": {
                "kpi": int(cur["dispatched"]), "kpi_unit": "", "stuck": late,
                "trend": int(cur["dispatched"] - prev["dispatched"]),
                "target_pct": _clip(cur["dispatched"] / 130 * 100), "on_track": late < 10,
            },
            "del": {
                "kpi": deliv, "kpi_unit": "%", "count": int(cur["delivered"]),
                "trend": round(deliv - deliv_prev, 1),
                "target_pct": _clip(deliv / 80 * 100), "on_track": deliv >= 80,
            },
            "ret": {
                "kpi": ret, "kpi_unit": "%", "count": int(cur["returned"]),
                "trend": round(ret - ret_prev, 1),
                "target_pct": _clip(ret / 8 * 100), "on_track": ret <= 8,
            },
            "cod": {
                "kpi": cod["pending"], "kpi_unit": "MAD", "overdue": cod["overdue"],
                "trend": 0, "target_pct": 55, "on_track": False,
            },
            "mkt": {
                "kpi": cur["value"], "kpi_unit": "MAD", "aov": aov,
                "trend": round(100.0 * (cur["value"] - prev["value"]) / prev["value"], 1) if prev["value"] else 0,
                "target_pct": _clip(cur["value"] / 35000 * 100), "on_track": cur["value"] >= 35000,
            },
        }
        return [dict(id=k, **d[k]) for k in ORDER]

    return B.cached(ck, build)


def _late_count(company):
    from ops_dashboard.api.kpis import _late
    return _late(company)


@frappe.whitelist()
def department_detail(dept="conf", period="today", company=None, from_date=None, to_date=None):
    """2×2 stats + 7-day trend + top performers for one department."""
    B.assert_access()
    start, end, ps, pe, _ = B.resolve_period(period, from_date, to_date)
    cur = _agg(start, end, company)
    prev = _agg(ps, pe, company)

    bars = _dept_bars(dept, company)
    top = _dept_top(dept, start, end, company)

    conf = _rate(cur["confirmed"], cur["real_orders"])
    deliv = _rate(cur["delivered"], cur["dispatched"])
    ret = _rate(cur["returned"], cur["real_orders"])

    stats_map = {
        "conf": [
            {"l": "confirmed_today", "v": int(cur["confirmed"]), "d": int(cur["confirmed"] - prev["confirmed"])},
            {"l": "awaiting", "v": int(cur["real_orders"] - cur["confirmed"]), "d": None},
            {"l": "rate", "v": conf, "unit": "%", "d": None},
            {"l": "total", "v": int(cur["real_orders"]), "d": int(cur["real_orders"] - prev["real_orders"])},
        ],
        "del": [
            {"l": "delivered_today", "v": int(cur["delivered"]), "d": int(cur["delivered"] - prev["delivered"])},
            {"l": "dispatched", "v": int(cur["dispatched"]), "d": None},
            {"l": "rate", "v": deliv, "unit": "%", "d": None},
            {"l": "returned", "v": int(cur["returned"]), "d": None},
        ],
        "ret": [
            {"l": "returned", "v": int(cur["returned"]), "d": int(cur["returned"] - prev["returned"])},
            {"l": "rate", "v": ret, "unit": "%", "d": None},
            {"l": "delivered", "v": int(cur["delivered"]), "d": None},
            {"l": "total", "v": int(cur["real_orders"]), "d": None},
        ],
    }
    stats = stats_map.get(dept, [
        {"l": "orders", "v": int(cur["orders"]), "d": int(cur["orders"] - prev["orders"])},
        {"l": "confirmed", "v": int(cur["confirmed"]), "d": None},
        {"l": "dispatched", "v": int(cur["dispatched"]), "d": None},
        {"l": "delivered", "v": int(cur["delivered"]), "d": None},
    ])
    return {"id": dept, "stats": stats, "bars": bars, "top": top}


def _dept_bars(dept, company):
    """7-day trend for the department's headline metric."""
    if dept == "mkt":
        params = {}
        comp = B.company_cond(company, params)
        rows = frappe.db.sql(
            f"""SELECT so.transaction_date d, ROUND(SUM(so.grand_total)) n
                FROM `tabSales Order` so
                WHERE so.docstatus=1 AND so.transaction_date >= CURDATE()-INTERVAL 6 DAY
                  AND so.transaction_date <= CURDATE(){comp}
                GROUP BY so.transaction_date""", params, as_dict=True)
    else:
        metric = {
            "conf": B.IS_CONFIRMED, "del": B.IS_DELIVERED, "ret": B.IS_RETURNED,
        }.get(dept, B.IS_DISPATCHED)
        params = {}
        comp = B.company_cond(company, params)
        rows = frappe.db.sql(
            f"""SELECT so.transaction_date d,
                       SUM(CASE WHEN {metric} THEN 1 ELSE 0 END) n
                FROM `tabSales Order` so
                WHERE so.docstatus=1 AND so.transaction_date >= CURDATE()-INTERVAL 6 DAY
                  AND so.transaction_date <= CURDATE(){comp}
                GROUP BY so.transaction_date""", params, as_dict=True)
    by_day = {str(r.d): flt(r.n) for r in rows}
    from frappe.utils import add_days, getdate, nowdate
    return [{"date": str(getdate(add_days(getdate(nowdate()), -i))),
             "count": by_day.get(str(getdate(add_days(getdate(nowdate()), -i))), 0)}
            for i in range(6, -1, -1)]


def _dept_top(dept, start, end, company):
    """Top performers. Confirmation is by the assigned agent (custom_allocated_to);
    delivery is by city; others fall back to city breakdown."""
    params = {"start": str(start), "end": str(end)}
    comp = B.company_cond(company, params)
    if dept == "conf":
        rows = frappe.db.sql(
            f"""SELECT IFNULL(NULLIF(so.custom_allocated_to,''),'—') k,
                       SUM(CASE WHEN {B.IS_CONFIRMED} THEN 1 ELSE 0 END) v, COUNT(*) t
                FROM `tabSales Order` so
                WHERE so.docstatus=1 AND so.transaction_date>=%(start)s
                  AND so.transaction_date<=%(end)s AND {B.IS_REAL}
                  AND IFNULL(so.custom_allocated_to,'') != ''{comp}
                GROUP BY so.custom_allocated_to ORDER BY v DESC LIMIT 3""",
            params, as_dict=True)
        out = []
        for r in rows:
            name = frappe.db.get_value("User", r.k, "full_name") or r.k
            out.append({"name": name, "value": int(r.v),
                        "pct": _clip(100.0 * r.v / r.t) if r.t else 0})
        return out
    # city-based for delivery / others
    rows = frappe.db.sql(
        f"""SELECT IFNULL(NULLIF(so.custom_shipping_city,''),'—') k, COUNT(*) v
            FROM `tabSales Order` so
            WHERE so.docstatus=1 AND so.transaction_date>=%(start)s
              AND so.transaction_date<=%(end)s AND {B.IS_REAL}{comp}
            GROUP BY so.custom_shipping_city ORDER BY v DESC LIMIT 3""",
        params, as_dict=True)
    mx = max([r.v for r in rows], default=1) or 1
    return [{"name": r.k, "value": int(r.v), "pct": _clip(100.0 * r.v / mx)} for r in rows]
