import { createRouter, createWebHistory } from "vue-router";

import AppShell from "@/components/AppShell.vue";
import Home from "@/pages/Home.vue";
import Departments from "@/pages/Departments.vue";
import DepartmentDetail from "@/pages/DepartmentDetail.vue";
import Orders from "@/pages/Orders.vue";
import Team from "@/pages/Team.vue";
import Finance from "@/pages/Finance.vue";
import Alerts from "@/pages/Alerts.vue";

const routes = [
  {
    path: "/ops",
    component: AppShell,
    children: [
      { path: "", redirect: "/ops/home" },
      { path: "home", name: "Home", component: Home, meta: { tab: "home" } },
      { path: "departments", name: "Departments", component: Departments, meta: { tab: "depts" } },
      { path: "departments/:id", name: "DepartmentDetail", component: DepartmentDetail, props: true, meta: { tab: "depts" } },
      { path: "orders", name: "Orders", component: Orders, meta: { tab: "orders" } },
      { path: "team", name: "Team", component: Team, meta: { tab: "team" } },
      { path: "finance", name: "Finance", component: Finance, meta: { tab: "finance" } },
      { path: "alerts", name: "Alerts", component: Alerts, meta: { tab: "alerts" } },
    ],
  },
  { path: "/", redirect: "/ops/home" },
  { path: "/:pathMatch(.*)*", redirect: "/ops/home" },
];

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});
