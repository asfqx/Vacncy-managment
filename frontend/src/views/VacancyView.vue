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
            <div v-if="canApply" class="actionCluster">
              <button
                class="applyBtn"
                type="button"
                :disabled="!canOpenApplyModal"
                @click="openApplyModal"
              >
                {{ applyButtonLabel }}
              </button>
              <span v-if="applicationHint" class="hintText">{{ applicationHint }}</span>
            </div>
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

            <div class="muted small">
              Размер команды: {{ company.company_size ? `${company.company_size} сотрудников` : "не указан" }}
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

    <transition name="modal-fade">
      <div v-if="showApplyModal" class="modalOverlay" @click.self="closeApplyModal">
        <div class="modalCard">
          <div class="modalHeader">
            <div>
              <p class="eyebrow">Отклик</p>
              <h2 class="h2">Отклик на {{ vacancy?.title }}</h2>
            </div>
            <button class="iconBtn" type="button" @click="closeApplyModal">×</button>
          </div>

          <div class="modalBody">

            <label class="field">
              <span>Сопроводительное письмо</span>
              <textarea
                v-model="responseForm.message"
                class="input input--textarea"
                rows="10"
                placeholder="Расскажите, почему вы подходите на эту вакансию"
              />
            </label>

            <p v-if="applyError" class="error">{{ applyError }}</p>
            <p v-if="applySuccess" class="success">{{ applySuccess }}</p>
          </div>

          <div class="modalActions">
            <button class="ghostBtn" type="button" :disabled="generatingResponse || submittingResponse" @click="generateResponseText">
              {{ generatingResponse ? "Генерируем..." : "Сгенерировать текст" }}
            </button>
            <button class="applyBtn" type="button" :disabled="submittingResponse || !canSubmitResponse" @click="submitResponse">
              {{ submittingResponse ? "Отправляем..." : "Отправить отклик" }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import InlineLoader from "../components/ui/InlineLoader.vue";
import { companyApi } from "../api/company";
import { responsesApi } from "../api/responses";
import { resumeApi } from "../api/resume";
import { vacanciesApi } from "../api/vacancies";
import { getUserRoleFromToken, isAdminRole, isCandidateRole } from "../utils/auth";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref("");
const vacancy = ref(null);
const companyLoading = ref(false);
const companyError = ref("");
const company = ref(null);
const role = getUserRoleFromToken();
const canApply = computed(() => isCandidateRole(role) || isAdminRole(role));
const companyAvatarSrc = computed(() => buildAvatarUrl(company.value?.avatar_url));
const companyAvatarLetter = computed(() => String(company.value?.title || "К").trim().slice(0, 1).toUpperCase());
const showApplyModal = ref(false);
const generatingResponse = ref(false);
const submittingResponse = ref(false);
const applyError = ref("");
const applySuccess = ref("");
const myResume = ref(null);
const hasExistingResponse = ref(false);
const existingResponseStatus = ref("");

const responseForm = reactive({
  message: "",
});

const canOpenApplyModal = computed(() => canApply.value && Boolean(myResume.value?.uuid) && !hasExistingResponse.value);
const canSubmitResponse = computed(() => String(responseForm.message || "").trim().length >= 20);
const applyButtonLabel = computed(() => {
  if (!canApply.value) return "";
  if (hasExistingResponse.value) return statusLabel(existingResponseStatus.value);
  if (!myResume.value?.uuid) return "Сначала заполните резюме";
  return "Откликнуться";
});
const applicationHint = computed(() => {
  if (!canApply.value) return "";
  if (hasExistingResponse.value) return "Отклик уже отправлен и отображается в разделе “Мои отклики”.";
  if (!myResume.value?.uuid) return "Без резюме мы не сможем сгенерировать письмо и отправить отклик.";
  return "";
});

function buildAvatarUrl(objectName) {
  if (!objectName) return "";
  const baseUrl = (import.meta.env.VITE_S3_PUBLIC_BASE_URL || "http://localhost:9000").replace(/\/$/, "");
  const normalizedPath = String(objectName).split("/").map((part) => encodeURIComponent(part)).join("/");
  return `${baseUrl}/avatars/${normalizedPath}`;
}

function goBack() {
  router.back();
}

function formatSalary(salary, currency) {
  if (!salary) return "Зарплата не указана";
  return `${salary.toLocaleString("ru-RU")} ${currency || "RUB"}`;
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString("ru-RU");
  } catch {
    return iso;
  }
}

