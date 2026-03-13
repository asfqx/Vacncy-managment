<template>
  <DashboardShell
    title="Отклики на вакансии"
    subtitle="Просматривайте входящие отклики, проверяйте резюме и меняйте статус кандидата."
    role-label="Работодатель"
    :nav-items="navItems"
    :primary-action="{ to: '/employer/vacancies/create', label: 'Создать вакансию' }"
    home-path="/home"
    avatar-letter="Р"
  >
    <template #aside>
      <UiCard title="Все отклики" :subtitle="String(items.length)" :active="activeFilter === 'all'" @click="setFilter('all')" />
      <UiCard title="Ожидают" :subtitle="String(stats.pending)" :active="activeFilter === 'pending'" @click="setFilter('pending')" />
      <UiCard title="Принято" :subtitle="String(stats.accepted)" :active="activeFilter === 'accepted'" @click="setFilter('accepted')" />
      <UiCard title="Отклонено" :subtitle="String(stats.rejected)" :active="activeFilter === 'rejected'" @click="setFilter('rejected')" />
    </template>

    <InlineLoader v-if="loading" text="Загружаем отклики..." />
    <p v-else-if="error" class="errorText">{{ error }}</p>
    <section v-else-if="!items.length" class="emptyState">
      <p class="eyebrow">Пусто</p>
      <h2>Отклики пока не поступили</h2>
      <p>Когда кандидаты начнут отправлять отклики, здесь появятся карточки со статусом, письмом и ссылками на резюме и вакансию.</p>
    </section>
    <section v-else-if="!filteredItems.length" class="emptyState emptyState--filtered">
      <div class="emptyState__content">
        <p class="eyebrow">Фильтр</p>
        <h2>По выбранному статусу откликов нет</h2>
        <p>Попробуйте переключиться на другой статус в левой колонке, чтобы увидеть остальные отклики.</p>
        <button class="ghostLink ghostLink--button" type="button" @click="setFilter('all')">Показать все отклики</button>
      </div>
    </section>

    <div v-else class="workspace">
      <aside class="responseList">
        <button
          v-for="item in filteredItems"
          :key="item.uuid"
          class="responseListItem"
          :class="{ 'is-active': selectedResponse?.uuid === item.uuid }"
          type="button"
          @click="selectResponse(item.uuid)"
        >
          <div class="responseListItem__head">
            <strong>{{ vacancyMap[item.vacancy_id]?.title || 'Вакансия' }}</strong>
            <span class="statusBadge" :class="statusClass(item.status)">{{ statusLabel(item.status) }}</span>
          </div>
          <p class="responseListItem__sub">{{ resumeMap[item.resume_id]?.title || 'Резюме кандидата' }}</p>
          <p class="responseListItem__meta">{{ formatDate(item.created_at) }}</p>
        </button>
      </aside>

      <section v-if="selectedResponse" class="detailCard">
        <div class="detailCard__header">
          <div>
            <p class="eyebrow">Отклик</p>
            <h2>{{ vacancyMap[selectedResponse.vacancy_id]?.title || 'Вакансия' }}</h2>
            <p class="mutedText">{{ resumeMap[selectedResponse.resume_id]?.title || 'Резюме кандидата' }}</p>
          </div>
          <span class="statusBadge" :class="statusClass(selectedResponse.status)">{{ statusLabel(selectedResponse.status) }}</span>
        </div>

        <div class="metaGrid">
          <div class="metaTile">
            <span>Статус</span>
            <strong>{{ statusLabel(selectedResponse.status) }}</strong>
          </div>
          <div class="metaTile">
            <span>Создан</span>
            <strong>{{ formatDate(selectedResponse.created_at) }}</strong>
          </div>
          <div class="metaTile">
            <span>Email</span>
            <strong>{{ candidateProfileMap[resumeMap[selectedResponse.resume_id]?.user_id]?.email || 'Не указан' }}</strong>
          </div>
          <div class="metaTile">
            <span>Телефон</span>
            <strong>{{ candidateProfileMap[resumeMap[selectedResponse.resume_id]?.user_id]?.phone_number || 'Не указан' }}</strong>
          </div>
        </div>

        <article class="letterCard">
          <p class="eyebrow">Письмо</p>
          <h3>{{ responseLetterTitle(selectedResponse) }}</h3>
          <p class="letterText">{{ selectedResponse.message }}</p>
        </article>

        <section class="letterCard">
          <p class="eyebrow">Комментарий работодателя</p>
          <textarea
            v-model="employerComment"
            class="commentInput"
            rows="4"
            placeholder="Можно оставить комментарий для кандидата"
          />
          <p class="mutedText">Комментарий можно не заполнять. Он будет виден кандидату в его откликах.</p>
        </section>

        <div class="actionRow">
          <RouterLink class="ghostLink" :to="`/vacancies/${selectedResponse.vacancy_id}`">Вакансия</RouterLink>
          <RouterLink class="ghostLink" :to="`/resumes/${selectedResponse.resume_id}`">Резюме</RouterLink>
          <button
            class="approveBtn"
            type="button"
            :disabled="updatingStatus"
            @click="changeStatus('ACCEPTED')"
          >
            {{ updatingStatus && pendingStatus === 'ACCEPTED' ? 'Сохраняем...' : 'Принять' }}
          </button>
          <button
            class="rejectBtn"
            type="button"
            :disabled="updatingStatus"
            @click="changeStatus('REJECTED')"
          >
            {{ updatingStatus && pendingStatus === 'REJECTED' ? 'Сохраняем...' : 'Отклонить' }}
          </button>
        </div>

        <p v-if="actionError" class="errorText">{{ actionError }}</p>
      </section>
    </div>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { responsesApi } from "../api/responses";
