import frappe


def get_context(context):
    """Host-page controller for the Ops Dashboard SPA (served at /ops/*).

    Injects a per-session CSRF token so the SPA's POST /api/method calls are
    accepted. no_cache is essential: the token is per session, so the page must
    never be cached and served to another user."""
    context.no_cache = 1
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context
