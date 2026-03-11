<template>
  <DashboardShell
    title="Мои отклики"
    subtitle="Здесь будут собраны статусы откликов, ответы компаний и история ваших заявок."
    role-label="Кандидат"
    :nav-items="navItems"
    :primary-action="{ to: '/candidate/resume', label: 'Создать резюме' }"
    home-path="/home"
    avatar-letter="К"
  >
    <template #aside>
      <UiCard title="Новые ответы" subtitle="0" />
      <UiCard title="В работе" subtitle="0" />
      <UiCard title="Архив" subtitle="0" />
    </template>

    <PlaceholderPanel
      badge="История"
      title="Раздел откликов кандидата"
      description="Здесь появятся карточки откликов, статусы рассмотрения и история переходов по этапам, чтобы вы в любой момент понимали, где и на каком шаге сейчас находитесь."
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