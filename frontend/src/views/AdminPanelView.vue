<template>
  <DashboardShell
    title="Панель администратора"
    subtitle="Просматривайте все сущности системы и блокируйте или удаляйте записи, которые нарушают правила или больше не нужны."
    role-label="Администратор"
    :nav-items="navItems"
    home-path="/home"
    avatar-letter="А"
  >
    <template #aside>
      <UiCard title="Вакансии" :subtitle="String(vacancies.length)" :active="activeTab === 'vacancies'" @click="activeTab = 'vacancies'" />
      <UiCard title="Пользователи" :subtitle="String(users.length)" :active="activeTab === 'users'" @click="activeTab = 'users'" />
      <UiCard title="Отклики" :subtitle="String(responses.length)" :active="activeTab === 'responses'" @click="activeTab = 'responses'" />
      <UiCard title="Резюме" :subtitle="String(resumes.length)" :active="activeTab === 'resumes'" @click="activeTab = 'resumes'" />
    </template>

    <InlineLoader v-if="loading" text="Загружаем данные панели..." />
    <p v-else-if="error" class="errorText">{{ error }}</p>

    <section v-else class="adminPanel">
      <header class="adminPanel__header">
        <div>
          <p class="eyebrow">Раздел</p>
          <h2>{{ activeTitle }}</h2>
        </div>
        <button class="ghostBtn" type="button" :disabled="reloading" @click="reloadAll">
          {{ reloading ? 'Обновляем...' : 'Обновить' }}
        </button>
      </header>

      <section v-if="activeTab === 'vacancies'" class="entityGrid">
        <article v-for="item in visibleVacancies" :key="item.uuid" class="entityCard">
          <div class="entityCard__top">
            <div>
              <p class="eyebrow">Вакансия</p>
              <h3>{{ item.title }}</h3>
            </div>
            <span class="statusChip">{{ item.status }}</span>
          </div>
          <p class="mutedText">{{ item.city || 'Город не указан' }} · {{ formatSalary(item.salary, item.currency) }}</p>
          <p class="bodyText">{{ shortText(item.description) }}</p>
          <div class="actionRow">
            <RouterLink class="ghostBtn" :to="`/vacancies/${item.uuid}`">Открыть</RouterLink>
            <button class="dangerBtn" type="button" @click="deleteVacancy(item.uuid)">Удалить</button>
          </div>
        </article>
      </section>

      <template v-else-if="activeTab === 'users'">
        <section class="filterPanel">
          <label class="searchField">
            <span class="eyebrow">Поиск пользователей</span>
            <input v-model.trim="userSearchQuery" class="searchInput" type="text" placeholder="Имя или username" />
          </label>
        </section>

        <section class="entityGrid">
          <article v-for="item in visibleUsers" :key="item.uuid" class="entityCard">
            <div class="entityCard__top">
              <div>
                <p class="eyebrow">Пользователь</p>
                <h3>{{ item.fio || item.username }}</h3>
              </div>
              <span class="statusChip">{{ item.role }}</span>
            </div>
            <p class="mutedText">@{{ item.username }}</p>
            <p class="bodyText">{{ item.email }}</p>
            <p class="mutedText">Статус: {{ item.status }}</p>
            <div class="actionRow">
              <RouterLink class="ghostBtn" :to="`/admin/users/${item.uuid}`">Профиль</RouterLink>
              <button
                class="dangerBtn"
                type="button"
                :disabled="item.uuid === currentUserUuid"
                @click="toggleUserBan(item)"
              >
                {{ userActionLabel(item) }}
              </button>
            </div>
          </article>
        </section>
      </template>

      <section v-else-if="activeTab === 'responses'" class="entityGrid">
        <article v-for="item in visibleResponses" :key="item.uuid" class="entityCard">
          <div class="entityCard__top">
            <div>
              <p class="eyebrow">Отклик</p>
              <h3>{{ responseTitle(item) }}</h3>
            </div>
            <span class="statusChip">{{ item.status }}</span>
          </div>
          <p class="bodyText">{{ item.message }}</p>
          <p v-if="item.employer_comment" class="mutedText">Комментарий работодателя: {{ item.employer_comment }}</p>
          <div class="actionRow actionRow--triple">
            <RouterLink class="ghostBtn" :to="`/vacancies/${item.vacancy_id}`">Вакансия</RouterLink>
            <RouterLink class="ghostBtn" :to="`/resumes/${item.resume_id}`">Резюме</RouterLink>
            <button class="dangerBtn" type="button" @click="deleteResponse(item.uuid)">Удалить</button>
          </div>
        </article>
      </section>

      <section v-else class="entityGrid">
        <article v-for="item in visibleResumes" :key="item.uuid" class="entityCard">
          <div class="entityCard__top">
            <div>
              <p class="eyebrow">Резюме</p>
              <h3>{{ item.title }}</h3>
            </div>
            <span class="statusChip">{{ item.currency || 'RUB' }}</span>
          </div>
          <p class="mutedText">{{ formatSalary(item.salary, item.currency) }}</p>
          <p class="bodyText">{{ item.about_me || 'Описание отсутствует.' }}</p>
          <div class="actionRow">
            <RouterLink class="ghostBtn" :to="`/resumes/${item.uuid}`">Открыть</RouterLink>
            <button class="dangerBtn" type="button" @click="deleteResume(item.uuid)">Удалить</button>
          </div>
        </article>
      </section>

      <div v-if="activeItems.length > visibleItems.length" ref="loadMoreTrigger" class="loadMoreTrigger" aria-hidden="true"></div>

      <section v-if="!activeItems.length" class="emptyState">
        <p class="eyebrow">Пусто</p>
        <h3>{{ emptyTitle }}</h3>
      </section>
    </section>
  </DashboardShell>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import UiCard from "../components/ui/UiCard.vue";
