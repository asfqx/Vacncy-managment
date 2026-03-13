<template>
  <DashboardShell
    title="Профиль пользователя"
    subtitle="Администратор может просматривать профиль пользователя, но не может изменять его данные с этой страницы."
    role-label="Администратор"
    :nav-items="navItems"
    :secondary-action="{ to: '/admin', label: 'К панели' }"
    home-path="/home"
    avatar-letter="А"
  >
    <InlineLoader v-if="loading" text="Загружаем профиль пользователя..." />
    <div v-else-if="error" class="errorPanel">{{ error }}</div>

    <template v-else>
      <section class="heroCard">
        <div class="heroCard__identity">
          <div class="heroCard__avatarWrap">
            <img v-if="avatarImageSrc" :src="avatarImageSrc" alt="Аватар" class="heroCard__avatarImage" />
            <div v-else class="heroCard__avatar">{{ avatarLetter }}</div>
          </div>

          <div>
            <p class="heroCard__role">{{ roleLabel }}</p>
            <h2 class="heroCard__name">{{ displayName }}</h2>
            <p class="heroCard__login">@{{ profile.username }}</p>
          </div>
        </div>

        <div class="heroCard__statusWrap">
          <span class="statusBadge" :class="{ success: profile.email_confirmed }">
            {{ profile.email_confirmed ? "Email подтвержден" : "Email не подтвержден" }}
          </span>
          <span class="statusBadge muted">Статус: {{ profile.status }}</span>
        </div>
      </section>

      <section class="contentGrid">
        <article class="panel detailsPanel">
          <div class="panelIntro">
            <div>
              <p class="panelEyebrow">Данные аккаунта</p>
              <h3 class="panel__title">Основная информация</h3>
            </div>
            <span class="readonlyChip">Только просмотр</span>
          </div>

          <dl class="details details--spacious">
            <div class="details__row">
              <dt>Email</dt>
              <dd>{{ profile.email || "Нет данных" }}</dd>
            </div>
            <div class="details__row">
              <dt>Username</dt>
              <dd>@{{ profile.username }}</dd>
            </div>
            <div class="details__row">
              <dt>ФИО</dt>
              <dd>{{ profile.fio || "Не указано" }}</dd>
            </div>
            <div class="details__row">
              <dt>Роль</dt>
              <dd>{{ roleLabel }}</dd>
            </div>
            <div class="details__row">
              <dt>UUID</dt>
              <dd class="details__mono">{{ profile.uuid }}</dd>
            </div>
          </dl>
        </article>

        <article class="panel activityCard">
          <div class="panelIntro panelIntro--compact">
            <div>
              <p class="panelEyebrow">Активность</p>
              <h3 class="panel__title">История аккаунта</h3>
            </div>
          </div>

          <dl class="details">
            <div class="details__row">
              <dt>Дата регистрации</dt>
              <dd>{{ formatDate(profile.created_at) }}</dd>
            </div>
            <div class="details__row">
              <dt>Обновлен</dt>
              <dd>{{ formatDate(profile.updated_at) }}</dd>
            </div>
            <div class="details__row">
              <dt>Последний вход</dt>
              <dd>{{ formatDate(profile.last_login_at) }}</dd>
            </div>
          </dl>
        </article>

        <article v-if="isEmployer" class="panel stackPanel">
          <div class="panelIntro panelIntro--compact">
            <div>
              <p class="panelEyebrow">Компания</p>
              <h3 class="panel__title">Профиль работодателя</h3>
            </div>
          </div>

          <div v-if="company" class="stackList">
            <section class="infoCard">
              <h4>{{ company.title }}</h4>
              <p class="bodyText">{{ company.description || "Описание отсутствует." }}</p>
              <p class="mutedText">Размер компании: {{ company.company_size || 0 }}</p>
              <p class="mutedText">Сайт: {{ company.website || "Не указан" }}</p>
            </section>

            <section class="subsection">
              <div class="subsection__head">
                <p class="panelEyebrow">Вакансии</p>
                <span class="readonlyChip">{{ employerVacancies.length }}</span>
              </div>
              <div v-if="employerVacancies.length" class="stackList">
                <article v-for="vacancy in employerVacancies" :key="vacancy.uuid" class="miniCard">
                  <div class="miniCard__top">
                    <h4>{{ vacancy.title }}</h4>
                    <span class="statusBadge muted">{{ vacancy.status }}</span>
                  </div>
                  <p class="mutedText">{{ vacancy.city || "Город не указан" }} · {{ formatSalary(vacancy.salary, vacancy.currency) }}</p>
                  <RouterLink class="ghostLink" :to="`/vacancies/${vacancy.uuid}`">Открыть вакансию</RouterLink>
                </article>
              </div>
              <p v-else class="mutedText">У этого работодателя пока нет вакансий.</p>
            </section>
          </div>
          <p v-else class="mutedText">Компания для этого пользователя не найдена.</p>
        </article>

        <article v-if="isCandidate" class="panel stackPanel">
          <div class="panelIntro panelIntro--compact">
            <div>
              <p class="panelEyebrow">Кандидат</p>
              <h3 class="panel__title">Резюме и отклики</h3>
            </div>
          </div>

          <div class="stackList">
            <section class="subsection">
              <div class="subsection__head">
                <p class="panelEyebrow">Резюме</p>
                <span class="readonlyChip">{{ candidateResumes.length }}</span>
              </div>
              <div v-if="candidateResumes.length" class="stackList">
                <article v-for="resume in candidateResumes" :key="resume.uuid" class="miniCard">
                  <div class="miniCard__top">
                    <h4>{{ resume.title }}</h4>
                    <span class="statusBadge muted">{{ formatSalary(resume.salary, resume.currency) }}</span>
                  </div>
                  <p class="bodyText">{{ resume.about_me || "Описание отсутствует." }}</p>
                  <RouterLink class="ghostLink" :to="`/resumes/${resume.uuid}`">Открыть резюме</RouterLink>
                </article>
              </div>
              <p v-else class="mutedText">У этого кандидата пока нет резюме.</p>
            </section>

            <section class="subsection">
              <div class="subsection__head">
                <p class="panelEyebrow">Отклики</p>
                <span class="readonlyChip">{{ candidateResponses.length }}</span>
              </div>
              <div v-if="candidateResponses.length" class="stackList">
                <article v-for="response in candidateResponses" :key="response.uuid" class="miniCard">
                  <div class="miniCard__top">
                    <h4>{{ responseVacancyTitle(response.vacancy_id) }}</h4>
                    <span class="statusBadge muted">{{ response.status }}</span>
                  </div>
                  <p class="bodyText">{{ response.message }}</p>
                  <div class="linkRow">
                    <RouterLink class="ghostLink" :to="`/vacancies/${response.vacancy_id}`">Вакансия</RouterLink>
                    <RouterLink class="ghostLink" :to="`/resumes/${response.resume_id}`">Резюме</RouterLink>
                  </div>
                </article>
              </div>
              <p v-else class="mutedText">У этого кандидата пока нет откликов.</p>
            </section>
          </div>
        </article>
      </section>
    </template>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { companyApi } from "../api/company";
