<template>
  <DashboardShell
    title="Отклики на вакансии"
    subtitle="Работодатель видит только отклики на свои вакансии."
    role-label="Работодатель"
    :nav-items="navItems"
    :primary-action="{ to: '/employer/vacancies/create', label: 'Создать вакансию' }"
    home-path="/employer/resumes"
    avatar-letter="Р"
  >
    <PlaceholderPanel
      badge="Работодатель"
      title="Раздел откликов работодателя"
      description="Страница закрыта для кандидатов и готова для вывода откликов по вакансиям компании."
    />
  </DashboardShell>
</template>

<script setup>
import DashboardShell from "../components/layouts/DashboardShell.vue";
import PlaceholderPanel from "../components/layouts/PlaceholderPanel.vue";

const navItems = [
  { to: "/employer/resumes", label: "Поиск резюме" },
  { to: "/employer/applications", label: "Отклики" },
  { to: "/employer/vacancies/create", label: "Создать вакансию" },
  { to: "/profile", label: "Профиль" },
];
</script>
