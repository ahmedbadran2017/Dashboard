"""Shared query fragments + helpers for the Ops Dashboard.

Every KPI on the dashboard is derived from `tabSales Order` and a few related
doctypes, using the SAME custom-field pipeline the other Justyol portals rely on.
This module is the single source of truth for:

  • period → date-range resolution (today / 7d / 30d, and the matching "previous"
    window for deltas)
  • the pipeline-stage SQL predicates (new → confirmed → dispatched → delivered,
    plus returned) so the funnel, rate cards and departments all agree
  • the COD "collected vs pending at courier" definition (a carrier remittance
    reference is present — CATH… / RDF…), ported from the accounting portal
  • a small rollup cache (short TTL, busted when a Sales Order changes)

Grounded in the live schema (verified 2026-07): the operational status lives in
custom fields, NOT the stock ERPNext `status` column:
  custom_sales_status      Confirmed / Did not Answer / Cancelled / Pending / …
  custom_logistics_status  Pending / Delivered / Returned / Shipped / Label …
  custom_track_shipment_status  carrier-side status (Delivered / In Transit / …)
  custom_shipping_city, custom_allocated_to, custom_*_at timestamps
"""
import frappe
from frappe.utils import add_days, flt, getdate, nowdate

# ── Pipeline vocabulary ──────────────────────────────────────────
CONFIRMED = "'Confirmed'"
# Cancelled/duplicated orders never entered the real funnel — exclude them from
# rates so the denominator is "real demand", matching the accounting portal.
DEAD_SALES = "('Cancelled','Duplicated')"
DELIVERED_LOG = "'Delivered'"
RETURNED_LOG = "'Returned'"
# "Dispatched" = physically left the warehouse. A shipped timestamp is the
# cleanest signal; fall back to any logistics status beyond Pending.
SHIPPED_LOG = "('Shipped','Label Generated','Label Printed','Delivered','Returned')"

# Carrier remittance reference prefixes = "the carrier paid us for this order"
# (see accounting_portal/api/cod.py — kept identical here).
REF_PREFIXES = ("CATH", "RDF")

# ── Order source (sales channel) ─────────────────────────────────
# The Sales Order naming series encodes the channel — verified live 2026-07:
#   #…    Shopify storefront          J-…    landing pages
#   YC-…  YouCan store                SAL-…  agent / manual entry
# These four cover 100% of orders (custom_channel is only filled for
# YouCan/Landing, so the name prefix is the reliable classifier).
SOURCE_CASE = (
    "CASE WHEN so.name LIKE '#%%' THEN 'shopify' "
    "WHEN so.name LIKE 'YC-%%' THEN 'youcan' "
    "WHEN so.name LIKE 'J-%%' THEN 'landing' "
    "WHEN so.name LIKE 'SAL-%%' THEN 'agent' "
    "ELSE 'other' END"
)
SOURCE_PREFIX = {"shopify": "#", "youcan": "YC-", "landing": "J-", "agent": "SAL-"}
SOURCES = ("shopify", "youcan", "landing", "agent")


def source_cond(source, params):
    """WHERE fragment scoping to one source (by name prefix)."""
    if source and source in SOURCE_PREFIX:
        params["src_prefix"] = SOURCE_PREFIX[source] + "%"
        return " AND so.name LIKE %(src_prefix)s"
    return ""


def ref_present(col):
    return "(" + " OR ".join(f"IFNULL({col},'') LIKE '{p}%%'" for p in REF_PREFIXES) + ")"


def ref_absent(col):
    return "(" + " AND ".join(f"IFNULL({col},'') NOT LIKE '{p}%%'" for p in REF_PREFIXES) + ")"


# Reusable CASE expressions (so funnel + rates + departments never drift apart).
IS_CONFIRMED = f"so.custom_sales_status = {CONFIRMED}"
IS_DISPATCHED = (
    f"(so.custom_shipped_at IS NOT NULL OR so.custom_logistics_status IN {SHIPPED_LOG})"
)
IS_DELIVERED = (
    f"(so.custom_logistics_status = {DELIVERED_LOG} "
    f"OR so.custom_track_shipment_status = 'Delivered')"
)
IS_RETURNED = f"so.custom_logistics_status = {RETURNED_LOG}"
IS_REAL = f"IFNULL(so.custom_sales_status,'') NOT IN {DEAD_SALES}"


# ── Period resolution ────────────────────────────────────────────
def resolve_period(period, from_date=None, to_date=None):
    """Return (start, end, prev_start, prev_end, label_key).

    today → today only, compared to the same elapsed window yesterday.
    d7    → last 7 days incl. today, compared to the 7 before that.
    d30   → last 30 days, compared to the 30 before that.
    An explicit from/to range overrides period (prev = same-length window before).
    """
    today = getdate(nowdate())
    if from_date and to_date:
        s, e = getdate(from_date), getdate(to_date)
        span = (e - s).days + 1
        return s, e, getdate(add_days(s, -span)), getdate(add_days(s, -1)), "custom"
    if period == "d7":
        s = getdate(add_days(today, -6))
        return s, today, getdate(add_days(s, -7)), getdate(add_days(s, -1)), "d7"
    if period == "d30":
        s = getdate(add_days(today, -29))
        return s, today, getdate(add_days(s, -30)), getdate(add_days(s, -1)), "d30"
    # default: today
    return today, today, getdate(add_days(today, -1)), getdate(add_days(today, -1)), "today"


def company_cond(company, params):
    """Optional company scope. The owner's dashboard defaults to ALL companies;
    pass `company` to scope to one."""
    if company:
        params["company"] = company
        return " AND so.company = %(company)s"
    return ""


def base_where(start, end, company, params, alias="so"):
    """Submitted, real (non-cancelled) orders in the date window."""
    params["start"] = str(start)
    params["end"] = str(end)
    cond = (
        f"{alias}.docstatus = 1 "
        f"AND {alias}.transaction_date >= %(start)s AND {alias}.transaction_date <= %(end)s"
    )
    cond += company_cond(company, params)
    return cond


# ── Small rollup cache ───────────────────────────────────────────
_TTL = 120  # seconds; the dashboard polls, and orders bust the cache on update


def cached(key, builder):
    try:
        hit = frappe.cache().get_value(key)
        if hit is not None:
            return hit
    except Exception:
        hit = None
    val = builder()
    try:
        frappe.cache().set_value(key, val, expires_in_sec=_TTL)
    except Exception:
        pass
    return val


def bust_kpi_cache(doc=None, method=None):
    """doc_event hook: an order changed → drop the rollup caches."""
    try:
        for prefix in ("ops_kpi:", "ops_dept:", "ops_team:", "ops_alerts:"):
            frappe.cache().delete_keys(prefix)
    except Exception:
        pass


def assert_access():
    """Any logged-in user with dashboard access. Guests are rejected."""
    if frappe.session.user in (None, "Guest"):
        frappe.throw("Please log in to access the Ops Dashboard", frappe.AuthenticationError)
