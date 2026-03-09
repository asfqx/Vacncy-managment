<template>
  <DashboardShell
    title="Поиск резюме"
    subtitle="Работодателю доступны поиск резюме, отклики на вакансии, создание вакансии и профиль."
    role-label="Работодатель"
    :nav-items="navItems"
    :primary-action="{ to: '/employer/vacancies/create', label: 'Создать вакансию' }"
    home-path="/employer/resumes"
    avatar-letter="Р"
  >
    <template #aside>
      <UiCard title="Отклики по вакансиям" subtitle="Под контролем" />
      <UiCard title="Активные вакансии" subtitle="Размещение" />
      <UiCard title="Профиль компании" subtitle="Настройки" />
    </template>

    <div class="panel searchPanel">
      <div class="searchRow">
        <div class="searchInputWrap">
          <span class="searchIcon">Q</span>
          <input v-model="query" class="searchInput" placeholder="Должность, навык или город" />
        </div>
        <button class="searchBtn" type="button">Найти</button>
      </div>

      <div class="filtersLine">
        <input v-model="filters.specialization" class="miniInput" placeholder="Специализация" />
        <input v-model="filters.city" class="miniInput" placeholder="Город" />
        <input v-model="filters.experience" class="miniInput" placeholder="Опыт" />
        <button class="ghostBtn" type="button" @click="clearAll">Очистить</button>
      </div>
    </div>

    <PlaceholderPanel
      badge="Новая страница"
      title="Здесь будет поиск резюме"
      description="Я добавил отдельную страницу для работодателя и сделал доступ к ней только после входа с ролью работодателя или администратора. Дальше сюда можно подключить API, фильтры и список найденных резюме."
    />
  </DashboardShell>
</template>

<script setup>
import { reactive, ref } from "vue";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import PlaceholderPanel from "../components/layouts/PlaceholderPanel.vue";
import UiCard from "../components/ui/UiCard.vue";

const navItems = [
  { to: "/employer/resumes", label: "Поиск резюме" },
  { to: "/employer/applications", label: "Отклики" },
  { to: "/employer/vacancies/create", label: "Создать вакансию" },
  { to: "/profile", label: "Профиль" },
];

const query = ref("");
const filters = reactive({
  specialization: "",
  city: "",
  experience: "",
});

function clearAll() {
  query.value = "";
  filters.specialization = "";
  filters.city = "";
  filters.experience = "";
}
</script>

<style scoped>
.panel {
  padding: 18px;
  border-radius: 24px;
  background: rgba(15, 16, 22, 0.94);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.searchPanel {
  display: grid;
  gap: 12px;
}

.searchRow {
  display: grid;
  grid-template-columns: 1fr 120px;
  gap: 10px;
}

.searchInputWrap {
  height: 46px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  border-radius: 14px;
  background: #0f1016;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.searchInput,
.miniInput {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  color: #eaeaf0;
  outline: none;
  font-size: 16px;
}

.searchIcon {
  opacity: 0.7;
  font-size: 14px;
}

.searchBtn,
.ghostBtn {
  height: 46px;
  border-radius: 14px;
  color: #fff;
  cursor: pointer;
}

.searchBtn {
  background: #2f73ff;
  border: 1px solid rgba(47, 115, 255, 0.5);
  font-weight: 800;
}

.filtersLine {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 140px;
  gap: 10px;
}

.miniInput {
  height: 42px;
  padding: 0 12px;
  border-radius: 12px;
  background: #0f1016;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.ghostBtn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.14);
}

@media (max-width: 980px) {
  .searchRow,
  .filtersLine {
    grid-template-columns: 1fr;
  }
}
</style>
