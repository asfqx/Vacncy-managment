<template>
  <DashboardShell
    title="Мои вакансии"
    subtitle="Следите за опубликованными ролями, зарплатой и форматом работы вашей компании."
    role-label="Работодатель"
    :nav-items="navItems"
    :primary-action="{ to: '/employer/vacancies/create', label: 'Создать вакансию' }"
    :secondary-action="secondaryAction"
    home-path="/home"
    avatar-letter="В"
  >
    <template #aside>
      <UiCard title="Все вакансии" :subtitle="stats.total" :active="activeFilter === 'all'" @click="activeFilter = 'all'" />
      <UiCard title="Опубликовано" :subtitle="stats.published" :active="activeFilter === 'published'" @click="activeFilter = 'published'" />
      <UiCard title="Удаленно" :subtitle="stats.remote" :active="activeFilter === 'remote'" @click="activeFilter = 'remote'" />
    </template>

    <InlineLoader v-if="loading" text="Загружаем вакансии компании..." />
    <div v-else-if="error" class="errorPanel">{{ error }}</div>

    <template v-else>
      <section class="heroPanel panel">
        <div>
          <p class="eyebrow">Компания</p>
          <h2 class="heroTitle">{{ company?.title || "Мои вакансии" }}</h2>
          <p class="heroText">
            {{ filteredVacancies.length ? "Ниже собраны вакансии по выбранному фильтру." : emptyText }}
          </p>
        </div>
        <RouterLink class="heroAction" to="/employer/vacancies/create">Добавить вакансию</RouterLink>
      </section>

      <section v-if="filteredVacancies.length" class="listGrid">
        <article
          v-for="vacancy in filteredVacancies"
          :key="vacancy.uuid"
          class="vacancyCard"
          @click="openVacancy(vacancy.uuid)"
        >
          <div class="vacancyCard__top">
            <div>
              <p class="vacancyCard__eyebrow">{{ vacancy.status }}</p>
              <h3 class="vacancyCard__title">{{ vacancy.title }}</h3>
            </div>
            <span class="badge" :class="{ remote: vacancy.remote }">
              {{ vacancy.remote ? "Удаленно" : "Офис" }}
            </span>
          </div>

          <p class="vacancyCard__salary">{{ formatSalary(vacancy.salary, vacancy.currency) }}</p>
          <p class="vacancyCard__meta">{{ vacancy.city || "Город не указан" }}</p>
          <p class="vacancyCard__description">{{ short(vacancy.description) }}</p>

          <div class="vacancyCard__footer">
            <span>{{ formatDate(vacancy.updated_at) }}</span>
          </div>
        </article>
      </section>

      <section v-else class="emptyPanel panel">
        <p class="eyebrow">Пока пусто</p>
        <h3 class="emptyTitle">{{ emptyTitle }}</h3>
        <p class="heroText">{{ emptyText }}</p>
        <RouterLink class="heroAction" to="/employer/vacancies/create">Создать вакансию</RouterLink>
      </section>
    </template>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { companyApi } from "../api/company";
import { vacanciesApi } from "../api/vacancies";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import UiCard from "../components/ui/UiCard.vue";
import { getUserRoleFromToken, isAdminRole } from "../utils/auth";

const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/employer/resumes", label: "Поиск резюме" },
  { to: "/employer/vacancies", label: "Мои вакансии" },
  { to: "/employer/applications", label: "Отклики" },
  { to: "/employer/vacancies/create", label: "Создать вакансию" },
  { to: "/profile", label: "Профиль" },
];

const router = useRouter();
const role = getUserRoleFromToken();
const secondaryAction = computed(() => (
  isAdminRole(role) ? { to: "/vacancies", label: "Страница кандидата" } : null
));

const loading = ref(true);
const error = ref("");
const company = ref(null);
const vacancies = ref([]);
const activeFilter = ref("all");

function isPublishedVacancy(item) {
  return String(item.status).toLowerCase() === "active" && !item.remote;
}

function isRemoteVacancy(item) {
  return Boolean(item.remote);
}

const stats = computed(() => ({
  total: String(vacancies.value.filter((item) => isPublishedVacancy(item) || isRemoteVacancy(item)).length),
  published: String(vacancies.value.filter((item) => isPublishedVacancy(item)).length),
  remote: String(vacancies.value.filter((item) => isRemoteVacancy(item)).length),
}));