import { responsesApi } from "../api/responses";
import { resumeApi } from "../api/resume";
import { usersApi } from "../api/users";
import { vacanciesApi } from "../api/vacancies";

const BATCH_SIZE = 12;

const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/vacancies", label: "Поиск вакансий" },
  { to: "/candidate/applications", label: "Мои отклики" },
  { to: "/candidate/resume", label: "Мои резюме" },
  { to: "/admin", label: "Панель администратора" },
  { to: "/profile", label: "Профиль" },
];

const activeTab = ref("vacancies");
const loading = ref(true);
const reloading = ref(false);
const error = ref("");
const currentUserUuid = ref("");
const vacancies = ref([]);
const users = ref([]);
const responses = ref([]);
const resumes = ref([]);
const userSearchQuery = ref("");
const visibleCount = ref(BATCH_SIZE);
const loadMoreTrigger = ref(null);

let observer = null;

const filteredUsers = computed(() => {
  const query = userSearchQuery.value.trim().toLowerCase();
  if (!query) return users.value;

  return users.value.filter((item) => {
    const fio = String(item.fio || "").toLowerCase();
    const username = String(item.username || "").toLowerCase();
    return fio.includes(query) || username.includes(query);
  });
});

const activeTitle = computed(() => ({
  vacancies: "Все вакансии",
  users: "Все пользователи",
  responses: "Все отклики",
  resumes: "Все резюме",
}[activeTab.value] || "Панель администратора"));

const activeItems = computed(() => ({
  vacancies: vacancies.value,
  users: filteredUsers.value,
  responses: responses.value,
  resumes: resumes.value,
}[activeTab.value] || []));

const visibleItems = computed(() => activeItems.value.slice(0, visibleCount.value));
const visibleVacancies = computed(() => activeTab.value === "vacancies" ? visibleItems.value : []);
const visibleUsers = computed(() => activeTab.value === "users" ? visibleItems.value : []);
const visibleResponses = computed(() => activeTab.value === "responses" ? visibleItems.value : []);
const visibleResumes = computed(() => activeTab.value === "resumes" ? visibleItems.value : []);

const emptyTitle = computed(() => {
  if (activeTab.value === "users" && userSearchQuery.value.trim()) {
    return "По вашему запросу пользователи не найдены";
  }
  return "В этом разделе пока нет записей";
});

