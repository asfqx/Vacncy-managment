<template>
  <DashboardShell
    title="Мои резюме"
    subtitle="Кандидат может создавать и редактировать только свои резюме."
    role-label="Кандидат"
    :nav-items="navItems"
    :primary-action="{ to: '/candidate/resume', label: 'Создать резюме' }"
    home-path="/vacancies"
    avatar-letter="К"
  >
    <PlaceholderPanel
      badge="Резюме"
      title="Раздел создания резюме"
      description="Я выделил отдельную страницу под создание и редактирование резюме. Она доступна только кандидатам после входа."
    />
  </DashboardShell>
</template>

<script setup>
import DashboardShell from "../components/layouts/DashboardShell.vue";
import PlaceholderPanel from "../components/layouts/PlaceholderPanel.vue";

const navItems = [
  { to: "/vacancies", label: "Поиск вакансий" },
  { to: "/candidate/applications", label: "Мои отклики" },
  { to: "/candidate/resume", label: "Мои резюме" },
  { to: "/profile", label: "Профиль" },
];
</script>
