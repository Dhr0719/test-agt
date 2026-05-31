import { createRouter, createWebHistory } from "vue-router";

// import HomeView from "@/pages/HomeView.vue";
import TestView from "@/pages/test.vue";
import UploadView from "@/pages/UploadView.vue";

const routes = [
  {
    path: "/",
    redirect: "/upload",
  },
//   {
//     path: "/home",
//     name: "Home",
//     component: HomeView,
//   },
  {
    path: "/test",
    name: "test",
    component: TestView,
  },
  {
    path: "/upload",
    name: "Upload",
    component: UploadView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;