function formatSalary(salary, currency) {
  if (!salary && salary !== 0) return "Зарплата не указана";
  return `${Number(salary).toLocaleString("ru-RU")} ${currency || "RUB"}`;
}

function shortText(value, limit = 220) {
  if (!value) return "Описание отсутствует.";
  const normalized = String(value).replace(/\s+/g, " ").trim();
  return normalized.length > limit ? `${normalized.slice(0, limit)}...` : normalized;
}

function responseTitle(item) {
  return `Отклик ${item.uuid.slice(0, 8)}`;
}

function userActionLabel(item) {
  if (item.uuid === currentUserUuid.value) return "Текущий пользователь";
  return item.status === "BANNED" ? "Разбанить" : "Забанить";
}

function pickFulfilledArray(result) {
  return result.status === "fulfilled" && Array.isArray(result.value) ? result.value : [];
}

function isNotFoundResult(result) {
  return result.status === "rejected" && result.reason?.response?.status === 404;
}

function resetVisibleCount() {
  visibleCount.value = BATCH_SIZE;
}

function loadNextBatch() {
  if (visibleCount.value >= activeItems.value.length) return;
  visibleCount.value += BATCH_SIZE;
}

async function syncObserver() {
  await nextTick();

  if (observer) {
    observer.disconnect();
  }

  if (!loadMoreTrigger.value || activeItems.value.length <= visibleItems.value.length) {
    return;
  }

  observer = new IntersectionObserver((entries) => {
    if (entries.some((entry) => entry.isIntersecting)) {
      loadNextBatch();
    }
  }, {
    root: null,
    rootMargin: "240px 0px",
    threshold: 0,
  });

  observer.observe(loadMoreTrigger.value);
}

async function loadVacancies() {
  try {
    const data = await vacanciesApi.getAll({ include_archived: true });

    if (Array.isArray(data) && data.length > 0) {
      return data;
    }
  } catch (error) {
    if (error?.response?.status !== 404) {
      throw error;
    }
  }

  return await vacanciesApi.getAll();
}

async function loadUsers() {
  try {
    return await usersApi.getAll();
  } catch (error) {
    if (error?.response?.status === 422) {
      return await usersApi.getAll({ limit: 1000 });
    }
    throw error;
  }
}

async function loadResumes() {
  try {
    return await resumeApi.getAll();
  } catch (error) {
    if (error?.response?.status === 422) {
      return await resumeApi.getAll({ limit: 1000 });
    }
    throw error;
  }
}

async function loadAll() {
  const [meResult, vacanciesResult, usersResult, responsesResult, resumesResult] = await Promise.allSettled([
    usersApi.getMe(),
    loadVacancies(),
    loadUsers(),
    responsesApi.getAll(),
    loadResumes(),
  ]);

  currentUserUuid.value = meResult.status === "fulfilled" ? meResult.value?.uuid || "" : "";
  vacancies.value = pickFulfilledArray(vacanciesResult);
  users.value = pickFulfilledArray(usersResult);
  responses.value = pickFulfilledArray(responsesResult);
  resumes.value = pickFulfilledArray(resumesResult);

  const failed = [vacanciesResult, usersResult, responsesResult, resumesResult].filter((item) => item.status === "rejected");
  const onlyNotFound = failed.length > 0 && failed.every(isNotFoundResult);

  if (failed.length === 4 && !onlyNotFound) {
    throw new Error("all_failed");
  }
}

async function initialLoad() {
  loading.value = true;
  error.value = "";
  try {
    await loadAll();
    resetVisibleCount();
    await syncObserver();
  } catch {
    error.value = "Не удалось загрузить панель администратора.";
  } finally {
    loading.value = false;
  }
}

async function reloadAll() {
  reloading.value = true;
  error.value = "";
  try {
    await loadAll();
    resetVisibleCount();
    await syncObserver();
  } catch {
    error.value = "Не удалось обновить панель администратора.";
  } finally {
    reloading.value = false;
  }
}

async function deleteVacancy(uuid) {
  await vacanciesApi.delete(uuid);
  vacancies.value = vacancies.value.filter((item) => item.uuid !== uuid);
}

