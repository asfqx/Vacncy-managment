import { createRouter, createWebHistory } from "vue-router";
import LoginView from "./views/LoginView.vue";
import RegisterView from "./views/RegisterView.vue";
import RegisterRoleSelectView from "./views/RegisterRoleSelectView.vue";
import EmailConfirmView from "./views/EmailConfirmView.vue";
import HomeView from "./views/HomeView.vue";
import EmployerHomeView from "./views/EmployerHomeView.vue";
import CandidateApplicationsView from "./views/CandidateApplicationsView.vue";
import CandidateResumeView from "./views/CandidateResumeView.vue";
import EmployerApplicationsView from "./views/EmployerApplicationsView.vue";
import EmployerVacanciesView from "./views/EmployerVacanciesView.vue";
import EmployerCreateVacancyView from "./views/EmployerCreateVacancyView.vue";
import ProfileView from "./views/ProfileView.vue";
import PasswordResetRequestView from "./views/PasswordResetRequestView.vue";
import PasswordResetConfirmView from "./views/PasswordResetConfirmView.vue";
import VacancyView from "./views/VacancyView.vue";
import SharedHomeView from "./views/SharedHomeView.vue";
import { getAccessToken, getDefaultRouteForRole, getUserRoleFromToken, USER_ROLES } from "./utils/auth";

const employerRoles = [USER_ROLES.COMPANY, USER_ROLES.ADMIN];
const candidateRoles = [USER_ROLES.CANDIDATE];
const candidateSearchRoles = [USER_ROLES.CANDIDATE, USER_ROLES.ADMIN];
const sharedRoles = [...candidateRoles, ...employerRoles];

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: () => getDefaultRouteForRole(getUserRoleFromToken()),
    },
    { path: "/login", name: "login", component: LoginView },
    { path: "/register", name: "register-select", component: RegisterRoleSelectView },
    { path: "/register/:role(candidate|employer)", name: "register", component: RegisterView },
    { path: "/email-confirm", name: "email-confirm", component: EmailConfirmView },
    { path: "/password-reset", name: "password-reset", component: PasswordResetRequestView },
    { path: "/password-reset/confirm", name: "password-reset-confirm", component: PasswordResetConfirmView },
    {
      path: "/home",
      name: "shared-home",
      component: SharedHomeView,
      meta: { requiresAuth: true, roles: sharedRoles },
    },
    {
      path: "/vacancies",
      name: "candidate-vacancies",
      component: HomeView,
      meta: { requiresAuth: true, roles: candidateSearchRoles },
    },
    {
      path: "/vacancies/:uuid",
      name: "vacancy",
      component: VacancyView,
      meta: { requiresAuth: true, roles: candidateSearchRoles },
    },
    {
      path: "/candidate/applications",
      name: "candidate-applications",
      component: CandidateApplicationsView,
      meta: { requiresAuth: true, roles: candidateRoles },
    },
    {
      path: "/candidate/resume",
      name: "candidate-resume",
      component: CandidateResumeView,
      meta: { requiresAuth: true, roles: candidateRoles },
    },
    {
      path: "/employer/resumes",
      name: "employer-resumes",
      component: EmployerHomeView,
      meta: { requiresAuth: true, roles: employerRoles },
    },
    {
      path: "/employer/vacancies",
      name: "employer-vacancies",
      component: EmployerVacanciesView,
      meta: { requiresAuth: true, roles: employerRoles },
    },
    {
      path: "/employer/applications",
      name: "employer-applications",
      component: EmployerApplicationsView,
      meta: { requiresAuth: true, roles: employerRoles },
    },
    {
      path: "/employer/vacancies/create",
      name: "employer-create-vacancy",
      component: EmployerCreateVacancyView,
      meta: { requiresAuth: true, roles: employerRoles },
    },
    {
      path: "/profile",
      name: "profile",
      component: ProfileView,
      meta: { requiresAuth: true, roles: sharedRoles },
    },
    {
      path: "/:pathMatch(.*)*",
      redirect: () => getDefaultRouteForRole(getUserRoleFromToken()),
    },
  ],
});

router.beforeEach((to) => {
  const token = getAccessToken();
  const role = getUserRoleFromToken(token);
  const defaultPath = getDefaultRouteForRole(role);
  const isGuestOnlyRoute = to.path === "/login" || to.path.startsWith("/register");

  if (isGuestOnlyRoute && token) {
    return { path: defaultPath };
  }

  if (to.meta.requiresAuth && !token) {
    return { path: "/login" };
  }

  if (to.meta.roles?.length && !to.meta.roles.includes(role)) {
    return { path: defaultPath };
  }

  return true;
});

export default router;
