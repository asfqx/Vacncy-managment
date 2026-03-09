<template>
  <DashboardShell
    title="Создание вакансии"
    subtitle="Эта страница доступна только работодателю или администратору."
    role-label="Работодатель"
    :nav-items="navItems"
    :primary-action="{ to: '/employer/vacancies/create', label: 'Создать вакансию' }"
    home-path="/employer/resumes"
    avatar-letter="Р"
  >
    <PlaceholderPanel
      badge="Вакансии"
      title="Форма создания вакансии"
      description="Я подготовил отдельный защищенный маршрут для создания вакансии. Здесь можно будет разместить форму публикации, черновики и предпросмотр."
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