async function toggleUserBan(item) {
  if (item.uuid === currentUserUuid.value) return;

  if (item.status === "BANNED") {
    await usersApi.unban(item.uuid);
    users.value = users.value.map((user) => (
      user.uuid === item.uuid ? { ...user, status: "ACTIVE" } : user
    ));
    return;
  }

  await usersApi.delete(item.uuid);
  users.value = users.value.map((user) => (
    user.uuid === item.uuid ? { ...user, status: "BANNED" } : user
  ));
}

async function deleteResponse(uuid) {
  await responsesApi.delete(uuid);
  responses.value = responses.value.filter((item) => item.uuid !== uuid);
}

async function deleteResume(uuid) {
  await resumeApi.delete(uuid);
  resumes.value = resumes.value.filter((item) => item.uuid !== uuid);
}

watch(activeTab, async () => {
  resetVisibleCount();
  await syncObserver();
});

watch(userSearchQuery, async () => {
  if (activeTab.value !== "users") return;
  resetVisibleCount();
  await syncObserver();
});

watch(activeItems, async () => {
  if (visibleCount.value > activeItems.value.length && activeItems.value.length > 0) {
    visibleCount.value = Math.max(BATCH_SIZE, activeItems.value.length);
  }
  await syncObserver();
});

onMounted(async () => {
  await initialLoad();
  await syncObserver();
});

onBeforeUnmount(() => {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
});
</script>

<style scoped>
.adminPanel { display: grid; gap: 16px; }
.adminPanel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 20px 22px;
  border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.08);
  background: linear-gradient(180deg, rgba(18,19,27,0.96), rgba(11,12,17,0.98));
}
.filterPanel {
  display: grid;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.08);
  background: linear-gradient(180deg, rgba(18,19,27,0.96), rgba(11,12,17,0.98));
}
.searchField {
  display: grid;
  gap: 8px;
}
.searchInput {
  min-height: 46px;
  border-radius: 16px;
  padding: 0 16px;
  background: rgba(8,10,16,0.96);
  border: 1px solid rgba(255,255,255,0.08);
  color: #eef2ff;
  outline: none;
}
.searchInput:focus {
  border-color: rgba(47,115,255,0.5);
  box-shadow: 0 0 0 4px rgba(47,115,255,0.12);
}
.entityGrid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.entityCard,
.emptyState {
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.08);
  background: linear-gradient(180deg, rgba(18,19,27,0.96), rgba(11,12,17,0.98));
  box-shadow: 0 18px 44px rgba(0,0,0,0.24);
}
.entityCard { display: grid; gap: 12px; }
.entityCard__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.eyebrow {
  margin: 0;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}
.h3,
.entityCard h3,
.adminPanel__header h2,
.emptyState h3 { margin: 6px 0 0; }
.bodyText,
.mutedText {
  margin: 0;
  line-height: 1.65;
}
.mutedText { color: rgba(255,255,255,0.68); }
.actionRow {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.actionRow--triple { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.ghostBtn,
.dangerBtn,
.statusChip {
  min-height: 42px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-weight: 700;
}
.ghostBtn {
  padding: 0 14px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.03);
  color: #fff;
}
.dangerBtn {
  padding: 0 14px;
  border: 1px solid rgba(255,113,113,0.32);
  background: rgba(255,113,113,0.12);
  color: #ffb0b0;
  cursor: pointer;
}
.dangerBtn:disabled { opacity: 0.6; cursor: not-allowed; }
.statusChip {
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(47,115,255,0.24);
  background: rgba(47,115,255,0.12);
  color: #cfe0ff;
  font-size: 12px;
}
.loadMoreTrigger {
  width: 100%;
  height: 1px;
}
.errorText { color: #ff9090; }
@media (max-width: 980px) {
  .entityGrid { grid-template-columns: 1fr; }
}
@media (max-width: 680px) {
  .adminPanel__header,
  .entityCard__top { flex-direction: column; align-items: flex-start; }
  .actionRow,
  .actionRow--triple { grid-template-columns: 1fr; }
}
</style>


