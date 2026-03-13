<template>
  <div class="page">
    <div class="pageGlow pageGlow--blue"></div>
    <div class="pageGlow pageGlow--coral"></div>

    <header class="header">
      <button class="ghost" type="button" @click="goBack">Назад</button>
    </header>

    <InlineLoader v-if="loading" text="Загружаем резюме..." />
    <p v-else-if="error" class="error">{{ error }}</p>

    <div v-else class="layout">
      <div class="left">
        <section class="panel heroPanel">
          <p class="eyebrow">Резюме</p>
          <div class="heroTop heroTop--profile">
            <div class="authorBlock">
              <img v-if="authorAvatarSrc" :src="authorAvatarSrc" alt="Аватар кандидата" class="authorAvatarImage" />
              <div v-else class="authorAvatarFallback">{{ authorLetter }}</div>

              <div class="authorMeta">
                <p class="authorLabel">Кандидат</p>
                <strong class="authorName">{{ authorName }}</strong>
                <span class="authorLogin">@{{ authorUsername }}</span>
              </div>
            </div>

            <span class="badge">{{ ageLabel }}</span>
          </div>

          <div>
            <h1 class="title">{{ resume.title }}</h1>
            <p class="lead">{{ resume.about_me || "Кандидат пока не добавил описание." }}</p>
          </div>

          <div class="metaGrid">
            <div class="metaTile">
              <span class="metaTile__label">Зарплатные ожидания</span>
              <strong>{{ salaryLabel }}</strong>
            </div>
            <div class="metaTile">
              <span class="metaTile__label">Пол</span>
              <strong>{{ genderLabel }}</strong>
            </div>
            <div class="metaTile">
              <span class="metaTile__label">Дата рождения</span>
              <strong>{{ birthDateLabel }}</strong>
            </div>
            <div class="metaTile">
              <span class="metaTile__label">Обновлено</span>
              <strong>{{ updatedLabel }}</strong>
            </div>
          </div>
        </section>

        <section v-if="contactItems.length" class="panel">
          <div class="sectionHeader">
            <p class="eyebrow">Контакты</p>
            <h2 class="h2">Как связаться с кандидатом</h2>
          </div>

          <div class="contactGrid">
            <a
              v-for="item in contactItems"
              :key="item.label"
              class="contactCard"
              :href="item.href"
              :target="item.external ? '_blank' : undefined"
              :rel="item.external ? 'noreferrer' : undefined"
            >
              <span class="contactCard__label">{{ item.label }}</span>
              <strong class="contactCard__value">{{ item.value }}</strong>
            </a>
          </div>
        </section>

        <section class="panel">
          <div class="sectionHeader">
            <p class="eyebrow">Опыт работы</p>
            <h2 class="h2">Профессиональный путь</h2>
          </div>

          <div v-if="resume.experiences?.length" class="timeline">
            <article v-for="item in resume.experiences" :key="item.uuid" class="timelineCard">
              <div class="timelineCard__head">
                <div>
                  <h3 class="h3">{{ item.position }}</h3>
                  <p class="mutedText">{{ item.company_name }}</p>
                </div>
                <span class="softBadge">{{ formatPeriod(item.start_date, item.end_date, item.is_current) }}</span>
              </div>
              <p v-if="item.description" class="text">{{ item.description }}</p>
            </article>
          </div>
          <p v-else class="mutedText">Опыт работы пока не добавлен.</p>
        </section>

        <section class="panel">
          <div class="sectionHeader">
            <p class="eyebrow">Образование</p>
            <h2 class="h2">Учебный трек</h2>
          </div>

          <div v-if="resume.educations?.length" class="timeline">
            <article v-for="item in resume.educations" :key="item.uuid" class="timelineCard">
              <div class="timelineCard__head">
                <div>
                  <h3 class="h3">{{ item.institution }}</h3>
                  <p class="mutedText">{{ educationLevelLabel(item.level) }}<span v-if="item.specialization"> · {{ item.specialization }}</span></p>
                </div>
                <span class="softBadge">{{ formatPeriod(item.start_date, item.end_date, item.is_current) }}</span>
              </div>
              <p v-if="item.description" class="text">{{ item.description }}</p>
            </article>
          </div>
          <p v-else class="mutedText">Образование пока не добавлено.</p>
        </section>
      </div>

      <aside class="right">
        <section class="panel compactPanel">
          <p class="eyebrow">Кратко</p>
          <ResumeCard :resume="resume" :interactive="false" />
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { resumeApi } from "../api/resume";
import { usersApi } from "../api/users";
import ResumeCard from "../components/resumes/ResumeCard.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import { getAccessToken, parseJwtPayload } from "../utils/auth";

