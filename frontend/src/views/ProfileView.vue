<template>
  <DashboardShell
    :title="title"
    subtitle="Профиль доступен обеим ролям, но вход в другие разделы ограничен согласно правам."
    :role-label="roleLabel"
    :nav-items="navItems"
    :primary-action="primaryAction"
    :home-path="homePath"
    :avatar-letter="avatarLetter"
  >
    <PlaceholderPanel
      badge="Профиль"
      :title="`Личный кабинет: ${roleLabel}`"
      :description="description"
    />
  </DashboardShell>
</template>

<script setup>
import { computed } from "vue";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import PlaceholderPanel from "../components/layouts/PlaceholderPanel.vue";
import { getRoleLabel, getUserRoleFromToken, isEmployerRole } from "../utils/auth";

const role = getUserRoleFromToken();
const employer = isEmployerRole(role);

const roleLabel = computed(() => getRoleLabel(role));
const title = computed(() => (employer ? "Профиль работодателя" : "Профиль кандидата"));
const homePath = computed(() => (employer ? "/employer/resumes" : "/vacancies"));
const avatarLetter = computed(() => (employer ? "Р" : "К"));
const primaryAction = computed(() => (
  employer
    ? { to: "/employer/vacancies/create", label: "Создать вакансию" }
    : { to: "/candidate/resume", label: "Создать резюме" }
));
const description = computed(() => (
  employer
    ? "Здесь можно вывести информацию о компании, реквизиты, контакты и настройки работодателя."
    : "Здесь можно вывести персональные данные кандидата, контакты, резюме и настройки уведомлений."
));
const navItems = computed(() => (
  employer
    ? [
        { to: "/employer/resumes", label: "Поиск резюме" },
        { to: "/employer/applications", label: "Отклики" },
        { to: "/employer/vacancies/create", label: "Создать вакансию" },
        { to: "/profile", label: "Профиль" },
      ]
    : [
        { to: "/vacancies", label: "Поиск вакансий" },
        { to: "/candidate/applications", label: "Мои отклики" },
        { to: "/candidate/resume", label: "Мои резюме" },
        { to: "/profile", label: "Профиль" },
      ]
));
</script>
