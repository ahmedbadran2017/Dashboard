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
user. On the phone an **install banner** appears inside the app:
- **Android/Chrome**: tap تثبيت → the native install dialog opens.
- **iPhone/Safari**: Apple has no install API, so the banner shows the two
  steps instead (Share → Add to Home Screen).
The banner hides once installed (or after the user dismisses it).

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
- `manifest.webmanifest` + icons are served from `/assets/ops_dashboard/`.
- The service worker is served from the **site root** (`www/sw.js` → `/sw.js`)
  so it can legally control the `/ops/` scope — a worker under `/assets/` cannot
  without a `Service-Worker-Allowed` header Frappe doesn't send. This is also
  what lets Chrome/Android show the install prompt.
- The service worker caches the shell (instant offline open) and falls back to
  the **last known numbers** when the connection drops; it refreshes
  network-first when online.
- After deploying a new bundle, the SW picks it up on the next open (its
  VERSION string busts old caches; hard-refresh once if an old shell lingers).

## 5. Storefront traffic + conversion (Shopify)

The Home "Storefront traffic" card (sessions → cart → checkout → conversion)
pulls from Shopify via ShopifyQL. **No setup needed** — it reuses the credentials
from the existing ERPNext Shopify integration (`Shopify Setting` single: the
`shopify_url` + the `password` access token, decrypted server-side).

The only requirement: that token must have the **`read_reports`** scope (ShopifyQL
analytics). The sync app usually has order/product/inventory scopes but not
reports. If the card shows "connect Shopify":
1. Add `read_reports` to the Shopify custom app and re-install/refresh the token, **or**
2. Point at a token that has it, via config (takes precedence is NOT given — the
   Shopify Setting is tried first; to force config, disable `enable_shopify` or
   clear its token):
   ```bash
   bench --site admin.justyol.com set-config shopify_domain "9db8fb-e0.myshopify.com"
   bench --site admin.justyol.com set-config shopify_token "shpat_xxx"
   ```

Nothing else breaks if it's not set — the card just shows the prompt. Everything
else (cash, profit, products, orders, …) is ERPNext-only and needs no config.

## 6. Finance figures — how they're scoped

- **Cash available** sums only positive bank balances (accounts that hold money);
  loans/overdrafts/FX accounts are also `account_type=Bank` and would drag a naive
  total negative. Carrier float ("… Transactions" accounts) is shown separately.
- **Profitability** is a **trailing 30 days** for the operating company
  (`Justyol Morocco` — edit `OPERATING_COMPANY` in `api/business.py`). It is NOT
  "this calendar month" on purpose: invoice/GL posting lags, so a month-to-date
  P&L reads near-zero early in the month. The live *today* revenue signal stays the
  Sales-Order value on Home.

## 7. What's live vs. placeholder

Live from `tabSales Order`: orders, sales value, funnel, confirmation/delivery/
return rates, AOV, COD collected-vs-pending (CATH/RDF refs), stuck>48h, cities,
confirmation-team leaderboard, alerts.

Pending a data source: warehouse-picking & returns-closing leaderboards (no
per-agent field on the Sales Order yet — the Team tab shows "connect a data
source" for those two sections until we wire e.g. Pick List assignments).