import { responsesApi } from "../api/responses";
import { resumeApi } from "../api/resume";
import { usersApi } from "../api/users";
import { vacanciesApi } from "../api/vacancies";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import { getRoleLabel } from "../utils/auth";

const route = useRoute();
const loading = ref(true);
const error = ref("");
const profile = ref(null);
const company = ref(null);
const employerVacancies = ref([]);
const candidateResumes = ref([]);
const candidateResponses = ref([]);
const vacancyMap = ref({});

const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/vacancies", label: "Поиск вакансий" },
  { to: "/candidate/applications", label: "Мои отклики" },
  { to: "/candidate/resume", label: "Мои резюме" },
  { to: "/admin", label: "Панель администратора" },
  { to: "/profile", label: "Профиль" },
];

const roleLabel = computed(() => getRoleLabel(profile.value?.role));
const isEmployer = computed(() => profile.value?.role === "company");
const isCandidate = computed(() => profile.value?.role === "candidate");
const displayName = computed(() => profile.value?.fio || profile.value?.username || "Пользователь");
const avatarLetter = computed(() => String(displayName.value || "П").trim().slice(0, 1).toUpperCase());
const avatarImageSrc = computed(() => buildAvatarUrl(profile.value?.avatar_url));

function buildAvatarUrl(objectName) {
  if (!objectName) return "";
  const baseUrl = (import.meta.env.VITE_S3_PUBLIC_BASE_URL || "http://localhost:9000").replace(/\/$/, "");
  const normalizedPath = String(objectName)
    .split("/")
    .map((part) => encodeURIComponent(part))
    .join("/");
  return `${baseUrl}/avatars/${normalizedPath}`;
}

function formatDate(value) {
  if (!value) return "Нет данных";
  try {
    return new Date(value).toLocaleString("ru-RU");
  } catch {
    return value;
  }
}

function formatSalary(salary, currency) {
  if (!salary && salary !== 0) return "Зарплата не указана";
  return `${Number(salary).toLocaleString("ru-RU")} ${currency || "RUB"}`;
}

function responseVacancyTitle(vacancyId) {
  return vacancyMap.value[vacancyId]?.title || "Вакансия";
}

async function loadEmployerContext(userUuid) {
  try {
    company.value = await companyApi.getByUserId(userUuid);
  } catch (e) {
    if (e?.response?.status !== 404) throw e;
    company.value = null;
  }

  if (!company.value) {
    employerVacancies.value = [];
    return;
  }

  try {
    employerVacancies.value = await vacanciesApi.getAll({ company_id: company.value.uuid, limit: 500 }) || [];
  } catch (e) {
    if (e?.response?.status === 404) employerVacancies.value = [];
    else throw e;
  }
}

