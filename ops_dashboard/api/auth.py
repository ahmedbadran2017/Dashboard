"""Current-user profile for the dashboard header/session."""
import frappe

from ops_dashboard.api import _base as B


@frappe.whitelist()
def me():
    B.assert_access()
    user = frappe.session.user
    full_name = frappe.db.get_value("User", user, "full_name") or user
    companies = [c.name for c in frappe.get_all("Company", fields=["name"], order_by="name")]
    return {
        "user": user,
        "name": full_name,
        "initials": "".join(p[0] for p in (full_name or "?").split()[:2]).upper(),
        "companies": companies,
        "roles": frappe.get_roles(user),
    }
