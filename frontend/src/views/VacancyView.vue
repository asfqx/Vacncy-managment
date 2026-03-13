<template>
  <div class="page">
    <div class="pageGlow pageGlow--blue"></div>
    <div class="pageGlow pageGlow--coral"></div>

    <header class="header">
      <button class="ghost" type="button" @click="goBack">Назад</button>
    </header>

    <InlineLoader v-if="loading" text="Загружаем вакансию..." />
    <p v-else-if="error" class="error">{{ error }}</p>

    <div v-else class="layout">
      <div class="left">
        <section class="panel vacancyHeader">
          <p class="eyebrow">Вакансия</p>
          <h1 class="title">{{ vacancy.title }}</h1>

          <div class="row">
            <span class="badge" :class="{ remote: vacancy.remote }">
              {{ vacancy.remote ? "Удаленно" : "Офис / гибрид" }}
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

          <div class="actionRow">
            <button v-if="canApply" class="applyBtn">Откликнуться</button>
            <p class="muted small">Обновлено: {{ formatDate(vacancy.updated_at) }}</p>
          </div>
        </section>

        <section class="panel">
          <p class="eyebrow">Описание</p>
          <h2 class="h2">Что предстоит делать</h2>
          <p class="text">
            {{ vacancy.description || "Описание отсутствует." }}
          </p>
        </section>
      </div>

      <aside class="right">
        <section class="panel companyPanel">
          <p class="eyebrow">Компания</p>
          <h2 class="h2">Кто нанимает</h2>

          <InlineLoader v-if="companyLoading" text="Загружаем компанию..." />
          <p v-else-if="companyError" class="error">{{ companyError }}</p>

          <div v-else>
            <div class="companyHead">
              <img v-if="companyAvatarSrc" :src="companyAvatarSrc" alt="Аватар компании" class="companyAvatarImage" />
              <div v-else class="companyAvatarFallback">{{ companyAvatarLetter }}</div>
              <div class="companyTitleWrap">
                <div class="companyTitle">{{ company.title }}</div>
              </div>
            </div>

            <div class="companySite" v-if="company.website">
              <a class="link" :href="company.website" target="_blank" rel="noreferrer">
                {{ company.website }}
              </a>
            </div>

            <div class="muted small">
              Размер команды: {{ company.company_size ? `${company.company_size} сотрудников` : "не указан" }}
            </div>

            <div v-if="companyContactItems.length" class="contactList">
              <a
                v-for="item in companyContactItems"
                :key="item.label"
                class="contactItem"
                :href="item.href"
                :target="item.external ? '_blank' : undefined"
                :rel="item.external ? 'noreferrer' : undefined"
              >
                <span class="contactItem__label">{{ item.label }}</span>
                <strong class="contactItem__value">{{ item.value }}</strong>
              </a>
            </div>

            <div class="divider"></div>

            <div class="infoTile">
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
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import InlineLoader from "../components/ui/InlineLoader.vue";
import { vacanciesApi } from "../api/vacancies";
import { companyApi } from "../api/company";
import { getUserRoleFromToken, isCandidateRole } from "../utils/auth";

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const error = ref("");
const vacancy = ref(null);
const companyLoading = ref(false);
const companyError = ref("");
const company = ref(null);
const role = getUserRoleFromToken();
const canApply = computed(() => isCandidateRole(role));
const companyAvatarSrc = computed(() => buildAvatarUrl(company.value?.avatar_url));
const companyAvatarLetter = computed(() => String(company.value?.title || "К").trim().slice(0, 1).toUpperCase());
const companyContactItems = computed(() => {
  const items = [];

  if (company.value?.email) {
    items.push({
      label: "Email",
      value: company.value.email,
      href: `mailto:${company.value.email}`,
      external: false,
    });
  }

  if (company.value?.telegram) {
    items.push({
      label: "Telegram",
      value: formatTelegramLabel(company.value.telegram),
      href: normalizeTelegramLink(company.value.telegram),
      external: true,
    });
  }

  if (company.value?.phone_number) {
    items.push({
      label: "Телефон",
      value: company.value.phone_number,
      href: `tel:${company.value.phone_number}`,
      external: false,
    });
  }

  return items;
});

function buildAvatarUrl(objectName) {
  if (!objectName) return "";
  const baseUrl = (import.meta.env.VITE_S3_PUBLIC_BASE_URL || "http://localhost:9000").replace(/\/$/, "");
  const normalizedPath = String(objectName)
    .split("/")
    .map((part) => encodeURIComponent(part))
    .join("/");
  return `${baseUrl}/avatars/${normalizedPath}`;
}

function goBack() {
  router.back();
}

