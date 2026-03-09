<template>
  <DashboardShell
    title="Мои отклики"
    subtitle="Кандидату доступна только его собственная история откликов."
    role-label="Кандидат"
    :nav-items="navItems"
    :primary-action="{ to: '/candidate/resume', label: 'Создать резюме' }"
    home-path="/vacancies"
    avatar-letter="К"
  >
    <PlaceholderPanel
      badge="История"
      title="Раздел откликов кандидата"
      description="Эта страница уже зарезервирована только для кандидата. Сюда можно вывести статус откликов, ответы работодателей и архив прошлых заявок."
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
