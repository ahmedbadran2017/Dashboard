"""Advertising: blended ROAS, cost-per-order, and spend by channel.

Architecture (deliberate): the dashboard NEVER calls Meta/TikTok/Google live —
those APIs are slow, rate-limited, and Google's OAuth expires. Instead a daily
scheduled job (`sync_all_ad_spend`) pulls each platform's spend into the
`JoyAgent Ad Spend` doctype, and `overview` reads from that doctype. So the card
is fast + reliable and keeps working if a platform is down; it just goes stale.

The headline metric is BLENDED ROAS (a.k.a. MER) = ERPNext sales ÷ total ad
spend. It needs no per-click attribution (the hard, unsolved part — UTM is empty
in ERPNext), so it's the honest top-line number. Cost-per-order = spend ÷ orders.

Spend rows in `JoyAgent Ad Spend`: {as_of: date, label: platform, spend, currency}.
"""
import frappe
from frappe.utils import add_days, flt, getdate, nowdate

from ops_dashboard.api import _base as B
from ops_dashboard.api.kpis import _agg

# label (as written by the sync jobs) → canonical channel id
CHANNELS = {"meta": "meta", "facebook": "meta", "instagram": "meta",
            "tiktok": "tiktok", "google": "google", "google ads": "google"}

# The trailing window the sync's `spend` figure covers (meta_ad_insights
# .sync_ad_spend(period_days=30)). Keep in step with it.
SPEND_WINDOW_DAYS = 30


def _channel(label, ad_id=None):
    """Canonical channel for a spend row.

    The sync never writes `label` — every row on production has it empty — so
    every dirham landed in "other" and the channel split read "Other 100%",
    which says nothing. A Meta ad id is a long numeric string, and Meta is the
    only platform wired up, so an unlabelled numeric id IS Meta. Labelled rows
    still win, so naming a channel at the source keeps working.
    """
    c = CHANNELS.get((label or "").strip().lower())
    if c:
        return c
    aid = str(ad_id or "").strip()
    if aid.isdigit() and len(aid) >= 12:
        return "meta"
    return "other"


@frappe.whitelist()
def overview(period="today", company=None, from_date=None, to_date=None):
    """Blended ROAS + CPO + per-channel spend for the period. Reads spend from the
    JoyAgent Ad Spend doctype; returns needs_config when no spend has synced yet."""
    B.assert_access()
    ck = f"ops_kpi:ads:{period}:{company or ''}:{from_date or ''}:{to_date or ''}"

    def build():
        start, end, ps, pe, _ = B.resolve_period(period, from_date, to_date)
        # `JoyAgent Ad Spend` holds ONE ROW PER AD, and the sync overwrites
        # `spend` with that ad's spend over its own trailing window (30 days by
        # default) while stamping `as_of` with the DATE OF THE SYNC. There is no
        # per-day spend anywhere in the schema.
        #
        # Filtering `as_of BETWEEN start AND end` therefore selects ads by when
        # they were last synced, not when the money was spent, and summing
        # `spend` adds up 30-day totals. On the "today" tab that produced a
        # confident 11.5K spend, ROAS 4.39x and CPO 49 MAD out of the trailing
        # totals of whichever three ads happened to sync this morning.
        #
        # Until the sync stores daily rows (Meta's insights API returns them with
        # time_increment=1 — the real fix, and it belongs in supplier_portal),
        # the only honest reading is the whole trailing window. So read every ad
        # and say plainly which window it covers, instead of pretending the
        # number belongs to the selected period.
        rows = frappe.db.sql(
            """SELECT ad_id, label, ROUND(SUM(spend)) spend FROM `tabJoyAgent Ad Spend`
               GROUP BY ad_id, label""", as_dict=True)
        if not rows:
            return {"needs_config": True}
        synced_on = frappe.db.sql(
            "SELECT MAX(as_of) FROM `tabJoyAgent Ad Spend`")[0][0]
        by_channel = {}
        for r in rows:
            c = _channel(r.label, r.ad_id)
            by_channel[c] = by_channel.get(c, 0.0) + flt(r.spend)
        total_spend = sum(by_channel.values())
        # Spend covers a trailing 30 days, so the revenue it is divided by has to
        # cover the same 30 days or the ratio is meaningless. This is NOT the
        # selected period, and the response says so.
        win_start = getdate(add_days(getdate(nowdate()), -(SPEND_WINDOW_DAYS - 1)))
        win = _agg(win_start, getdate(nowdate()), company)
        sales = flt(win["value"])
        orders = int(win["orders"])
        roas = round(sales / total_spend, 2) if total_spend else 0
        return {
            "needs_config": False, "currency": "MAD",
            # The window these three numbers actually describe. The UI must show
            # it: on the "today" tab they are not today's.
            "window_days": SPEND_WINDOW_DAYS,
            "synced_on": str(synced_on) if synced_on else None,
            "spend": total_spend,
            "sales": sales,
            "roas": roas,
            "roas_delta": None,   # no per-day history to compare against yet
            "cpo": round(total_spend / orders) if orders else 0,
            "channels": [
                {"id": c, "spend": by_channel[c],
                 "share": round(100.0 * by_channel[c] / total_spend, 1) if total_spend else 0}
                for c in sorted(by_channel, key=lambda k: -by_channel[k])
            ],
        }

    return B.cached(ck, build)


# ── Daily spend sync (scheduled) ─────────────────────────────────
def _record_spend(platform, day, amount, currency="MAD"):
    """Idempotent upsert of one platform's spend for one day into JoyAgent Ad Spend."""
    day = str(getdate(day))
    frappe.db.delete("JoyAgent Ad Spend", {"label": platform, "as_of": day})
    frappe.get_doc({
        "doctype": "JoyAgent Ad Spend", "label": platform, "as_of": day,
        "spend": flt(amount), "currency": currency,
    }).insert(ignore_permissions=True)


