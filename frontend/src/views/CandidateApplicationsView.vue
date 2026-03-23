<template>
  <DashboardShell
    title="Мои отклики"
    subtitle="Следите за статусами откликов и быстро возвращайтесь к интересным вакансиям."
    role-label="Кандидат"
    :nav-items="navItems"
    :primary-action="{ to: '/candidate/resume', label: 'Мое резюме' }"
    :secondary-action="secondaryAction"
    home-path="/home"
    avatar-letter="К"
  >
    <template #aside>
      <UiCard title="На рассмотрении" :subtitle="String(stats.pending)" :active="activeFilter === 'pending'" @click="setFilter('pending')" />
      <UiCard title="Принято" :subtitle="String(stats.accepted)" :active="activeFilter === 'accepted'" @click="setFilter('accepted')" />
      <UiCard title="Отклонено" :subtitle="String(stats.rejected)" :active="activeFilter === 'rejected'" @click="setFilter('rejected')" />
    </template>

    <InlineLoader v-if="loading" text="Загружаем отклики..." />
    <p v-else-if="error" class="errorText">{{ error }}</p>
    <section v-else-if="!items.length" class="emptyState">
      <p class="eyebrow">Пусто</p>
      <h2>У вас пока нет откликов</h2>
      <p>Перейдите к вакансиям, откройте интересную позицию и отправьте сопроводительное письмо прямо из карточки вакансии.</p>
      <RouterLink class="primaryLink" to="/vacancies">Перейти к вакансиям</RouterLink>
    </section>

    <div v-else class="responseGrid">
      <article v-for="item in filteredItems" :key="item.uuid" class="responseCard">
        <div class="responseCard__top">
          <div>
            <p class="responseCard__label">{{ vacancyMap[item.vacancy_id]?.title || 'Вакансия' }}</p>
            <h3 class="responseCard__title">{{ vacancyTitle(item) }}</h3>
          </div>
          <span class="statusBadge" :class="statusClass(item.status)">{{ statusLabel(item.status) }}</span>
        </div>

        <div class="responseMetaRow">
          <span class="responseMetaChip">{{ vacancyMap[item.vacancy_id]?.city || 'Город не указан' }}</span>
          <span class="responseMetaChip responseMetaChip--salary">{{ formatSalary(vacancyMap[item.vacancy_id]?.salary, vacancyMap[item.vacancy_id]?.currency) }}</span>
        </div>

        <p class="responseCard__message">{{ item.message }}</p>

        <section v-if="item.employer_comment" class="commentPanel">
          <p class="responseCard__label">Сообщение от работодателя</p>
          <div class="commentCard">{{ item.employer_comment }}</div>
        </section>

        <section v-if="item.status === 'ACCEPTED' && acceptedContactItems(item).length" class="contactPanel">
          <p class="responseCard__label">Контакты компании</p>
          <div class="contactGrid">
            <component
              v-for="contact in acceptedContactItems(item)"
              :key="`${item.uuid}-${contact.label}`"
              :is="contact.clickable ? 'a' : 'div'"
              class="contactCard"
              :class="{ 'contactCard--clickable': contact.clickable }"
              :href="contact.clickable ? contact.href : undefined"
              :target="contact.clickable && contact.external ? '_blank' : undefined"
              :rel="contact.clickable && contact.external ? 'noreferrer' : undefined"
            >
              <span class="contactCard__label">{{ contact.label }}</span>
              <strong class="contactCard__value">{{ contact.value }}</strong>
            </component>
          </div>
        </section>

        <div class="responseCard__footer">
          <span>{{ formatDate(item.created_at) }}</span>
          <RouterLink class="ghostLink" :to="`/vacancies/${item.vacancy_id}`">Вакансия</RouterLink>
        </div>
      </article>
    </div>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { getUserRoleFromToken, isAdminRole } from "../utils/auth";
import { RouterLink } from "vue-router";
import { companyApi } from "../api/company";
import { responsesApi } from "../api/responses";
import { usersApi } from "../api/users";
import { vacanciesApi } from "../api/vacancies";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import UiCard from "../components/ui/UiCard.vue";

