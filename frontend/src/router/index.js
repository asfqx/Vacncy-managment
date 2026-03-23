import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import EmailConfirmView from "../views/EmailConfirmView.vue";
import HomeView from "../views/HomeView.vue";
import PasswordResetRequestView from "../views/PasswordResetRequestView.vue";
import PasswordResetConfirmView from "../views/PasswordResetConfirmView.vue";
import VacancyView from "../views/VacancyView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView },
    { path: "/register", name: "register", component: RegisterView },
    { path: "/email-confirm", name: "email-confirm", component: EmailConfirmView },
    { path: "/password-reset", name: "password-reset", component: PasswordResetRequestView },
    { path: "/password-reset/confirm", name: "password-reset-confirm", component: PasswordResetConfirmView },
    { path: "/", name: "home", component: HomeView, meta: { requiresAuth: true } },
    { path: "/vacancies/:uuid", name: "vacancy", component: VacancyView, meta: { requiresAuth: true } },
  ],
});

router.beforeEach((to) => {
  const token = localStorage.getItem("access_token");

  if ((to.path === "/login" || to.path === "/register") && token) return { path: "/" };

  if (to.meta.requiresAuth && !token) return { path: "/login" };

  return true;
});

export default router;