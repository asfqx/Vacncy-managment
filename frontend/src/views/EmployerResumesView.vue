<template>
  <DashboardShell
    title="Поиск резюме"
    subtitle="Используйте поиск, фильтры и рекомендации, чтобы быстрее находить подходящих кандидатов."
    role-label="Работодатель"
    :nav-items="navItems"
    :primary-action="{ to: '/employer/vacancies/create', label: 'Создать вакансию' }"
    :secondary-action="secondaryAction"
    home-path="/home"
    avatar-letter="Р"
  >
    <div class="panel searchPanel">
      <div class="searchRow">
        <div class="searchInputWrap">
          <span class="searchIcon">Q</span>
          <input
            v-model="query"
            class="searchInput"
            placeholder="Должность, ключевые навыки или профессия"
            @keydown.enter.prevent="loadFirst"
          />
        </div>
        <button class="searchBtn" type="button" :disabled="loading" @click="loadFirst">Найти</button>
      </div>

      <div class="filtersGrid">
        <label class="field">
          <span>Пол</span>
          <AppSelect v-model="filters.gender" :options="genderOptions" />
        </label>

        <label class="field">
          <span>Образование</span>
          <AppSelect v-model="filters.education_level" :options="educationLevelOptions" />
        </label>

        <label class="field">
          <span>Зарплата от</span>
          <input v-model.number="filters.salary_from" class="miniInput" type="number" min="0" placeholder="120000" />
        </label>

        <label class="field">
          <span>Зарплата до</span>
          <input v-model.number="filters.salary_to" class="miniInput" type="number" min="0" placeholder="250000" />
        </label>

        <label class="field">
          <span>Дата рождения от</span>
          <AppDateInput v-model="filters.birth_date_from" />
        </label>

        <label class="field">
          <span>Дата рождения до</span>
          <AppDateInput v-model="filters.birth_date_to" />
        </label>
      </div>

      <div class="toolbar">
        <button class="ghostBtn" type="button" :disabled="loading" @click="clearAll">Сбросить фильтры</button>
      </div>
    </div>

    <p v-if="error" class="errorText">{{ error }}</p>
    <InlineLoader v-else-if="loading" text="Загружаем резюме..." />

    <section v-if="!loading" class="resultsGrid">
      <ResumeCard v-for="resume in items" :key="resume.uuid" :resume="resume" />

      <InlineLoader v-if="loadingMore" class="listState" text="Подгружаем еще резюме..." />
      <InfiniteSentinel v-if="hasMore" :disabled="loading || loadingMore" :on-reach="loadMore" />

      <p v-if="!items.length && !error" class="listState">Резюме не найдены</p>
      <p v-else-if="!hasMore && items.length" class="listState">Вы просмотрели все найденные резюме</p>
    </section>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import ResumeCard from "../components/resumes/ResumeCard.vue";
import AppDateInput from "../components/ui/AppDateInput.vue";
import AppSelect from "../components/ui/AppSelect.vue";
import InfiniteSentinel from "../components/ui/InfiniteSentinel.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import { resumeApi } from "../api/resume";
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

const genderOptions = [
  { value: "", label: "Любой" },
  { value: "MALE", label: "Мужчина" },
  { value: "FEMALE", label: "Женщина" },
];

const educationLevelOptions = [
  { value: "", label: "Любое" },
  { value: "SECONDARY", label: "Среднее" },
  { value: "SECONDARY_SPECIAL", label: "Среднее специальное" },
  { value: "INCOMPLETE_HIGHER", label: "Неоконченное высшее" },
  { value: "BACHELOR", label: "Бакалавр" },
  { value: "SPECIALIST", label: "Специалист" },
  { value: "MASTER", label: "Магистр" },
  { value: "POSTGRADUATE", label: "Аспирантура" },
  { value: "DOCTORATE", label: "Докторантура" },
];

const loading = ref(true);
const loadingMore = ref(false);
const error = ref("");
const items = ref([]);
const query = ref("");
const mode = ref("recommendation");
const cursor = ref(null);
const cursorUuid = ref(null);
const hasMore = ref(true);
const limit = 12;

const filters = reactive({
  gender: "",
  education_level: "",
  salary_from: null,
  salary_to: null,
  birth_date_from: "",
  birth_date_to: "",
});

