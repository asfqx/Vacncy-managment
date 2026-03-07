<template>
  <div class="page">
    <header class="header">
      <button class="ghost" type="button" @click="goBack">← Назад</button>
    </header>

    <InlineLoader v-if="loading" text="Загружаем вакансию…" />
    <p v-else-if="error" class="error">{{ error }}</p>

    <div v-else class="layout">

      <!-- LEFT COLUMN -->
      <div class="left">

        <!-- VACANCY HEADER -->
        <section class="panel vacancyHeader">
          <h1 class="title">{{ vacancy.title }}</h1>

          <div class="row">
            <span class="badge" :class="{ remote: vacancy.remote }">
              {{ vacancy.remote ? "Удалённо" : "Офис" }}
            </span>

            <span class="salary">
              {{ formatSalary(vacancy.salary, vacancy.currency) }}
            </span>
          </div>

          <p class="meta">
            <span>{{ vacancy.city || "Город не указан" }}</span>
            <span class="dot">•</span>
            <span class="muted">Статус: {{ vacancy.status }}</span>
          </p>

          <button class="applyBtn">
            Откликнуться
          </button>

          <p class="muted small">
            Обновлено: {{ formatDate(vacancy.updated_at) }}
          </p>
        </section>

        <!-- VACANCY DESCRIPTION -->
        <section class="panel">
          <h2 class="h2">Описание вакансии</h2>

          <p class="text">
            {{ vacancy.description || "Описание отсутствует." }}
          </p>
        </section>

      </div>


      <!-- RIGHT COLUMN -->
      <aside class="right">

        <section class="panel companyPanel">

          <h2 class="h2">Компания</h2>

          <InlineLoader
            v-if="companyLoading"
            text="Загружаем компанию…"
          />

          <p v-else-if="companyError" class="error">
            {{ companyError }}
          </p>

          <div v-else>

            <div class="companyTitle">
              {{ company.title }}
            </div>

            <div class="companySite" v-if="company.website">
              <a
                class="link"
                :href="company.website"
                target="_blank"
                rel="noreferrer"
              >
                {{ company.website }}
              </a>
            </div>

            <div class="muted small">
              Размер:
              {{
                company.company_size
                  ? company.company_size + " сотрудников"
                  : "не указан"
              }}
            </div>

            <div class="divider"></div>

            <div class="block">
              <h3 class="h3">О компании</h3>
              <p class="text">
                {{ company.description || "Описание компании отсутствует." }}
              </p>
            </div>

          </div>

        </section>

      </aside>

    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import InlineLoader from "../components/ui/InlineLoader.vue";
import { vacanciesApi } from "../api/vacancies";
import { companyApi } from "../api/company";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref("");

const vacancy = ref(null);

const companyLoading = ref(false);
const companyError = ref("");
const company = ref(null);

function goBack() {
  router.back();
}

function formatSalary(salary, currency) {
  if (!salary) return "З/п не указана";
  const cur = currency || "RUB";
  return `${salary.toLocaleString("ru-RU")} ${cur}`;
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString("ru-RU");
  } catch {
    return iso;
  }
}

async function loadCompany(companyId) {
  companyLoading.value = true;
  companyError.value = "";

  try {
    company.value = await companyApi.getById(companyId);
  } catch (e) {
    const status = e?.response?.status;

    if (status === 404) companyError.value = "Компания не найдена";
    else companyError.value = "Не удалось загрузить данные компании";

    company.value = null;
  } finally {
    companyLoading.value = false;
  }
}

async function loadVacancy() {
  loading.value = true;
  error.value = "";
  vacancy.value = null;

  const uuid = route.params.uuid;

  try {
    const data = await vacanciesApi.getById(uuid);

    vacancy.value = data;

    if (data?.company_id) {
      await loadCompany(data.company_id);
    } else {
      company.value = {
        title: "Компания не указана",
        description: "",
        website: "",
        company_size: 0,
      };
    }

  } catch (e) {
    const status = e?.response?.status;

    if (status === 404) error.value = "Вакансия не найдена";
    else if (status === 401) error.value = "Вы не авторизованы";
    else error.value = "Не удалось загрузить вакансию";

  } finally {
    loading.value = false;
  }
}

onMounted(loadVacancy);
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #0b0c10;
  color: #eaeaf0;
  padding: 18px 14px 28px;
  max-width: 1180px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 12px;
}

.ghost {
  height: 40px;
  border-radius: 12px;
  padding: 0 12px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.9);
  font-weight: 700;
  cursor: pointer;
}

.layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  align-items: start;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
}

.left {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.right {
  position: sticky;
  top: 20px;
}

.panel {
  background: rgba(15, 16, 22, 0.92);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 16px;
  display: grid;
  gap: 10px;
}

.title {
  margin: 0;
  font-size: 24px;
  line-height: 1.2;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.salary {
  font-size: 22px;
  font-weight: 900;
}

.badge {
  font-size: 14px;
  padding: 5px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.16);
}

.badge.remote {
  border-color: rgba(124,255,155,0.35);
}

.meta {
  font-size: 15px;
  opacity: 0.8;
  display: flex;
  gap: 8px;
  align-items: center;
}

.dot {
  opacity: 0.6;
}

.block {
  margin-top: 6px;
  display: grid;
  gap: 6px;
}

.h2 {
  margin: 0;
  font-size: 20px;
}

.h3 {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.text {
  margin: 0;
  font-size: 15px;
  line-height: 1.55;
  opacity: 0.92;
  white-space: pre-wrap;
}

.companyTitle {
  font-weight: 900;
  font-size: 18px;
}

.companySite {
  margin-top: 4px;
}

.link {
  color: rgba(47,115,255,0.95);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.small {
  font-size: 14px;
}

.muted {
  opacity: 0.65;
}

.applyBtn {
  margin-top: 10px;
  height: 44px;
  border-radius: 12px;
  border: none;
  background: rgba(47,115,255,0.95);
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.applyBtn:hover {
  background: rgba(47,115,255,1);
}

.companyPanel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.divider {
  height: 1px;
  background: rgba(255,255,255,0.08);
  margin: 6px 0;
}

.error {
  color: #ff6b6b;
  font-size: 15px;
  margin: 0;
}
</style>