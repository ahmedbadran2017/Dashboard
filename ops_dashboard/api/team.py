"""Team tab: per-agent leaderboards.

Confirmation is fully live — orders are assigned to an agent via
`custom_allocated_to`, so we can rank agents by orders confirmed + confirmation
rate for the period. Warehouse picking and returns handling are not attributed to
an individual on the Sales Order in the current schema, so those sections report
`needs_source: true` (wire them once a picker/handler field exists, e.g. from the
logistics portal's Pick List assignment).
"""
import frappe
from frappe.utils import flt

from ops_dashboard.api import _base as B


def _initials(name):
    parts = (name or "?").strip().split()
    return "".join(p[0] for p in parts[:2]).upper() or "?"


@frappe.whitelist()
def sections(period="today", company=None, from_date=None, to_date=None):
    B.assert_access()
    ck = f"ops_team:sections:{period}:{company or ''}:{from_date or ''}:{to_date or ''}"

    def build():
        start, end, _, _, _ = B.resolve_period(period, from_date, to_date)
        return [
            {
                "id": "conf", "metric": "confirmed",
                "members": _confirmation_leaderboard(start, end, company),
                "needs_source": False,
            },
            {"id": "wh", "metric": "picked", "members": [], "needs_source": True},
            {"id": "ret", "metric": "closed", "members": [], "needs_source": True},
        ]

    return B.cached(ck, build)


def _confirmation_leaderboard(start, end, company):
    params = {"start": str(start), "end": str(end)}
    comp = B.company_cond(company, params)
    rows = frappe.db.sql(
        f"""
        SELECT so.custom_allocated_to AS agent,
               SUM(CASE WHEN {B.IS_CONFIRMED} THEN 1 ELSE 0 END) AS confirmed,
               COUNT(*) AS total
        FROM `tabSales Order` so
        WHERE so.docstatus=1 AND so.transaction_date>=%(start)s
          AND so.transaction_date<=%(end)s AND {B.IS_REAL}
          AND IFNULL(so.custom_allocated_to,'') != ''{comp}
        GROUP BY so.custom_allocated_to
        HAVING confirmed > 0
        ORDER BY confirmed DESC LIMIT 8
        """,
        params, as_dict=True,
    )
    if not rows:
        return []
    top = flt(rows[0].confirmed) or 1
    out = []
    for i, r in enumerate(rows):
        name = frappe.db.get_value("User", r.agent, "full_name") or r.agent
        rate = round(100.0 * r.confirmed / r.total) if r.total else 0
        out.append({
            "rank": i + 1,
            "name": name,
            "initials": _initials(name),
            "value": int(r.confirmed),
            "sub": f"{rate}%",
            "pct": max(4, round(100.0 * r.confirmed / top)),
        })
    return out