const route = useRoute();
const router = useRouter();

const educationLabels = {
  SECONDARY: "Среднее",
  SECONDARY_SPECIAL: "Среднее специальное",
  INCOMPLETE_HIGHER: "Неоконченное высшее",
  BACHELOR: "Бакалавр",
  SPECIALIST: "Специалист",
  MASTER: "Магистр",
  POSTGRADUATE: "Аспирантура",
  DOCTORATE: "Докторантура",
};

const genderLabels = {
  MALE: "Мужчина",
  FEMALE: "Женщина",
};

const loading = ref(true);
const error = ref("");
const resume = ref(null);
const author = ref(null);

const salaryLabel = computed(() => {
  if (!resume.value?.salary && resume.value?.salary !== 0) return "Не указаны";
  return `${Number(resume.value.salary).toLocaleString("ru-RU")} ${resume.value.currency || "RUB"}`;
});

const genderLabel = computed(() => genderLabels[resume.value?.gender] || "Не указан");
const birthDateLabel = computed(() => formatDate(resume.value?.birth_date));
const updatedLabel = computed(() => formatDateTime(resume.value?.updated_at));
const authorName = computed(() => author.value?.fio || "Кандидат");
const authorUsername = computed(() => author.value?.username || "profile");
const authorLetter = computed(() => String(authorName.value || "К").trim().slice(0, 1).toUpperCase());
const authorAvatarSrc = computed(() => buildAvatarUrl(author.value?.avatar_url));
const currentUserUuid = computed(() => String(parseJwtPayload(getAccessToken())?.sub || ""));
const ageLabel = computed(() => {
  if (!resume.value?.birth_date) return "Возраст не указан";
  const birthDate = new Date(resume.value.birth_date);
  if (Number.isNaN(birthDate.getTime())) return "Возраст не указан";

  const now = new Date();
  let age = now.getFullYear() - birthDate.getFullYear();
  const monthDelta = now.getMonth() - birthDate.getMonth();
  if (monthDelta < 0 || (monthDelta === 0 && now.getDate() < birthDate.getDate())) age -= 1;
  return `${age} лет`;
});
const contactItems = computed(() => {
  const items = [];

  if (resume.value?.email) {
    items.push({
      label: "Email",
      value: resume.value.email,
      href: `mailto:${resume.value.email}`,
      external: false,
    });
  }

  if (resume.value?.telegram) {
    items.push({
      label: "Telegram",
      value: formatTelegramLabel(resume.value.telegram),
      href: normalizeTelegramLink(resume.value.telegram),
      external: true,
    });
  }

  if (resume.value?.phone_number) {
    items.push({
      label: "Телефон",
      value: resume.value.phone_number,
      href: `tel:${resume.value.phone_number}`,
      external: false,
    });
  }

  return items;
});

function goBack() {
  router.back();
}

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
  if (!value) return "Не указана";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Не указана";
  return date.toLocaleDateString("ru-RU");
}

function formatDateTime(value) {
  if (!value) return "Не указано";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Не указано";
  return date.toLocaleString("ru-RU");
}

function formatPeriod(startDate, endDate, isCurrent) {
  const start = startDate ? new Date(startDate).toLocaleDateString("ru-RU", { year: "numeric", month: "short" }) : "Не указано";
  const end = isCurrent
    ? "по настоящее время"
    : endDate
      ? new Date(endDate).toLocaleDateString("ru-RU", { year: "numeric", month: "short" })
      : "Не указано";
  return `${start} - ${end}`;
}

