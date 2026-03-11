<template>
  <DashboardShell
    title="Мои резюме"
    subtitle="Создавайте и обновляйте свои резюме в отдельном рабочем пространстве кандидата."
    role-label="Кандидат"
    :nav-items="navItems"
    :primary-action="{ to: '/candidate/resume', label: 'Создать резюме' }"
    home-path="/home"
    avatar-letter="К"
  >
    <template #aside>
      <UiCard title="Активные резюме" subtitle="0" />
      <UiCard title="Черновики" subtitle="0" />
      <UiCard title="Просмотры" subtitle="0" />
    </template>

    <PlaceholderPanel
      badge="Резюме"
      title="Раздел резюме кандидата"
      description="Здесь будет создание и редактирование резюме, а еще место для разных версий под разные вакансии и отслеживания просмотров со стороны работодателей."
    />
  </DashboardShell>
</template>

<script setup>
import DashboardShell from "../components/layouts/DashboardShell.vue";
import PlaceholderPanel from "../components/layouts/PlaceholderPanel.vue";
import UiCard from "../components/ui/UiCard.vue";

const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/vacancies", label: "Поиск вакансий" },
  { to: "/candidate/applications", label: "Мои отклики" },
  { to: "/candidate/resume", label: "Мои резюме" },
  { to: "/profile", label: "Профиль" },
];
</script>