def sync_meta_spend(days=3):
    """Pull daily spend from the Meta Marketing API into JoyAgent Ad Spend.
    Config: meta_ads_token (required), meta_ads_account (default 168583286019654)."""
    token = frappe.conf.get("meta_ads_token")
    account = frappe.conf.get("meta_ads_account") or "168583286019654"
    if not token:
        return {"ok": False, "reason": "meta_ads_token not set"}
    import requests
    from frappe.utils import add_days, nowdate
    since = str(getdate(add_days(nowdate(), -int(days))))
    until = str(getdate(nowdate()))
    r = requests.get(
        f"https://graph.facebook.com/v20.0/act_{account}/insights",
        params={"fields": "spend", "time_increment": 1,
                "time_range": f'{{"since":"{since}","until":"{until}"}}',
                "access_token": token},
        timeout=30)
    n = 0
    for row in r.json().get("data", []):
        _record_spend("Meta", row.get("date_start"), row.get("spend", 0))
        n += 1
    frappe.db.commit()
    return {"ok": True, "days": n}


def sync_tiktok_spend(days=3):
    """Pull daily spend from the TikTok Business API. Config: tiktok_access_token,
    tiktok_advertiser_id."""
    token = frappe.conf.get("tiktok_access_token")
    advertiser = frappe.conf.get("tiktok_advertiser_id")
    if not (token and advertiser):
        return {"ok": False, "reason": "tiktok creds not set"}
    import requests
    from frappe.utils import add_days, nowdate
    since = str(getdate(add_days(nowdate(), -int(days))))
    until = str(getdate(nowdate()))
    r = requests.get(
        "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
        headers={"Access-Token": token},
        params={"advertiser_id": advertiser, "report_type": "BASIC",
                "data_level": "AUCTION_ADVERTISER", "dimensions": '["stat_time_day"]',
                "metrics": '["spend"]', "start_date": since, "end_date": until},
        timeout=30)
    n = 0
    for row in (r.json().get("data", {}) or {}).get("list", []):
        dims = row.get("dimensions", {})
        metrics = row.get("metrics", {})
        day = (dims.get("stat_time_day") or "")[:10]
        if day:
            _record_spend("TikTok", day, metrics.get("spend", 0))
            n += 1
    frappe.db.commit()
    return {"ok": True, "days": n}


def sync_google_spend(days=3):
    """Pull daily spend from the Google Ads API. Config: google_ads_* (developer
    token, OAuth refresh token, customer + login-customer ids). NOTE: the Google
    Ads OAuth for account 7430474060 currently needs renewal — until refreshed
    this returns ok:false and the other channels still populate."""
    cfg = frappe.conf
    needed = ("google_ads_developer_token", "google_ads_refresh_token",
              "google_ads_client_id", "google_ads_client_secret", "google_ads_customer_id")
    if not all(cfg.get(k) for k in needed):
        return {"ok": False, "reason": "google ads creds not set (OAuth needs renewal)"}
    try:
        import requests
        from frappe.utils import add_days, nowdate
        # exchange refresh token → access token
        tok = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": cfg.get("google_ads_client_id"),
            "client_secret": cfg.get("google_ads_client_secret"),
            "refresh_token": cfg.get("google_ads_refresh_token"),
            "grant_type": "refresh_token"}, timeout=30).json()
        access = tok.get("access_token")
        if not access:
            return {"ok": False, "reason": "google token refresh failed"}
        since = str(getdate(add_days(nowdate(), -int(days)))).replace("-", "")
        until = str(getdate(nowdate())).replace("-", "")
        cid = str(cfg.get("google_ads_customer_id")).replace("-", "")
        headers = {"developer-token": cfg.get("google_ads_developer_token"),
                   "Authorization": f"Bearer {access}"}
        if cfg.get("google_ads_login_customer_id"):
            headers["login-customer-id"] = str(cfg.get("google_ads_login_customer_id")).replace("-", "")
        gaql = ("SELECT segments.date, metrics.cost_micros FROM customer "
                f"WHERE segments.date BETWEEN '{since}' AND '{until}'")
        r = requests.post(
            f"https://googleads.googleapis.com/v17/customers/{cid}/googleAds:searchStream",
            headers=headers, json={"query": gaql}, timeout=30)
        n = 0
        for batch in r.json():
            for res in batch.get("results", []):
                day = res.get("segments", {}).get("date")
                micros = flt(res.get("metrics", {}).get("costMicros", 0))
                if day:
                    _record_spend("Google", day, micros / 1_000_000.0)
                    n += 1
        frappe.db.commit()
        return {"ok": True, "days": n}
    except Exception as e:
        frappe.log_error(f"Google Ads sync failed: {e}", "ops_dashboard")
        return {"ok": False, "reason": str(e)}


def sync_all_ad_spend():
    """Scheduler entry point (daily): pull all three platforms, tolerate failures."""
    results = {}
    for name, fn in (("meta", sync_meta_spend), ("tiktok", sync_tiktok_spend), ("google", sync_google_spend)):
        try:
            results[name] = fn()
        except Exception as e:
            frappe.log_error(f"{name} ad-spend sync failed: {e}", "ops_dashboard")
            results[name] = {"ok": False, "reason": str(e)}
    try:
        frappe.cache().delete_keys("ops_kpi:ads:")
    except Exception:
        pass
    return results


@frappe.whitelist()
def sync_now():
    """Manual trigger (System Manager) — run all syncs on demand for testing."""
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw("Not permitted", frappe.PermissionError)
    return sync_all_ad_spend()
