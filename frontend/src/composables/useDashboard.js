// Shared dashboard state: the selected period (today / d7 / d30 / custom range)
// and a refresh nonce that pages watch to refetch. Kept module-global so Home,
// Departments, Orders and Team all read the same period.
import { ref, computed } from "vue";

const period = ref("today");
const fromDate = ref(null); // "YYYY-MM-DD" when period === "custom"
const toDate = ref(null);
const refreshNonce = ref(0);

export function useDashboard() {
  function setPeriod(p) {
    period.value = p;
    if (p !== "custom") {
      fromDate.value = null;
      toDate.value = null;
    }
  }
  function setCustomRange(from, to) {
    if (!from || !to) return;
    // keep from ≤ to regardless of input order
    if (from > to) [from, to] = [to, from];
    fromDate.value = from;
    toDate.value = to;
    period.value = "custom";
  }
  function refresh() {
    refreshNonce.value++;
  }
  // params every data call sends; backend resolve_period() uses the explicit
  // range when both dates are present ("custom" never reaches the named-period
  // branches, and it also keeps the today-only forecast off for ranges).
  function periodParams() {
    return {
      period: period.value,
      from_date: fromDate.value || null,
      to_date: toDate.value || null,
    };
  }
  // single reactive key pages watch to reload on ANY period change
  const periodKey = computed(() => `${period.value}:${fromDate.value}:${toDate.value}`);
  return { period, fromDate, toDate, refreshNonce, periodKey, setPeriod, setCustomRange, refresh, periodParams };
}