function statusLabel(status) {
  const map = {
    PENDING: "Отклик уже отправлен",
    ACCEPTED: "Отклик принят",
    REJECTED: "Отклик отклонен",
  };
  return map[String(status || "").toUpperCase()] || "Откликнуться";
}

function openApplyModal() {
  if (!canOpenApplyModal.value) return;
  applyError.value = "";
  applySuccess.value = "";

  responseForm.message = "";
  showApplyModal.value = true;
}

function closeApplyModal() {
  if (generatingResponse.value || submittingResponse.value) return;
  showApplyModal.value = false;
}

async function loadCompany(companyId) {
  companyLoading.value = true;
  companyError.value = "";

  try {
    company.value = await companyApi.getById(companyId);
  } catch (e) {
    const status = e?.response?.status;
    companyError.value = status === 404 ? "Компания не найдена" : "Не удалось загрузить данные компании";
    company.value = null;
  } finally {
    companyLoading.value = false;
  }
}

async function loadCandidateState() {
  if (!canApply.value) return;

  try {
    myResume.value = await resumeApi.getMine();
  } catch (e) {
    if (e?.response?.status !== 404) {
      console.error(e);
    }
    myResume.value = null;
  }

  try {
    const responses = await responsesApi.getAll();
    const current = responses.find((item) => item.vacancy_id === route.params.uuid);
    hasExistingResponse.value = Boolean(current);
    existingResponseStatus.value = current?.status || "";
  } catch (e) {
    if (e?.response?.status !== 404) {
      console.error(e);
    }
    hasExistingResponse.value = false;
    existingResponseStatus.value = "";
  }
}

async function loadVacancy() {
  loading.value = true;
  error.value = "";
  vacancy.value = null;

  try {
    const data = await vacanciesApi.getById(route.params.uuid);
    vacancy.value = data;

    if (data?.company_id) {
      await loadCompany(data.company_id);
    }

    await loadCandidateState();
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) error.value = "Вакансия не найдена";
    else if (status === 401) error.value = "Вы не авторизованы";
    else error.value = "Не удалось загрузить вакансию";
  } finally {
    loading.value = false;
  }
}

async function generateResponseText() {
  if (!vacancy.value?.uuid) return;
  generatingResponse.value = true;
  applyError.value = "";
  applySuccess.value = "";

  try {
    const data = await responsesApi.generate({ vacancy_uuid: vacancy.value.uuid });
    responseForm.message = data?.text || "";
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) applyError.value = "Сначала заполните и сохраните резюме.";
    else applyError.value = "Не удалось сгенерировать текст письма.";
  } finally {
    generatingResponse.value = false;
  }
}