const hasActiveFilters = computed(() => Boolean(
  filters.gender ||
  filters.education_level ||
  filters.salary_from ||
  filters.salary_to ||
  filters.birth_date_from ||
  filters.birth_date_to
));

function buildParams({ cursorValue }) {
  return {
    gender: filters.gender || undefined,
    education_level: filters.education_level || undefined,
    salary_from: Number.isFinite(filters.salary_from) ? filters.salary_from : undefined,
    salary_to: Number.isFinite(filters.salary_to) ? filters.salary_to : undefined,
    birth_date_from: filters.birth_date_from || undefined,
    birth_date_to: filters.birth_date_to || undefined,
    resume_title: query.value.trim() || undefined,
    cursor: cursorValue || undefined,
    cursor_uuid: cursorUuid.value || undefined,
    limit,
  };
}

function computeNextCursor(list) {
  if (!list?.length) return null;
  const last = list[list.length - 1];
  return { createdAt: last.created_at, uuid: last.uuid };
}

function resetState() {
  items.value = [];
  cursor.value = null;
  cursorUuid.value = null;
  hasMore.value = true;
  error.value = "";
}

async function loadFirst() {
  loading.value = true;
  loadingMore.value = false;
  resetState();

  try {
    const hasQuery = Boolean(query.value.trim());

    if (hasQuery) {
      mode.value = "search";
      items.value = (await resumeApi.search(buildParams({ cursorValue: null }))) || [];
    } else if (hasActiveFilters.value) {
      mode.value = "all";
      items.value = (await resumeApi.getAll(buildParams({ cursorValue: null }))) || [];
    } else {
      mode.value = "recommendation";
      try {
        items.value = (await resumeApi.getRecommendations({ limit })) || [];
      } catch (e) {
        if (e?.response?.status !== 404) throw e;
        mode.value = "all";
        items.value = (await resumeApi.getAll(buildParams({ cursorValue: null }))) || [];
      }
    }

    const next = computeNextCursor(items.value);
    cursor.value = next?.createdAt || null;
    cursorUuid.value = next?.uuid || null;
    hasMore.value = Boolean(cursor.value && cursorUuid.value && items.value.length >= limit);
  } catch (e) {
    if (e?.response?.status === 404) error.value = "Резюме не найдены.";
    else error.value = "Не удалось загрузить резюме.";
    hasMore.value = false;
  } finally {
    loading.value = false;
  }
}

async function loadMore() {
  if (loading.value || loadingMore.value || !hasMore.value) return;

  loadingMore.value = true;
  error.value = "";

  try {
    let batch = [];

    if (mode.value === "search") batch = (await resumeApi.search(buildParams({ cursorValue: cursor.value }))) || [];
    else if (mode.value === "recommendation") batch = (await resumeApi.getRecommendations({ limit, cursor: cursor.value, cursor_uuid: cursorUuid.value })) || [];
    else batch = (await resumeApi.getAll(buildParams({ cursorValue: cursor.value }))) || [];

    if (!batch.length) {
      hasMore.value = false;
      return;
    }

    items.value = items.value.concat(batch);
    const next = computeNextCursor(batch);
    cursor.value = next?.createdAt || null;
    cursorUuid.value = next?.uuid || null;
    hasMore.value = Boolean(cursor.value && cursorUuid.value && batch.length >= limit);
  } catch {
    hasMore.value = false;
    error.value = "Не удалось подгрузить еще резюме.";
  } finally {
    loadingMore.value = false;
  }
}

function clearAll() {
  query.value = "";
  filters.gender = "";
  filters.education_level = "";
  filters.salary_from = null;
  filters.salary_to = null;
  filters.birth_date_from = "";
  filters.birth_date_to = "";
  loadFirst();
}

onMounted(loadFirst);
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

.searchBtn:disabled,
.ghostBtn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.filtersGrid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.field {
  display: grid;
  gap: 8px;
}

.field span {
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  font-weight: 600;
}

.miniInput {
  height: 52px;
  padding: 0 12px;
  border-radius: 16px;
  background: #0f1016;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toolbar {
  display: flex;
  justify-content: flex-start;
}

.ghostBtn {
  min-width: 160px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.resultsGrid {
  display: grid;
  gap: 16px;
}

.listState {
  margin: 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.68);
}

.errorText {
  margin: 0;
  color: #ff9d9d;
}

@media (max-width: 980px) {
  .searchRow,
  .filtersGrid {
    grid-template-columns: 1fr;
  }
}
</style>
