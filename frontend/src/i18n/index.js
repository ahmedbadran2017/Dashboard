// Bilingual copy — Arabic (default, RTL) / English (LTR). Strings lifted verbatim
// from the design prototype so the recreation matches. Access via useI18n().t(key).
import { ref, computed } from "vue";

const STR = {
  appTitle: ["لوحة العمليات", "Ops Dashboard"],
  subtitle: ["لوحة العمليات", "Operations"],
  // header
  live: ["مباشر", "Live"],
  refresh: ["تحديث", "Refresh"],
  // periods
  today: ["اليوم", "Today"],
  d7: ["7 أيام", "7 days"],
  d30: ["30 يوم", "30 days"],
  customTab: ["مخصص", "Custom"],
  customTitle: ["اختار الفترة", "Pick a date range"],
  fromLabel: ["من", "From"],
  toLabel: ["إلى", "To"],
  applyBtn: ["تطبيق", "Apply"],
  qYesterday: ["أمس", "Yesterday"],
  qThisMonth: ["الشهر ده", "This month"],
  qLastMonth: ["الشهر اللي فات", "Last month"],
  qLast90: ["آخر 90 يوم", "Last 90 days"],
  vsPrevPeriod: ["عن الفترة اللي قبلها", "vs previous period"],
  // hero
  orders: ["الأوردرات", "Orders"],
  salesValue: ["قيمة المبيعات", "Sales value"],
  vsYesterday: ["عن نفس الوقت أمس", "vs same time yesterday"],
  vsLastWeek: ["عن الأسبوع اللي فات", "vs last week"],
  vsLastMonth: ["عن الشهر اللي فات", "vs last month"],
  forecast: ["متوقع نهاية اليوم:", "Projected end of day:"],
  forecastUnit: ["أوردر بمعدل الساعة الحالي", "orders at current hourly rate"],
  // funnel
  funnelTitle: ["رحلة الأوردر", "Order funnel"],
  fNew: ["وصل جديد", "New"],
  fConfirmed: ["اتأكد", "Confirmed"],
  fDispatched: ["خرج للشحن", "Dispatched"],
  fDelivered: ["اتسلّم", "Delivered"],
  // rate cards
  rConfirmation: ["معدل التأكيد", "Confirmation rate"],
  rDelivery: ["معدل التسليم", "Delivery rate"],
  rAov: ["متوسط قيمة الأوردر", "Avg order value"],
  rReturns: ["نسبة المرتجعات", "Return rate"],
  // sources
  sourcesTitle: ["مصادر الأوردرات", "Order sources"],
  srcShopify: ["شوبيفاي", "Shopify"],
  srcYoucan: ["يوكان", "YouCan"],
  srcLanding: ["لاندينج", "Landing"],
  srcAgent: ["أجينت", "Agent"],
  srcOther: ["تاني", "Other"],
  confShort: ["تأكيد", "conf."],
  allSources: ["كل المصادر", "All sources"],
  // storefront funnel (Shopify)
  storefrontTitle: ["حركة المتجر", "Storefront traffic"],
  visits: ["زيارات", "Visits"],
  addedToCart: ["ضافوا للسلة", "Added to cart"],
  reachedCheckout: ["وصلوا للدفع", "Reached checkout"],
  conversionRate: ["معدل التحويل", "Conversion rate"],
  connectShopify: ["اربط Shopify عشان تشوف الزيارات والتحويل", "Connect Shopify to see traffic & conversion"],
  // top products / stock
  topProductsTitle: ["أكثر المنتجات مبيعاً", "Top products"],
  lowStockTitle: ["منتجات قربت تخلص", "Running low on stock"],
  lowStockSub: ["منتجات نجمة، المتبقي قليل — راجع المخزون", "Best-sellers with low stock — reorder"],
  unitsSold: ["اتباع", "sold"],
  left: ["متبقي", "left"],
  // finance tab
  financeTitle: ["المالية", "Finance"],
  cashTitle: ["الكاش المتاح", "Cash available"],
  inBanks: ["في البنوك", "In banks"],
  atCarriers: ["عند شركات الشحن", "Held by carriers"],
  onCards: ["على البطاقات", "On cards"],
  profitTitle: ["الربحية · آخر 30 يوم", "Profitability · last 30 days"],
  revenue: ["الإيراد", "Revenue"],
  cogs: ["تكلفة البضاعة", "COGS"],
  grossProfit: ["الربح الإجمالي", "Gross profit"],
  netProfit: ["صافي الربح", "Net profit"],
  margin: ["الهامش", "Margin"],
  topExpenses: ["أكبر المصروفات", "Top expenses"],
  supplierPayable: ["مستحقات الموردين", "Owed to suppliers"],
  operatingCompany: ["شركة التشغيل", "operating company"],
  // cod
  codTitle: ["تحصيل الدفع عند الاستلام", "COD collection"],
  codCollected: ["اتحصّل", "Collected"],
  codPending: ["معلّق عند الكوريير", "Pending at courier"],
  // late
  lateTitle: ["أوردرات متأخرة / عالقة", "Late / stuck orders"],
  lateSub: ["فاتت 48 ساعة من غير حركة — اضغط للتفاصيل", "No movement for 48h — tap for details"],
  // daily report
  reportTitle: ["التقرير اليومي", "Daily report"],
  reportSub: ["ملخص الأداء يتبعت أوتوماتيك الساعة 10 مساءً", "Performance summary auto-sent at 10 PM"],
  reportWa: ["ابعت واتساب", "Send WhatsApp"],
  reportPdf: ["نزّل PDF", "Download PDF"],
  // departments
  deptsTitle: ["أداء الأقسام", "Department performance"],
  weekTrend: ["آخر 7 أيام", "Last 7 days"],
  topTeam: ["أفضل أداء في الفريق", "Top performers"],
  back: ["الأقسام", "Departments"],
  target: ["الهدف:", "Target:"],
  // orders
  ordersTitle: ["الأوردرات", "Orders"],
  searchPh: ["دوّر برقم الأوردر أو اسم العميل…", "Search by order # or customer…"],
  all: ["الكل", "All"],
  allCities: ["كل المدن", "All cities"],
  sNew: ["جديد", "New"],
  sConf: ["مؤكد", "Confirmed"],
  sDisp: ["خرج للشحن", "Dispatched"],
  sDel: ["اتسلّم", "Delivered"],
  sRet: ["مرتجع", "Returned"],
  // order sheet
  confirmAttempts: ["محاولات التأكيد", "Confirm attempts"],
  items: ["المنتجات", "Items"],
  courier: ["الكوريير", "Courier"],
  itemsN: ["قطع", "items"],
  tlReceived: ["الأوردر وصل من المتجر", "Order received"],
  tlConfirmed: ["اتأكد مع العميل", "Confirmed with customer"],
  tlDispatched: ["خرج مع الكوريير", "Dispatched"],
  tlDelivered: ["اتسلّم وCOD اتحصل", "Delivered, COD collected"],
  pending: ["لسه", "Pending"],
  waCustomer: ["واتساب العميل", "WhatsApp customer"],
  trackShipment: ["تتبع الشحنة", "Track shipment"],
  // team
  teamTitle: ["أداء الفريق", "Team performance"],
  teamConf: ["فريق التأكيد", "Confirmation team"],
  teamWh: ["فريق المخزن", "Warehouse team"],
  teamRet: ["فريق المرتجعات", "Returns team"],
  mConfirmed: ["أوردرات اتأكدت اليوم", "confirmed today"],
  mPicked: ["أوردرات اتحضرت اليوم", "picked today"],
  mClosed: ["مرتجعات اتقفلت اليوم", "closed today"],
  needsSource: ["محتاج ربط مصدر البيانات", "Connect a data source"],
  needsSourceSub: ["مفيش حقل يربط الموظف بالأوردر في السكيمة الحالية", "No per-agent field in the current schema"],
  // alerts
  alertsTitle: ["التنبيهات", "Alerts"],
  noAlerts: ["مفيش تنبيهات دلوقتي 🎉", "No alerts right now 🎉"],
  hoursAgo: ["من {n} ساعة", "{n}h ago"],
  today2: ["النهارده", "Today"],
  // install banner
  installTitle: ["ثبّت الأب على موبايلك", "Install the app on your phone"],
  installSub: ["شاشة كاملة، أسرع، ويشتغل أوفلاين", "Full screen, faster, works offline"],
  installBtn: ["تثبيت", "Install"],
  installIos1: ["دوس زرار المشاركة", "Tap the Share button"],
  installIos2: ["وبعدين «Add to Home Screen»", "then “Add to Home Screen”"],
  // shared
  loading: ["بنحمّل…", "Loading…"],
  errorLoad: ["حصل خطأ في التحميل", "Couldn’t load"],
  retry: ["إعادة المحاولة", "Retry"],
};