function educationLevelLabel(value) {
  return educationLabels[value] || value || "Не указано";
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

async function loadResume() {
  loading.value = true;
  error.value = "";

  try {
    const resumeData = await resumeApi.getById(route.params.uuid);
    resume.value = resumeData;

    if (String(resumeData?.user_id || "") === currentUserUuid.value) {
      try {
        author.value = await usersApi.getMe();
      } catch {
        author.value = null;
      }
    }
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) error.value = "Резюме не найдено";
    else if (status === 401) error.value = "Вы не авторизованы";
    else error.value = "Не удалось загрузить резюме";
  } finally {
    loading.value = false;
  }
}

onMounted(loadResume);
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
.layout,
.error {
  position: relative;
  z-index: 1;
  max-width: 1180px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 14px;
}

.ghost {
  min-height: 42px;
  border-radius: 14px;
  padding: 0 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.92);
  font-weight: 700;
  cursor: pointer;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.8fr);
  gap: 18px;
  align-items: start;
}

.left {
  display: grid;
  gap: 16px;
}

.right {
  position: sticky;
  top: 20px;
}

.panel {
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 22px;
  display: grid;
  gap: 14px;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}

.compactPanel {
  gap: 12px;
}

.eyebrow {
  margin: 0;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.heroTop,
.timelineCard__head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.heroTop--profile {
  align-items: center;
}

.authorBlock {
  display: flex;
  align-items: center;
  gap: 14px;
}

.authorAvatarImage,
.authorAvatarFallback {
  width: 74px;
  height: 74px;
  border-radius: 24px;
}

.authorAvatarImage {
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.authorAvatarFallback {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #2f73ff, #ff7a59);
  color: #fff;
  font-size: 26px;
  font-weight: 800;
}

.authorMeta {
  display: grid;
  gap: 4px;
}

.authorLabel,
.authorLogin,
.lead,
.text,
.mutedText {
  margin: 0;
  line-height: 1.7;
}

.authorLabel {
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.authorName {
  font-size: 22px;
}

.authorLogin {
  color: rgba(255, 255, 255, 0.56);
}

.title {
  margin: 0;
  font-size: 34px;
  line-height: 1.08;
}

.lead {
  color: rgba(255, 255, 255, 0.78);
  max-width: 760px;
}

.metaGrid,
.contactGrid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.metaTile,
.contactCard {
  display: grid;
  gap: 6px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.contactCard {
  text-decoration: none;
  color: #eaeaf0;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.contactCard:hover {
  transform: translateY(-1px);
  border-color: rgba(47, 115, 255, 0.34);
  background: rgba(47, 115, 255, 0.08);
}

.metaTile__label,
.contactCard__label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.55);
}

.contactCard__value {
  word-break: break-word;
}

.badge,
.softBadge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  white-space: nowrap;
}

.badge {
  min-height: 40px;
  min-width: 96px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.04);
}

.softBadge {
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(47, 115, 255, 0.12);
  border: 1px solid rgba(47, 115, 255, 0.22);
  color: #d8e5ff;
}

.sectionHeader {
  display: grid;
  gap: 8px;
}

.h2,
.h3 {
  margin: 0;
}

.h2 {
  font-size: 24px;
}

.h3 {
  font-size: 18px;
}

.timeline {
  display: grid;
  gap: 12px;
}

.timelineCard {
  display: grid;
  gap: 10px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
}

.mutedText {
  color: rgba(255, 255, 255, 0.68);
}

.error {
  color: #ff7d7d;
  font-size: 15px;
}

@media (max-width: 920px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .right {
    position: static;
  }
}

@media (max-width: 640px) {
  .heroTop,
  .timelineCard__head,
  .authorBlock {
    flex-direction: column;
    align-items: flex-start;
  }

  .metaGrid,
  .contactGrid {
    grid-template-columns: 1fr;
  }

  .title {
    font-size: 28px;
  }
}
</style>
