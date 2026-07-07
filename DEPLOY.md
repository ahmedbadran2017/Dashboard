# Deploying the Ops Dashboard to admin.justyol.com

The dashboard is a Frappe app (`ops_dashboard`) that serves a pre-built Vue PWA
at `/ops/*`. The built bundle is **committed to git**, so the production bench
does **not** need Node — it only installs the app and clears cache.

> GitHub repo: **`Dashbaord`** (`ahmedbadran2017/Dashbaord`) — the Frappe **app
> name stays `ops_dashboard`** (the python package). `bench get-app` takes the
> app name as its first argument, so we pass `ops_dashboard` explicitly below.

## 1. First install (run on the server)

```bash
cd ~/frappe-bench
bench get-app ops_dashboard https://github.com/ahmedbadran2017/Dashbaord
bench --site admin.justyol.com install-app ops_dashboard
bench --site admin.justyol.com clear-cache
bench restart                             # or: sudo supervisorctl restart all
```

Then open **https://admin.justyol.com/ops/home** — log in with your ERPNext
user. On the phone: open it in Safari/Chrome → **Add to Home Screen** → it
installs as the Justyol Ops app (standalone, offline shell, orange icon).

## 2. Updating after changes

Local (build + commit + push in one step):

```bash
cd "/Users/ahmedbadran/App Dashboard/ops_dashboard"
./deploy.sh "what changed"
```

Server:

```bash
cd ~/frappe-bench/apps/ops_dashboard && git pull
cd ~/frappe-bench
bench --site admin.justyol.com clear-cache
bench restart
```

(`migrate` is only needed if a future change adds fixtures/doctypes — plain
KPI/UI changes just need pull + clear-cache.)

## 3. Access

Any logged-in ERPNext user can open the dashboard (guests are rejected by
`api/_base.py::assert_access`). If you later want it owner/manager-only, add a
role check there — one line.

## 4. PWA notes

- Served pages: `/ops/*` → `templates/pages/ops.html` hosts the SPA.
- `manifest.webmanifest` + `sw.js` are served from `/assets/ops_dashboard/`.
- The service worker caches the shell (instant offline open) and falls back to
  the **last known numbers** when the connection drops; it refreshes
  network-first when online.
- After deploying a new bundle, the SW picks it up on the next open (its
  VERSION string busts old caches; hard-refresh once if an old shell lingers).

## 5. What's live vs. placeholder

Live from `tabSales Order`: orders, sales value, funnel, confirmation/delivery/
return rates, AOV, COD collected-vs-pending (CATH/RDF refs), stuck>48h, cities,
confirmation-team leaderboard, alerts.

Pending a data source: warehouse-picking & returns-closing leaderboards (no
per-agent field on the Sales Order yet — the Team tab shows "connect a data
source" for those two sections until we wire e.g. Pick List assignments).