async function submitResponse() {
  if (!vacancy.value?.uuid || !canSubmitResponse.value) return;
  submittingResponse.value = true;
  applyError.value = "";
  applySuccess.value = "";

  try {
    const created = await responsesApi.create({
      vacancy_uuid: vacancy.value.uuid,
      message: String(responseForm.message || "").trim(),
    });

    hasExistingResponse.value = true;
    existingResponseStatus.value = created?.status || "PENDING";
    applySuccess.value = "Отклик отправлен.";
    responseForm.message = "";
    closeApplyModal();
  } catch (e) {
    const status = e?.response?.status;
    if (status === 409) {
      applyError.value = "Вы уже откликались на эту вакансию.";
      hasExistingResponse.value = true;
    } else if (status === 404) {
      applyError.value = "Не найдено резюме. Сначала заполните его.";
    } else {
      applyError.value = "Не удалось отправить отклик.";
    }
  } finally {
    submittingResponse.value = false;
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
.pageGlow { position: absolute; border-radius: 999px; filter: blur(80px); opacity: 0.32; pointer-events: none; }
.pageGlow--blue { width: 260px; height: 260px; left: -60px; top: 20px; background: rgba(47, 115, 255, 0.28); }
.pageGlow--coral { width: 220px; height: 220px; right: -40px; bottom: 30px; background: rgba(255, 122, 89, 0.18); }
.header, .layout { position: relative; z-index: 1; max-width: 1180px; margin: 0 auto; }
.header { display: flex; justify-content: flex-start; margin-bottom: 14px; }
.ghost, .ghostBtn, .iconBtn {
  border-radius: 14px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.92);
  cursor: pointer;
}
.ghost { min-height: 42px; padding: 0 14px; font-weight: 700; }
.layout { display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.8fr); gap: 18px; align-items: start; }
.left { display: grid; gap: 16px; }
.right { position: sticky; top: 20px; }
.panel { background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98)); border: 1px solid rgba(255,255,255,0.10); border-radius: 24px; padding: 22px; display: grid; gap: 12px; box-shadow: 0 18px 44px rgba(0,0,0,0.24); }
.eyebrow { margin: 0; color: #8eb4ff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; }
.title { margin: 0; font-size: 34px; line-height: 1.08; }
.row, .actionRow { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.actionCluster { display: grid; gap: 8px; }
.hintText { font-size: 13px; color: rgba(255,255,255,0.64); }
.salary { font-size: 26px; font-weight: 800; }
.badge { display: inline-flex; align-items: center; min-height: 38px; padding: 0 12px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.16); background: rgba(255,255,255,0.04); }
.badge.remote { border-color: rgba(124,255,155,0.35); color: #9ff0b8; }
.meta { margin: 0; font-size: 15px; opacity: 0.82; display: flex; gap: 8px; align-items: center; }
.dot { opacity: 0.6; }
.h2 { margin: 0; font-size: 24px; }
.h3 { margin: 0; font-size: 16px; }
.text { margin: 0; font-size: 15px; line-height: 1.7; opacity: 0.92; white-space: pre-wrap; }
.companyHead { display: flex; align-items: center; gap: 14px; }
.companyAvatarImage, .companyAvatarFallback { width: 56px; height: 56px; border-radius: 18px; }
.companyAvatarImage { object-fit: cover; border: 1px solid rgba(255,255,255,0.12); }
.companyAvatarFallback { display: grid; place-items: center; background: linear-gradient(135deg, #ff7a59, #2f73ff); color: #fff; font-size: 22px; font-weight: 800; }
.companyTitleWrap { display: grid; gap: 4px; }
.companyTitle { font-weight: 800; font-size: 22px; }
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
.applyBtn:disabled, .ghostBtn:disabled { opacity: 0.6; cursor: not-allowed; }
.companyPanel { gap: 16px; }
.divider { height: 1px; background: rgba(255,255,255,0.08); margin: 6px 0 4px; }
.infoTile { padding: 4px 0 0; display: grid; gap: 10px; }
.error { color: #ff7d7d; font-size: 15px; margin: 0 auto; max-width: 1180px; position: relative; z-index: 1; }
.success { color: #9ff0b8; margin: 0; }
.field { display: grid; gap: 8px; }
.field span { font-size: 13px; color: rgba(255,255,255,0.72); font-weight: 700; }
.input { min-height: 52px; border-radius: 16px; padding: 0 16px; background: rgba(8, 10, 16, 0.96); border: 1px solid rgba(255,255,255,0.08); color: #eef2ff; outline: none; }
.input--textarea { min-height: 220px; padding: 14px 16px; resize: none; }
.modalOverlay { position: fixed; inset: 0; background: rgba(3, 6, 12, 0.72); backdrop-filter: blur(8px); display: grid; place-items: center; padding: 20px; z-index: 40; }
.modalCard { width: min(760px, 100%); border-radius: 28px; border: 1px solid rgba(255,255,255,0.12); background: linear-gradient(180deg, rgba(18, 19, 27, 0.98), rgba(9, 10, 15, 0.99)); box-shadow: 0 24px 80px rgba(0,0,0,0.35); display: grid; gap: 18px; padding: 24px; }
.modalHeader, .modalActions { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.modalBody { display: grid; gap: 16px; }
.iconBtn { width: 40px; height: 40px; font-size: 24px; }
.ghostBtn { min-height: 44px; padding: 0 14px; font-weight: 700; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.18s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
@media (max-width: 920px) { .layout { grid-template-columns: 1fr; } .right { position: static; } }
@media (max-width: 640px) { .row, .actionRow, .modalHeader, .modalActions { flex-direction: column; align-items: flex-start; } .title { font-size: 28px; } .modalCard { padding: 18px; } }
</style>