// Alert copy (title + sub) keyed by the backend alert `key`; {v} substitutes count/value.
export const ALERT_COPY = {
  stuck: {
    title: ["{v} أوردر عالق في الشحن أكتر من 48 ساعة", "{v} orders stuck in dispatch > 48h"],
    sub: ["الكوريير ما سحبش دفعة — اتواصل معاه", "Carrier missed pickup — contact them"],
  },
  cod_overdue: {
    title: ["{v} MAD تحصيل COD متأخر أكتر من 7 أيام", "{v} MAD COD overdue > 7 days"],
    sub: ["راجع كشف التسوية من الكوريير", "Review the carrier settlement statement"],
  },
  no_confirm_call: {
    title: ["{v} أوردر من غير أول محاولة تأكيد خلال 4 ساعات", "{v} orders with no first confirmation call in 4h"],
    sub: ["طابور التأكيد متكدس", "Confirmation queue backed up"],
  },
  return_rate: {
    title: ["نسبة المرتجعات طلعت {v}% الشهر ده", "Return rate up to {v}% this month"],
    sub: ["راجع أسباب الإرجاع", "Review return reasons"],
  },
  low_stock: {
    title: ["{v} منتجات قربت تخلص من المخزن", "{v} SKUs close to stock-out"],
    sub: ["راجع المخزون قبل الحملة الجاية", "Review stock before the next campaign"],
  },
};

