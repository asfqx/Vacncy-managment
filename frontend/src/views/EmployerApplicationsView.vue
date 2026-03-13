<template>
  <DashboardShell
    title="Отклики на вакансии"
    subtitle="Работодатель видит только отклики на свои вакансии."
    role-label="Работодатель"
    :nav-items="navItems"
    :primary-action="{ to: '/employer/vacancies/create', label: 'Создать вакансию' }"
    :secondary-action="secondaryAction"
    home-path="/home"
    avatar-letter="Р"
  >
    <PlaceholderPanel
      badge="Работодатель"
      title="Раздел откликов работодателя"
      description="Страница готова для вывода откликов по вакансиям компании и закрыта для кандидатов."
    />
  </DashboardShell>
</template>

<script setup>
import { computed } from "vue";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import PlaceholderPanel from "../components/layouts/PlaceholderPanel.vue";
import { getUserRoleFromToken, isAdminRole } from "../utils/auth";

const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/employer/resumes", label: "Поиск резюме" },
  { to: "/employer/vacancies", label: "Мои вакансии" },
  { to: "/employer/applications", label: "Отклики" },
  { to: "/employer/vacancies/create", label: "Создать вакансию" },
  { to: "/profile", label: "Профиль" },
];

const role = getUserRoleFromToken();
const secondaryAction = computed(() => (
  isAdminRole(role) ? { to: "/vacancies", label: "Страница кандидата" } : null
));
</script>