async function loadCandidateContext(userUuid) {
  let resumes = [];
  try {
    const allResumes = await resumeApi.getAll({ limit: 500 });
    resumes = Array.isArray(allResumes) ? allResumes.filter((item) => item.user_id === userUuid) : [];
  } catch (e) {
    if (e?.response?.status !== 404) throw e;
  }

  candidateResumes.value = resumes;

  const resumeIds = new Set(resumes.map((item) => item.uuid));
  if (!resumeIds.size) {
    candidateResponses.value = [];
    vacancyMap.value = {};
    return;
  }

  let responses = [];
  try {
    const allResponses = await responsesApi.getAll();
    responses = Array.isArray(allResponses) ? allResponses.filter((item) => resumeIds.has(item.resume_id)) : [];
  } catch (e) {
    if (e?.response?.status !== 404) throw e;
  }

  candidateResponses.value = responses;

  const vacancyIds = [...new Set(responses.map((item) => item.vacancy_id).filter(Boolean))];
  const entries = await Promise.all(
    vacancyIds.map(async (uuid) => {
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

async function loadProfile() {
  loading.value = true;
  error.value = "";
  company.value = null;
  employerVacancies.value = [];
  candidateResumes.value = [];
  candidateResponses.value = [];
  vacancyMap.value = {};

  try {
    profile.value = await usersApi.getById(route.params.uuid);

    if (profile.value?.role === "company") {
      await loadEmployerContext(profile.value.uuid);
    } else if (profile.value?.role === "candidate") {
      await loadCandidateContext(profile.value.uuid);
    }
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) error.value = "Пользователь не найден.";
    else if (status === 403) error.value = "Недостаточно прав для просмотра профиля.";
    else error.value = "Не удалось загрузить профиль пользователя.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadProfile);
</script>

<style scoped>
.heroCard,
.panel,
.errorPanel {
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}
.heroCard {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
}
.heroCard__identity { display: flex; align-items: center; gap: 18px; }
.heroCard__avatarWrap { display: grid; justify-items: center; }
.heroCard__avatar,
.heroCard__avatarImage { width: 92px; height: 92px; border-radius: 28px; }
.heroCard__avatar {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #ff7a59, #2f73ff);
  color: #fff;
  font-size: 34px;
  font-weight: 800;
}
.heroCard__avatarImage { object-fit: cover; border: 1px solid rgba(255,255,255,0.12); }
.heroCard__role {
  margin: 0 0 8px;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}
.heroCard__name { margin: 0; font-size: 30px; line-height: 1.1; }
.heroCard__login { margin: 8px 0 0; color: rgba(255, 255, 255, 0.68); }
.heroCard__statusWrap { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; }
.statusBadge {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.statusBadge.success { color: #91f2b0; border-color: rgba(145, 242, 176, 0.35); background: rgba(20, 66, 40, 0.22); }
.statusBadge.muted { color: rgba(255, 255, 255, 0.76); }
.contentGrid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr); gap: 18px; }
.stackPanel { grid-column: 1 / -1; }
.panel { padding: 22px; }
.panelIntro {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}
.panelIntro--compact { margin-bottom: 16px; }
.panelEyebrow {
  margin: 0 0 8px;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}
.panel__title { margin: 0; font-size: 24px; line-height: 1.15; }
.readonlyChip {
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(47,115,255,0.3);
  background: rgba(47,115,255,0.12);
  color: #dce7ff;
  font-size: 12px;
  font-weight: 700;
}
.details { display: grid; gap: 14px; margin: 0; }
.details--spacious { gap: 0; }
.details__row { display: grid; gap: 6px; padding: 14px 0; border-top: 1px solid rgba(255, 255, 255, 0.06); }
.details__row:first-child { padding-top: 0; border-top: none; }
.details dt { color: rgba(255, 255, 255, 0.58); font-size: 13px; }
.details dd { margin: 0; font-size: 17px; line-height: 1.45; }
.details__mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 14px; word-break: break-all; }
.stackList { display: grid; gap: 14px; }
.subsection { display: grid; gap: 12px; }
.subsection__head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.infoCard,
.miniCard {
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  padding: 16px;
  display: grid;
  gap: 10px;
}
.miniCard__top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.infoCard h4,
.miniCard h4 { margin: 0; font-size: 18px; }
.bodyText,
.mutedText { margin: 0; line-height: 1.65; }
.mutedText { color: rgba(255,255,255,0.68); }
.linkRow { display: flex; flex-wrap: wrap; gap: 10px; }
.ghostLink {
  min-height: 36px;
  padding: 0 12px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.03);
  color: #fff;
  font-weight: 700;
}
.errorPanel { padding: 18px; color: #ff9d9d; }
@media (max-width: 1100px) {
  .contentGrid { grid-template-columns: 1fr; }
}
@media (max-width: 780px) {
  .heroCard,
  .panelIntro,
  .subsection__head,
  .miniCard__top { flex-direction: column; align-items: flex-start; }
  .heroCard__statusWrap { justify-content: flex-start; }
}
</style>