import { resumeApi } from "../api/resume";
import { usersApi } from "../api/users";
import { vacanciesApi } from "../api/vacancies";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import UiCard from "../components/ui/UiCard.vue";

const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/employer/resumes", label: "Поиск резюме" },
  { to: "/employer/vacancies", label: "Мои вакансии" },
  { to: "/employer/applications", label: "Отклики" },
  { to: "/employer/vacancies/create", label: "Создать вакансию" },
  { to: "/profile", label: "Профиль" },
];

const loading = ref(true);
const error = ref("");
const actionError = ref("");
const updatingStatus = ref(false);
const pendingStatus = ref("");
const items = ref([]);
const selectedUuid = ref("");
const activeFilter = ref("all");
const vacancyMap = ref({});
const resumeMap = ref({});
const candidateProfileMap = ref({});
const employerComment = ref("");

const filteredItems = computed(() => {
  if (activeFilter.value === "pending") return items.value.filter((item) => item.status === "PENDING");
  if (activeFilter.value === "accepted") return items.value.filter((item) => item.status === "ACCEPTED");
  if (activeFilter.value === "rejected") return items.value.filter((item) => item.status === "REJECTED");
  return items.value;
});

const selectedResponse = computed(() => (
  filteredItems.value.find((item) => item.uuid === selectedUuid.value) || filteredItems.value[0] || null
));

const stats = computed(() => ({
  pending: items.value.filter((item) => item.status === "PENDING").length,
  accepted: items.value.filter((item) => item.status === "ACCEPTED").length,
  rejected: items.value.filter((item) => item.status === "REJECTED").length,
}));

watch(
  () => selectedResponse.value?.uuid,
  () => {
    employerComment.value = selectedResponse.value?.employer_comment || "";
  },
  { immediate: true }
);

function statusLabel(status) {
  return ({ PENDING: "Ожидает", ACCEPTED: "Принят", REJECTED: "Отклонен" })[status] || status;
}

function statusClass(status) {
  return {
    "status--pending": status === "PENDING",
    "status--accepted": status === "ACCEPTED",
    "status--rejected": status === "REJECTED",
  };
}

