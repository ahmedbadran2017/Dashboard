app_name = "ops_dashboard"
app_title = "Justyol Ops Dashboard"
app_publisher = "Justyol"
app_description = "Mobile-first operations dashboard (PWA) for Justyol — live order volume, funnel, department KPIs, team performance, COD collection and alerts, read from ERPNext."
app_email = "info@justyol.com"
app_license = "MIT"

# ── Website routing ──────────────────────────────────────────────
# Serve the Vue SPA (PWA) for every /ops/* route. The service worker and
# manifest are served as static assets from the app's public/ folder.
website_route_rules = [
    {"from_route": "/ops/<path:app_path>", "to_route": "ops"},
]

# The PWA manifest + service worker live at the app root of the assets mount
# (/assets/ops_dashboard/...). See templates/pages/ops.html for the links.

# ── Cache busting ────────────────────────────────────────────────
# The dashboard caches aggregate KPI rollups for a short TTL (see api/_base.py).
# When an order moves through the pipeline we drop the rollup cache so the next
# refresh is live rather than up-to-TTL stale.
doc_events = {
    "Sales Order": {
        "on_update": "ops_dashboard.api._base.bust_kpi_cache",
    },
}
