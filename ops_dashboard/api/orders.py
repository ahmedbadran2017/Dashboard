"""Orders tab: filterable list + per-status counts + order detail sheet.

The five UI statuses (new → confirmed → dispatched → delivered, plus returned)
are derived from the same pipeline predicates as the funnel, so the chip counts
tie out to the Home funnel exactly.
"""
import frappe
from frappe.utils import flt

from ops_dashboard.api import _base as B

# Priority-ordered derivation → one canonical UI status per order.
UI_STATUS_CASE = f"""
  CASE
    WHEN {B.IS_RETURNED} THEN 'ret'
    WHEN {B.IS_DELIVERED} THEN 'del'
    WHEN {B.IS_DISPATCHED} THEN 'disp'
    WHEN {B.IS_CONFIRMED} THEN 'conf'
    ELSE 'new'
  END
"""

_COND = {
    "new": f"NOT {B.IS_RETURNED} AND NOT {B.IS_DELIVERED} AND NOT {B.IS_DISPATCHED} AND NOT {B.IS_CONFIRMED}",
    "conf": f"{B.IS_CONFIRMED} AND NOT {B.IS_DISPATCHED} AND NOT {B.IS_DELIVERED} AND NOT {B.IS_RETURNED}",
    "disp": f"{B.IS_DISPATCHED} AND NOT {B.IS_DELIVERED} AND NOT {B.IS_RETURNED}",
    "del": f"{B.IS_DELIVERED} AND NOT {B.IS_RETURNED}",
    "ret": B.IS_RETURNED,
}


@frappe.whitelist()
def counts(period="today", company=None, from_date=None, to_date=None, source=None):
    """Per-status chip counts for the period (All + the five statuses)."""
    B.assert_access()
    start, end, _, _, _ = B.resolve_period(period, from_date, to_date)
    params = {}
    where = B.base_where(start, end, company, params) + B.source_cond(source, params)
    row = frappe.db.sql(
        f"""
        SELECT
          COUNT(*) AS total,
          SUM(CASE WHEN {_COND['new']} THEN 1 ELSE 0 END)  AS c_new,
          SUM(CASE WHEN {_COND['conf']} THEN 1 ELSE 0 END) AS c_conf,
          SUM(CASE WHEN {_COND['disp']} THEN 1 ELSE 0 END) AS c_disp,
          SUM(CASE WHEN {_COND['del']} THEN 1 ELSE 0 END)  AS c_del,
          SUM(CASE WHEN {_COND['ret']} THEN 1 ELSE 0 END)  AS c_ret
        FROM `tabSales Order` so WHERE {where}
        """,
        params, as_dict=True,
    )[0]
    return {
        "all": int(row.total or 0), "new": int(row.c_new or 0),
        "conf": int(row.c_conf or 0), "disp": int(row.c_disp or 0),
        "del": int(row.c_del or 0), "ret": int(row.c_ret or 0),
    }


@frappe.whitelist()
def list_orders(period="today", status="all", city=None, search=None,
                company=None, from_date=None, to_date=None, limit=100, source=None):
    """Orders in the period, filtered by status / source / city / search — newest first."""
    B.assert_access()
    start, end, _, _, _ = B.resolve_period(period, from_date, to_date)
    params = {"limit": min(int(limit or 100), 500)}
    conds = [B.base_where(start, end, company, params)]
    src = B.source_cond(source, params)
    if src:
        conds.append(src.replace(" AND ", "", 1))
    if status and status != "all" and status in _COND:
        conds.append("(" + _COND[status] + ")")
    if city and city != "all":
        conds.append("so.custom_shipping_city = %(city)s")
        params["city"] = city
    if search:
        conds.append("(so.name LIKE %(s)s OR so.customer_name LIKE %(s)s OR so.customer LIKE %(s)s)")
        params["s"] = f"%{search}%"
    where = " AND ".join(conds)
    rows = frappe.db.sql(
        f"""
        SELECT so.name AS id,
               COALESCE(NULLIF(so.customer_name,''), so.customer) AS customer,
               IFNULL(so.custom_shipping_city,'') AS city,
               ROUND(so.grand_total) AS amount,
               DATE_FORMAT(so.creation, '%%H:%%i') AS time,
               so.transaction_date AS date,
               {B.SOURCE_CASE} AS source,
               {UI_STATUS_CASE} AS status
        FROM `tabSales Order` so WHERE {where}
        ORDER BY so.creation DESC LIMIT %(limit)s
        """,
        params, as_dict=True,
    )
    for r in rows:
        r["amount"] = flt(r["amount"])
    return rows


@frappe.whitelist()
def cities(period="today", company=None, from_date=None, to_date=None, limit=12):
    """Top shipping cities in the period, for the city filter chips."""
    B.assert_access()
    start, end, _, _, _ = B.resolve_period(period, from_date, to_date)
    params = {"limit": min(int(limit or 12), 40)}
    where = B.base_where(start, end, company, params)
    rows = frappe.db.sql(
        f"""
        SELECT so.custom_shipping_city AS city, COUNT(*) AS n
        FROM `tabSales Order` so
        WHERE {where} AND IFNULL(so.custom_shipping_city,'') != ''
        GROUP BY so.custom_shipping_city ORDER BY n DESC LIMIT %(limit)s
        """,
        params, as_dict=True,
    )
    return [r.city for r in rows]


@frappe.whitelist()
def get_order(name=None):
    """Detail sheet: header, info tiles, and the 4-step delivery timeline."""
    B.assert_access()
    if not name or not frappe.db.exists("Sales Order", name):
        return None
    so = frappe.db.get_value(
        "Sales Order", name,
        ["name", "customer", "customer_name", "grand_total", "custom_shipping_city",
         "custom_shipping_phone", "custom_customer_phone", "custom_items_count",
         "custom_tracking_company", "custom_tracking_url", "custom_sales_status",
         "custom_logistics_status", "custom_track_shipment_status",
         "custom_first_reminder", "custom_second_reminder",
         "creation", "custom_shipped_at", "custom_delivered_at"],
        as_dict=True,
    )
    # derive UI status
    status = frappe.db.sql(
        f"SELECT {UI_STATUS_CASE} FROM `tabSales Order` so WHERE so.name=%s", name)[0][0]
    step_done = {"new": 1, "conf": 2, "disp": 3, "del": 4, "ret": 3}.get(status, 1)
    attempts = 1 + int(so.get("custom_first_reminder") or 0) + int(so.get("custom_second_reminder") or 0)
    return {
        "id": so.name,
        "customer": so.customer_name or so.customer,
        "city": so.custom_shipping_city or "",
        "phone": so.custom_shipping_phone or so.custom_customer_phone or "",
        "amount": flt(so.grand_total),
        "status": status,
        "items_count": int(so.custom_items_count or 0),
        "courier": so.custom_tracking_company or "—",
        "tracking_url": so.custom_tracking_url or "",
        "attempts": attempts,
        "step_done": step_done,
        "shipped_at": str(so.custom_shipped_at or ""),
        "delivered_at": str(so.custom_delivered_at or ""),
        "created_at": str(so.creation or ""),
    }