// Department display metadata (name + icon + accent), keyed by id.
export const DEPT_META = {
  conf: { name: ["تأكيد الطلبات", "Confirmation"], icon: "check", accent: "green" },
  wh: { name: ["المخزن والتحضير", "Warehouse & Picking"], icon: "box", accent: "orange" },
  disp: { name: ["الشحن وخروج الأوردرات", "Dispatch"], icon: "truck", accent: "blue" },
  del: { name: ["التوصيل", "Delivery"], icon: "pin", accent: "green" },
  ret: { name: ["المرتجعات", "Returns"], icon: "ret", accent: "red" },
  cod: { name: ["تحصيل COD", "COD Collection"], icon: "cash", accent: "orange" },
  mkt: { name: ["التسويق والمبيعات", "Marketing & Sales"], icon: "trend", accent: "orange" },
};

const STORAGE_KEY = "ops.lang";
const lang = ref((typeof localStorage !== "undefined" && localStorage.getItem(STORAGE_KEY)) || "ar");

export function useI18n() {
  const isAr = computed(() => lang.value === "ar");
  const dir = computed(() => (isAr.value ? "rtl" : "ltr"));
  function t(key, vars) {
    const pair = STR[key];
    let s = pair ? pair[isAr.value ? 0 : 1] : key;
    if (vars) for (const k in vars) s = s.replace(`{${k}}`, vars[k]);
    return s;
  }
  // localize a [ar,en] tuple directly
  function L(pair, vars) {
    let s = Array.isArray(pair) ? pair[isAr.value ? 0 : 1] : pair;
    if (vars) for (const k in vars) s = s.replace(`{${k}}`, vars[k]);
    return s;
  }
  function toggle() {
    lang.value = isAr.value ? "en" : "ar";
    if (typeof localStorage !== "undefined") localStorage.setItem(STORAGE_KEY, lang.value);
    document.documentElement.setAttribute("dir", dir.value);
    document.documentElement.setAttribute("lang", lang.value);
  }
  return { lang, isAr, dir, t, L, toggle };
}

export function applyLangToRoot() {
  const l = lang.value;
  const d = l === "ar" ? "rtl" : "ltr";
  document.documentElement.setAttribute("dir", d);
  document.documentElement.setAttribute("lang", l);
}