function formatSalary(salary, currency) {
  if (!salary) return "Зарплата не указана";
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

function normalizeTelegramLink(value) {
  const raw = String(value || "").trim();
  if (!raw) return "#";
  if (/^https?:\/\//i.test(raw)) return raw;
  const username = raw.replace(/^@/, "");
  return `https://t.me/${username}`;
}

function formatTelegramLabel(value) {
  const raw = String(value || "").trim();
  if (!raw) return "Telegram";
  if (/^https?:\/\//i.test(raw)) {
    const username = raw.split("t.me/")[1] || raw;
    return username.startsWith("@") ? username : `@${username.replace(/^@/, "")}`;
  }
  return raw.startsWith("@") ? raw : `@${raw}`;
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
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(47, 115, 255, 0.2), transparent 24%),
    radial-gradient(circle at top right, rgba(255, 122, 89, 0.14), transparent 20%),
    #0b0c10;
  color: #eaeaf0;
  padding: 18px 14px 32px;
}
.pageGlow {
  position: absolute;
  border-radius: 999px;
  filter: blur(80px);
  opacity: 0.32;
  pointer-events: none;
}
.pageGlow--blue {
  width: 260px;
  height: 260px;
  left: -60px;
  top: 20px;
  background: rgba(47, 115, 255, 0.28);
}
.pageGlow--coral {
  width: 220px;
  height: 220px;
  right: -40px;
  bottom: 30px;
  background: rgba(255, 122, 89, 0.18);
}
.header,
.layout {
  position: relative;
  z-index: 1;
  max-width: 1180px;
  margin: 0 auto;
}
.header { display: flex; justify-content: flex-start; margin-bottom: 14px; }
.ghost {
  min-height: 42px;
  border-radius: 14px;
  padding: 0 14px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.92);
  font-weight: 700;
  cursor: pointer;
}
.layout {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.8fr);
  gap: 18px;
  align-items: start;
}
.left { display: grid; gap: 16px; }
.right { position: sticky; top: 20px; }
.panel {
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 24px;
  padding: 22px;
  display: grid;
  gap: 12px;
  box-shadow: 0 18px 44px rgba(0,0,0,0.24);
}
.eyebrow {
  margin: 0;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}
.title { margin: 0; font-size: 34px; line-height: 1.08; }
.row,
.actionRow { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.salary { font-size: 26px; font-weight: 800; }
.badge {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(255,255,255,0.04);
}
.badge.remote { border-color: rgba(124,255,155,0.35); color: #9ff0b8; }
.meta { margin: 0; font-size: 15px; opacity: 0.82; display: flex; gap: 8px; align-items: center; }
.dot { opacity: 0.6; }
.h2 { margin: 0; font-size: 24px; }
.h3 { margin: 0; font-size: 16px; }
.text { margin: 0; font-size: 15px; line-height: 1.7; opacity: 0.92; white-space: pre-wrap; }
.companyHead { display: flex; align-items: center; gap: 14px; }
.companyAvatarImage,
.companyAvatarFallback {
  width: 56px;
  height: 56px;
  border-radius: 18px;
}
.companyAvatarImage { object-fit: cover; border: 1px solid rgba(255,255,255,0.12); }
.companyAvatarFallback {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #ff7a59, #2f73ff);
  color: #fff;
  font-size: 22px;
  font-weight: 800;
}
.companyTitleWrap { display: grid; gap: 4px; }
.companyTitle { font-weight: 800; font-size: 22px; }
.companySite { margin-top: 2px; }
.link { color: #9ac0ff; text-decoration: none; }
.link:hover { text-decoration: underline; }
.small { font-size: 14px; }
.muted { opacity: 0.68; }
.applyBtn {
  min-height: 46px;
  padding: 0 16px;
  border-radius: 16px;
  border: 1px solid rgba(47,115,255,0.38);
  background: linear-gradient(135deg, #2f73ff, #5a93ff);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 22px rgba(47,115,255,0.22);
}
.companyPanel { gap: 16px; }
.contactList {
  display: grid;
  gap: 10px;
  margin-top: 4px;
}
.contactItem {
  display: grid;
  gap: 4px;
  padding: 14px 16px;
  border-radius: 16px;
  text-decoration: none;
  color: #eaeaf0;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}
.contactItem:hover {
  transform: translateY(-1px);
  border-color: rgba(47,115,255,0.34);
  background: rgba(47,115,255,0.08);
}
.contactItem__label {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.56);
}
.contactItem__value {
  word-break: break-word;
}
.divider { height: 1px; background: rgba(255,255,255,0.08); margin: 6px 0 4px; }
.infoTile { padding: 4px 0 0; display: grid; gap: 10px; }
.error { color: #ff7d7d; font-size: 15px; margin: 0 auto; max-width: 1180px; position: relative; z-index: 1; }
@media (max-width: 920px) {
  .layout { grid-template-columns: 1fr; }
  .right { position: static; }
}
@media (max-width: 640px) {
  .row,
  .actionRow { flex-direction: column; align-items: flex-start; }
  .title { font-size: 28px; }
}
</style>
