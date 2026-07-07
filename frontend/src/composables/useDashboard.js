// Shared dashboard state: the selected period (today / d7 / d30) and a refresh
// nonce that pages watch to refetch. Kept module-global so Home, Departments,
// Orders and Team all read the same period.
import { ref } from "vue";

const period = ref("today");
const refreshNonce = ref(0);

export function useDashboard() {
  function setPeriod(p) {
    period.value = p;
  }
  function refresh() {
    refreshNonce.value++;
  }
  return { period, refreshNonce, setPeriod, refresh };
}