const role = getUserRoleFromToken();
const secondaryAction = computed(() => (isAdminRole(role) ? { to: "/employer/vacancies", label: "Страница компании" } : null));
const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/vacancies", label: "Поиск вакансий" },
  { to: "/candidate/applications", label: "Мои отклики" },
  { to: "/candidate/resume", label: "Мое резюме" },
  { to: "/profile", label: "Профиль" },
];

const loading = ref(true);
const error = ref("");
const items = ref([]);
const activeFilter = ref("all");
const vacancyMap = ref({});
const companyMap = ref({});
const companyUserMap = ref({});

const filteredItems = computed(() => {
  if (activeFilter.value === "pending") return items.value.filter((item) => item.status === "PENDING");
  if (activeFilter.value === "accepted") return items.value.filter((item) => item.status === "ACCEPTED");
  if (activeFilter.value === "rejected") return items.value.filter((item) => item.status === "REJECTED");
  return items.value;
});

const stats = computed(() => ({
  pending: items.value.filter((item) => item.status === "PENDING").length,
  accepted: items.value.filter((item) => item.status === "ACCEPTED").length,
  rejected: items.value.filter((item) => item.status === "REJECTED").length,
}));

function statusLabel(status) {
  return ({ PENDING: "На рассмотрении", ACCEPTED: "Принято", REJECTED: "Отклонено" })[status] || status;
}

function setFilter(filter) {
  activeFilter.value = filter;
}

function statusClass(status) {
  return {
    "status--pending": status === "PENDING",
    "status--accepted": status === "ACCEPTED",
    "status--rejected": status === "REJECTED",
  };
}

function vacancyTitle(item) {
  const vacancy = vacancyMap.value[item.vacancy_id];
  if (!vacancy?.title) return "Сопроводительное письмо";
  return `Отклик на ${vacancy.title}`;
}

function formatDate(value) {
  try {
    return new Date(value).toLocaleString("ru-RU");
  } catch {
    return value;
  }
}

function formatSalary(salary, currency) {
  if (!salary) return "Зарплата не указана";
  return `${Number(salary).toLocaleString("ru-RU")} ${currency || "RUB"}`;
}