function setFilter(filter) {
  activeFilter.value = filter;
  if (!filteredItems.value.some((item) => item.uuid === selectedUuid.value)) {
    selectedUuid.value = filteredItems.value[0]?.uuid || "";
  }
}

function selectResponse(uuid) {
  selectedUuid.value = uuid;
}

function responseLetterTitle(item) {
  const resume = resumeMap.value[item.resume_id];
  return resume?.title ? `Письмо к резюме ${resume.title}` : "Сопроводительное письмо";
}

function formatDate(value) {
  try {
    return new Date(value).toLocaleString("ru-RU");
  } catch {
    return value;
  }
}

async function hydrateMaps(responses) {
  const vacancyIds = [...new Set(responses.map((item) => item.vacancy_id).filter(Boolean))];
  const resumeIds = [...new Set(responses.map((item) => item.resume_id).filter(Boolean))];

  const [vacancies, resumes] = await Promise.all([
    Promise.all(vacancyIds.map(async (uuid) => {
      try {
        return [uuid, await vacanciesApi.getById(uuid)];
      } catch {
        return [uuid, null];
      }
    })),
    Promise.all(resumeIds.map(async (uuid) => {
      try {
        return [uuid, await resumeApi.getById(uuid)];
      } catch {
        return [uuid, null];
      }
    })),
  ]);

  vacancyMap.value = Object.fromEntries(vacancies);
  resumeMap.value = Object.fromEntries(resumes);
}

async function hydrateCandidateProfiles() {
  const userIds = [...new Set(Object.values(resumeMap.value).map((item) => item?.user_id).filter(Boolean))];
  const entries = await Promise.all(
    userIds.map(async (uuid) => {
      try {
        return [uuid, await usersApi.getById(uuid)];
      } catch {
        return [uuid, null];
      }
    })
  );

  candidateProfileMap.value = Object.fromEntries(entries);
}

async function loadResponses() {
  loading.value = true;
  error.value = "";

  try {
    const data = await responsesApi.getAll();
    items.value = Array.isArray(data) ? data : [];
    selectedUuid.value = items.value[0]?.uuid || "";
    await hydrateMaps(items.value);
    await hydrateCandidateProfiles();
  } catch (e) {
    if (e?.response?.status === 404) {
      items.value = [];
      selectedUuid.value = "";
      vacancyMap.value = {};
      resumeMap.value = {};
      candidateProfileMap.value = {};
    } else {
      error.value = "Не удалось загрузить отклики.";
    }
  } finally {
    loading.value = false;
  }
}

async function changeStatus(status) {
  if (!selectedResponse.value?.uuid) return;
  updatingStatus.value = true;
  pendingStatus.value = status;
  actionError.value = "";

  try {
    const updated = await responsesApi.updateStatus(selectedResponse.value.uuid, {
      status,
      employer_comment: employerComment.value?.trim() || null,
    });
    items.value = items.value.map((item) => (item.uuid === updated.uuid ? updated : item));
    employerComment.value = updated.employer_comment || "";
    if (!filteredItems.value.some((item) => item.uuid === updated.uuid)) {
      selectedUuid.value = filteredItems.value[0]?.uuid || "";
    }
  } catch {
    actionError.value = "Не удалось изменить статус отклика.";
  } finally {
    updatingStatus.value = false;
    pendingStatus.value = "";
  }
}

onMounted(loadResponses);
</script>