const filteredVacancies = computed(() => {
  if (activeFilter.value === "remote") return vacancies.value.filter((item) => isRemoteVacancy(item));
  if (activeFilter.value === "published") return vacancies.value.filter((item) => isPublishedVacancy(item));
  return vacancies.value.filter((item) => isPublishedVacancy(item) || isRemoteVacancy(item));
});

const emptyTitle = computed(() => {
  if (activeFilter.value === "remote") return "Удаленных вакансий пока нет";
  if (activeFilter.value === "published") return "Опубликованных вакансий пока нет";
  return "У вас еще нет вакансий";
});

const emptyText = computed(() => {
  if (activeFilter.value === "remote") return "Добавьте удаленный формат работы, и такие вакансии появятся в этом списке.";
  if (activeFilter.value === "published") return "Когда у компании появятся активные вакансии, вы увидите их здесь.";
  return "Создайте первую вакансию и сразу увидите ее в этом списке.";
});

function openVacancy(uuid) {
  router.push(`/vacancies/${uuid}`);
}

function short(text) {
  if (!text) return "Описание пока не заполнено.";
  const normalized = String(text).replace(/\s+/g, " ").trim();
  return normalized.length > 220 ? `${normalized.slice(0, 220)}...` : normalized;
}

function formatSalary(salary, currency) {
  if (!salary && salary !== 0) return "Зарплата не указана";
  return `${salary.toLocaleString("ru-RU")} ${currency || "RUB"}`;
}

function formatDate(value) {
  try {
    return `Обновлено ${new Date(value).toLocaleString("ru-RU")}`;
  } catch {
    return value;
  }
}

async function loadVacancies() {
  loading.value = true;
  error.value = "";

  try {
    const myCompany = await companyApi.getMine();
    company.value = myCompany;
    vacancies.value = await vacanciesApi.getAll({ company_id: myCompany.uuid, limit: 50 });
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) {
      const detail = e?.response?.data?.detail;
      if (typeof detail === "string" && detail.includes("Компания")) {
        error.value = "Сначала создайте компанию, чтобы работать с вакансиями.";
      } else {
        vacancies.value = [];
      }
    } else if (status === 401) {
      error.value = "Сессия истекла. Войдите снова.";
    } else {
      error.value = "Не удалось загрузить вакансии компании.";
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadVacancies);
</script>

<style scoped>
.panel,
.errorPanel,
.vacancyCard {
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}
.heroPanel,
.emptyPanel {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
}
.eyebrow,
.vacancyCard__eyebrow {
  margin: 0 0 8px;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}
.heroTitle,
.emptyTitle {
  margin: 0;
  font-size: 30px;
  line-height: 1.1;
}
.heroText {
  margin: 12px 0 0;
  max-width: 52ch;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.65;
}
.heroAction {
  min-height: 46px;
  padding: 0 18px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #fff;
  font-weight: 700;
  border: 1px solid rgba(47, 115, 255, 0.4);
  background: linear-gradient(135deg, #2f73ff, #5a93ff);
  box-shadow: 0 10px 22px rgba(47, 115, 255, 0.24);
}
.listGrid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.vacancyCard {
  padding: 18px;
  display: grid;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease;
}
.vacancyCard:hover { transform: translateY(-2px); border-color: rgba(47, 115, 255, 0.24); }
.vacancyCard__top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.vacancyCard__title { margin: 0; font-size: 22px; line-height: 1.2; }
.badge {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.04);
}
.badge.remote { border-color: rgba(124, 255, 155, 0.35); color: #9ff0b8; }
.vacancyCard__salary { margin: 0; font-size: 24px; font-weight: 700; }
.vacancyCard__meta,
.vacancyCard__description,
.vacancyCard__footer { margin: 0; color: rgba(255, 255, 255, 0.7); line-height: 1.6; }
.vacancyCard__footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
  padding-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.errorPanel { padding: 18px; color: #ff9d9d; }
@media (max-width: 1080px) { .listGrid { grid-template-columns: 1fr; } }
@media (max-width: 780px) {
  .heroPanel,
  .emptyPanel,
  .vacancyCard__top { flex-direction: column; align-items: flex-start; }
  .vacancyCard__footer { flex-direction: column; }
}
</style>