function normalizeTelegramLink(value) {
  const raw = String(value || "").trim();
  if (!raw) return "#";
  if (/^https?:\/\//i.test(raw)) return raw;
  return `https://t.me/${raw.replace(/^@/, "")}`;
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

function acceptedContactItems(item) {
  if (item.status !== "ACCEPTED") return [];
  const vacancy = vacancyMap.value[item.vacancy_id];
  const company = companyMap.value[vacancy?.company_id];
  const profile = companyUserMap.value[company?.user_uuid];
  if (!profile) return [];

  const contacts = [];
  if (profile.email) {
    contacts.push({ label: "Email", value: profile.email, href: `mailto:${profile.email}`, external: false, clickable: false });
  }
  if (profile.telegram) {
    contacts.push({ label: "Telegram", value: formatTelegramLabel(profile.telegram), href: normalizeTelegramLink(profile.telegram), external: true, clickable: true });
  }
  if (profile.phone_number) {
    contacts.push({ label: "Телефон", value: profile.phone_number, href: `tel:${profile.phone_number}`, external: false, clickable: false });
  }
  return contacts;
}

async function hydrateVacancies(responses) {
  const ids = [...new Set(responses.map((item) => item.vacancy_id).filter(Boolean))];
  const entries = await Promise.all(
    ids.map(async (uuid) => {
      try {
        const vacancy = await vacanciesApi.getById(uuid);
        return [uuid, vacancy];
      } catch {
        return [uuid, null];
      }
    })
  );
  vacancyMap.value = Object.fromEntries(entries);
}

async function hydrateCompanies() {
  const companyIds = [...new Set(Object.values(vacancyMap.value).map((item) => item?.company_id).filter(Boolean))];
  const entries = await Promise.all(
    companyIds.map(async (uuid) => {
      try {
        const company = await companyApi.getById(uuid);
        return [uuid, company];
      } catch {
        return [uuid, null];
      }
    })
  );
  companyMap.value = Object.fromEntries(entries);
}

async function hydrateCompanyUsers() {
  const userIds = [...new Set(Object.values(companyMap.value).map((item) => item?.user_uuid).filter(Boolean))];
  const entries = await Promise.all(
    userIds.map(async (uuid) => {
      try {
        const user = await usersApi.getById(uuid);
        return [uuid, user];
      } catch {
        return [uuid, null];
      }
    })
  );
  companyUserMap.value = Object.fromEntries(entries);
}

async function loadResponses() {
  loading.value = true;
  error.value = "";

  try {
    const data = await responsesApi.getAll();
    items.value = Array.isArray(data) ? data : [];
    await hydrateVacancies(items.value);
    await hydrateCompanies();
    await hydrateCompanyUsers();
  } catch (e) {
    if (e?.response?.status === 404) {
      items.value = [];
      vacancyMap.value = {};
      companyMap.value = {};
      companyUserMap.value = {};
    } else {
      error.value = "Не удалось загрузить отклики.";
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadResponses);
</script>

<style scoped>
.responseGrid { display: grid; gap: 14px; }
.responseCard, .emptyState {
  border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.08);
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  box-shadow: 0 18px 44px rgba(0,0,0,0.24);
  padding: 22px;
}
.responseCard__top, .responseCard__footer { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.responseCard__footer { margin-top: 16px; }
.responseCard__label { margin: 0 0 6px; color: #8eb4ff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; }
.responseCard__title { margin: 0; font-size: 24px; }
.responseCard__meta, .responseCard__message { margin: 14px 0 0; color: rgba(255,255,255,0.72); line-height: 1.7; white-space: pre-wrap; }
.responseMetaRow { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
.responseMetaChip { display: inline-flex; align-items: center; min-height: 38px; padding: 0 14px; border-radius: 999px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.76); font-size: 14px; line-height: 1; }
.responseMetaChip--salary { background: linear-gradient(135deg, rgba(47,115,255,0.16), rgba(93,160,255,0.08)); border-color: rgba(47,115,255,0.24); color: #dbe8ff; font-weight: 700; }
.commentPanel, .contactPanel { margin-top: 16px; display: grid; gap: 10px; }
.commentCard {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.78);
  line-height: 1.7;
  white-space: pre-wrap;
}
.contactGrid { display: grid; gap: 10px; }
.contactGrid--primary { grid-template-columns: minmax(0, 1fr); }
.contactGrid--secondary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.contactCard {
  display: grid;
  gap: 10px;
  min-width: 0;
  padding: 14px 16px;
  border-radius: 18px;
  text-decoration: none;
  color: #eaeaf0;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(124,255,155,0.18);
}
.contactCard--primary {
  padding-right: 18px;
}
.contactCard__label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(255,255,255,0.55); }
.contactCard__value {
  display: block;
  margin-top: 2px;
  min-width: 0;
  font-size: clamp(0.72rem, 1.2vw, 0.95rem);
  line-height: 1.25;
  letter-spacing: -0.02em;
  white-space: nowrap;
}
.contactCard__value--email {
  font-size: clamp(0.78rem, 1.1vw, 1rem);
}
.contactCard--clickable { cursor: pointer; transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease; }
.contactCard--clickable:hover { transform: translateY(-1px); border-color: rgba(47,115,255,0.3); background: rgba(47,115,255,0.08); }
.statusBadge {
  min-height: 36px;
  padding: 0 12px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.12);
}
.status--pending { background: rgba(255,196,84,0.14); color: #ffd36f; }
.status--accepted { background: rgba(124,255,155,0.12); color: #9ff0b8; }
.status--rejected { background: rgba(255,113,113,0.12); color: #ffb0b0; }
.ghostLink, .primaryLink {
  text-decoration: none;
  border-radius: 14px;
  padding: 10px 14px;
  font-weight: 700;
}
.ghostLink { color: #fff; border: 1px solid rgba(255,255,255,0.14); }
.primaryLink { display: inline-flex; width: fit-content; margin-top: 10px; color: #fff; background: linear-gradient(135deg, #2f73ff, #5a93ff); }
.ghostLink--button { background: transparent; cursor: pointer; }
.errorText { color: #ff8e8e; }
.emptyState h2 { margin: 6px 0 0; font-size: 28px; }
.emptyState p { margin: 12px 0 0; color: rgba(255,255,255,0.72); line-height: 1.6; }
.eyebrow { margin: 0; color: #8eb4ff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; }
@media (max-width: 720px) { .responseCard__top, .responseCard__footer { flex-direction: column; align-items: flex-start; } .contactGrid--secondary { grid-template-columns: 1fr; } }
</style>