<style scoped>
.workspace { display: grid; grid-template-columns: 360px minmax(0, 1fr); gap: 18px; }
.responseList { display: grid; gap: 10px; align-content: start; }
.responseListItem, .detailCard, .emptyState {
  border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.08);
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  box-shadow: 0 18px 44px rgba(0,0,0,0.24);
}
.emptyState {
  padding: 24px;
  overflow-wrap: anywhere;
}
.emptyState h2,
.emptyState p {
  max-width: 100%;
}
.emptyState p {
  margin: 12px 0 0;
}
.responseListItem {
  padding: 16px;
  text-align: left;
  color: #fff;
  cursor: pointer;
}
.responseListItem.is-active { border-color: rgba(47,115,255,0.32); background: linear-gradient(180deg, rgba(25, 32, 50, 0.96), rgba(13, 16, 25, 0.98)); }
.responseListItem__head { display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }
.responseListItem__sub, .responseListItem__meta, .mutedText, .letterText, .emptyState p { color: rgba(255,255,255,0.72); line-height: 1.6; }
.responseListItem__sub { margin: 10px 0 0; }
.responseListItem__meta { margin: 8px 0 0; font-size: 13px; }
.detailCard { padding: 24px; display: grid; gap: 18px; }
.detailCard__header { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.actionRow { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; align-items: stretch; }
.metaGrid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.metaTile, .letterCard { padding: 16px; border-radius: 18px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); }
.metaTile span { display: block; margin-bottom: 6px; color: rgba(255,255,255,0.55); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
.letterCard h3, .emptyState h2 { margin: 8px 0 0; }
.letterText { white-space: pre-wrap; margin: 12px 0 0; }
.commentInput {
  width: 100%;
  min-height: 110px;
  margin-top: 10px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(8, 10, 16, 0.96);
  border: 1px solid rgba(255,255,255,0.08);
  color: #eef2ff;
  outline: none;
  resize: none;
}
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
}
.status--pending { background: rgba(255,196,84,0.14); color: #ffd36f; }
.status--accepted { background: rgba(124,255,155,0.12); color: #9ff0b8; }
.status--rejected { background: rgba(255,113,113,0.12); color: #ffb0b0; }
.approveBtn, .rejectBtn, .ghostLink {
  width: 100%;
  min-height: 44px;
  padding: 0 16px;
  border-radius: 14px;
  font-weight: 700;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease, color 0.18s ease;
}
.ghostLink { color: #fff; border: 1px solid rgba(255,255,255,0.14); }
.ghostLink:hover {
  transform: translateY(-1px);
  border-color: rgba(47,115,255,0.34);
  background: rgba(47,115,255,0.12);
  box-shadow: 0 10px 24px rgba(47,115,255,0.16);
}
.approveBtn { border: 1px solid rgba(124,255,155,0.28); background: rgba(124,255,155,0.12); color: #9ff0b8; }
.approveBtn:hover {
  transform: translateY(-1px);
  border-color: rgba(124,255,155,0.42);
  background: rgba(124,255,155,0.2);
  box-shadow: 0 10px 24px rgba(124,255,155,0.14);
}
.rejectBtn { border: 1px solid rgba(255,113,113,0.28); background: rgba(255,113,113,0.12); color: #ffb0b0; }
.rejectBtn:hover {
  transform: translateY(-1px);
  border-color: rgba(255,113,113,0.42);
  background: rgba(255,113,113,0.2);
  box-shadow: 0 10px 24px rgba(255,113,113,0.14);
}
.approveBtn:disabled, .rejectBtn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
.errorText { color: #ff8e8e; }
.emptyState--filtered { display: grid; place-items: center; min-height: 320px; }
.emptyState__content { width: min(640px, 100%); display: grid; gap: 14px; }
.emptyState--filtered h2, .emptyState--filtered p { margin: 0; }
.ghostLink--button { background: transparent; cursor: pointer; width: fit-content; }
.eyebrow { margin: 0; color: #8eb4ff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; }
@media (max-width: 1080px) { .workspace { grid-template-columns: 1fr; } }
@media (max-width: 720px) { .responseListItem__head, .detailCard__header { flex-direction: column; align-items: flex-start; } .actionRow { grid-template-columns: 1fr 1fr; } .metaGrid { grid-template-columns: 1fr; } }
@media (max-width: 520px) { .actionRow { grid-template-columns: 1fr; } }
</style>


