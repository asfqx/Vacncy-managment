<template>
  <DashboardShell
    title="Поиск вакансий"
    subtitle="Кандидату доступны поиск вакансий, история откликов, управление резюме и профиль."
    role-label="Кандидат"
    :nav-items="navItems"
    :primary-action="{ to: '/candidate/resume', label: 'Создать резюме' }"
    :secondary-action="secondaryAction"
    home-path="/home"
    avatar-letter="К"
  >
    <div class="searchPanel">
      <div class="searchRow">
        <div class="searchInputWrap">
          <span class="searchIcon">Q</span>
          <input
            v-model="query"
            class="searchInput"
            placeholder="Профессия, должность или компания"
            @keydown.enter.prevent="onSearch"
          />
        </div>
        <button class="searchBtn" type="button" :disabled="loading" @click="onSearch">Найти</button>
      </div>

      <div class="filtersLine">
        <input v-model="filters.city" class="miniInput" placeholder="Город" />

        <div class="workFormat">
          <button class="formatBtn" :class="{ active: filters.remote === null }" type="button" @click="filters.remote = null">Любой</button>
          <button class="formatBtn" :class="{ active: filters.remote === true }" type="button" @click="filters.remote = true">Удаленно</button>
          <button class="formatBtn" :class="{ active: filters.remote === false }" type="button" @click="filters.remote = false">Офис</button>
        </div>

        <input v-model="filters.salary_from" class="miniInput" inputmode="numeric" placeholder="З/п от" />
        <input v-model="filters.salary_to" class="miniInput" inputmode="numeric" placeholder="З/п до" />

        <button class="ghostBtn" type="button" :disabled="loading" @click="clearAll">Сбросить</button>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <InlineLoader v-else-if="loading" text="Загружаем вакансии..." />

    <div v-if="!loading" class="list">
      <VacancyCardHH v-for="vacancy in items" :key="vacancy.uuid" :vacancy="vacancy" />

      <InlineLoader v-if="loadingMore" text="Подгружаем еще..." />
      <InfiniteSentinel v-if="hasMore" :disabled="loadingMore || loading" :on-reach="loadMore" />

      <p v-if="isEmpty" class="muted center">Ничего не найдено</p>
      <p v-else-if="!hasMore && items.length" class="muted center">Это все вакансии</p>
    </div>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted } from "vue";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import InfiniteSentinel from "../components/ui/InfiniteSentinel.vue";
import VacancyCardHH from "../components/vacancies/VacancyCard.vue";
import { useVacancies } from "../composables/useVacancies";
import { getUserRoleFromToken, isAdminRole } from "../utils/auth";

const role = getUserRoleFromToken();
const secondaryAction = computed(() => (
  isAdminRole(role) ? { to: "/employer/vacancies", label: "Страница компании" } : null
));

const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/vacancies", label: "Поиск вакансий" },
  { to: "/candidate/applications", label: "Мои отклики" },
  { to: "/candidate/resume", label: "Мои резюме" },
  { to: "/profile", label: "Профиль" },
];

const { items, loading, loadingMore, error, query, filters, hasMore, isEmpty, loadFirst, loadMore, reset } = useVacancies();

async function onSearch() {
  await loadFirst();
}

function clearAll() {
  query.value = "";
  filters.city = "";
  filters.remote = null;
  filters.salary_from = "";
  filters.salary_to = "";
  filters.company_id = "";
  reset();
  loadFirst();
}

onMounted(loadFirst);
</script>

<style scoped>
.searchPanel,
.list { display: grid; gap: 12px; }
.searchPanel { padding: 18px; border-radius: 24px; background: rgba(15,16,22,0.94); border: 1px solid rgba(255,255,255,0.1); }
.searchRow { display: grid; grid-template-columns: 1fr 120px; gap: 10px; align-items: center; }
.searchInputWrap { height: 46px; display: flex; align-items: center; gap: 8px; padding: 0 12px; border-radius: 14px; background: #0f1016; border: 1px solid rgba(255,255,255,0.1); }
.searchIcon { opacity: 0.7; font-size: 14px; }
.searchInput { width: 100%; height: 100%; border: none; background: transparent; color: #eaeaf0; outline: none; font-size: 16px; }
.searchBtn { height: 46px; border-radius: 14px; background: #2f73ff; border: 1px solid rgba(47,115,255,0.5); color: #fff; font-weight: 800; cursor: pointer; }
.searchBtn:disabled, .ghostBtn:disabled { opacity: 0.65; cursor: not-allowed; }
.filtersLine { display: grid; grid-template-columns: 1fr 1fr 0.9fr 0.9fr auto; gap: 10px; align-items: center; }
.miniInput { height: 40px; border-radius: 12px; padding: 0 12px; background: #0f1016; border: 1px solid rgba(255,255,255,0.1); color: #eaeaf0; outline: none; }
.workFormat { display: flex; gap: 6px; padding: 4px; border-radius: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); }
.formatBtn { height: 32px; padding: 0 12px; border-radius: 8px; border: none; background: transparent; color: rgba(255,255,255,0.75); font-weight: 600; cursor: pointer; }
.formatBtn.active { background: #2f73ff; color: #fff; }
.ghostBtn { height: 40px; border-radius: 12px; padding: 0 12px; background: transparent; border: 1px solid rgba(255,255,255,0.14); color: rgba(255,255,255,0.9); font-weight: 700; cursor: pointer; }
.error { color: #ff6b6b; font-size: 15px; margin: 0; }
.muted { opacity: 0.75; font-size: 15px; margin: 2px 0 0; }
.center { text-align: center; padding: 8px 0; }
@media (max-width: 980px) { .searchRow, .filtersLine { grid-template-columns: 1fr; } .workFormat { flex-wrap: wrap; } }
</style>
