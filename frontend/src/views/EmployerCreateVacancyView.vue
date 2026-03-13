<template>
  <DashboardShell
    title="Создание вакансии"
    subtitle="Заполните ключевые поля и опубликуйте вакансию от имени компании."
    role-label="Работодатель"
    :nav-items="navItems"
    :primary-action="{ to: '/employer/vacancies/create', label: 'Создать вакансию' }"
    :secondary-action="secondaryAction"
    home-path="/home"
    avatar-letter="Р"
  >
    <section class="pageGrid">
      <article class="panel introPanel">
        <p class="eyebrow">Вакансия</p>
        <h2 class="title">Новая публикация</h2>
        <p class="lead">Укажите роль, формат работы и коротко опишите задачи.</p>

        <div class="tips">
          <div class="tipCard">
            <strong>Понятный заголовок</strong>
            <span>Например, Frontend разработчик Vue.js.</span>
          </div>
          <div class="tipCard">
            <strong>Живое описание</strong>
            <span>Добавьте стек, задачи и ожидания от кандидата.</span>
          </div>
          <div class="tipCard">
            <strong>Покажите контекст</strong>
            <span>Напишите, какой продукт строит команда и над чем человек будет работать в первые месяцы.</span>
          </div>
        </div>
      </article>

      <article class="panel formPanel">
        <div class="panelHeader">
          <div>
            <p class="eyebrow">Форма</p>
            <h2 class="title">Параметры вакансии</h2>
          </div>
          <span class="chip">Публикуется сразу</span>
        </div>

        <form class="vacancyForm" @submit.prevent="submitVacancy">
          <label class="field field--full">
            <span>Название вакансии</span>
            <input v-model="form.title" class="input" type="text" placeholder="Frontend разработчик Vue.js" />
          </label>

          <label class="field field--full">
            <span>Описание</span>
            <textarea
              v-model="form.description"
              class="input input--textarea"
              rows="8"
              placeholder="Коротко опишите задачи, стек, формат работы и процесс отбора."
            />
          </label>

          <div class="toggleRow">
            <button class="toggle" :class="{ active: !form.remote }" type="button" @click="form.remote = false">Офис / гибрид</button>
            <button class="toggle" :class="{ active: form.remote }" type="button" @click="form.remote = true">Удаленно</button>
          </div>

          <label class="field">
            <span>Город</span>
            <input v-model="form.city" class="input" type="text" :placeholder="form.remote ? 'Можно не указывать' : 'Москва'" />
          </label>

          <label class="field">
            <span>Зарплата</span>
            <input v-model.number="form.salary" class="input" type="number" min="0" placeholder="250000" />
          </label>

          <label class="field field--narrow">
            <span>Валюта</span>
            <AppSelect v-model="form.currency" :options="currencyOptions" />
          </label>

          <div class="summaryBox">
            <p class="summaryBox__title">Предпросмотр</p>
            <p class="summaryBox__line"><strong>{{ previewTitle }}</strong></p>
            <p class="summaryBox__line">{{ previewLocation }}</p>
            <p class="summaryBox__line">{{ previewSalary }}</p>
          </div>

          <div class="actions">
            <button class="primaryBtn" type="submit" :disabled="submitting">
              {{ submitting ? "Публикуем..." : "Создать вакансию" }}
            </button>
          </div>
        </form>

        <p v-if="successMessage" class="successText">{{ successMessage }}</p>
        <p v-if="errorMessage" class="errorText">{{ errorMessage }}</p>
      </article>
    </section>
  </DashboardShell>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import AppSelect from "../components/ui/AppSelect.vue";
import { vacanciesApi } from "../api/vacancies";
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
const submitting = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const currencyOptions = [
  { value: "", label: "Не указана" },
  { value: "RUB", label: "RUB" },
  { value: "USD", label: "USD" },
  { value: "EUR", label: "EUR" },
];

const form = reactive({
  title: "",
  description: "",
  city: "",
  remote: false,
  salary: null,
  currency: "RUB",
});

const secondaryAction = computed(() => (
  isAdminRole(role) ? { to: "/vacancies", label: "Страница кандидата" } : null
));

const previewTitle = computed(() => form.title.trim() || "Название вакансии");
const previewLocation = computed(() => {
  if (form.remote) return "Удаленно";
  return form.city.trim() ? `Город: ${form.city.trim()}` : "Город не указан";
});
const previewSalary = computed(() => {
  if (!form.salary && form.salary !== 0) return "Зарплата не указана";
  return `${form.salary} ${form.currency || ""}`.trim();
});

function resetForm() {
  form.title = "";
  form.description = "";
  form.city = "";
  form.remote = false;
  form.salary = null;
  form.currency = "RUB";
}

async function submitVacancy() {
  submitting.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      city: form.city.trim() || null,
      remote: form.remote,
      salary: Number.isFinite(form.salary) ? form.salary : null,
      currency: form.currency || null,
    };

    await vacanciesApi.create(payload);
    successMessage.value = "Вакансия успешно создана.";
    resetForm();
  } catch (e) {
    const status = e?.response?.status;
    const detail = e?.response?.data?.detail;

    if (status === 400 && typeof detail === "string") errorMessage.value = detail;
    else if (status === 409) errorMessage.value = "Вакансия с таким названием уже существует.";
    else if (status === 422) errorMessage.value = "Проверьте заполнение полей и попробуйте снова.";
    else errorMessage.value = "Не удалось создать вакансию.";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.pageGrid { display: grid; grid-template-columns: minmax(360px, 0.9fr) minmax(0, 1.9fr); gap: 18px; }
.panel { border-radius: 26px; border: 1px solid rgba(255,255,255,0.08); background: linear-gradient(180deg, rgba(18,19,27,0.96), rgba(11,12,17,0.98)); box-shadow: 0 18px 44px rgba(0,0,0,0.24); }
.introPanel, .formPanel { padding: 24px; }
.eyebrow { margin: 0 0 10px; color: #8eb4ff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; }
.title { margin: 0; font-size: 30px; line-height: 1.1; }
.lead { margin: 14px 0 0; max-width: 42ch; color: rgba(255,255,255,0.72); line-height: 1.7; }
.tips { display: grid; gap: 12px; margin-top: 20px; }
.tipCard, .summaryBox { padding: 16px; border-radius: 18px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); }
.tipCard strong, .summaryBox__title { display: block; margin-bottom: 8px; }
.tipCard span, .summaryBox__line { color: rgba(255,255,255,0.7); line-height: 1.6; }
.panelHeader { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 22px; }
.chip { display: inline-flex; align-items: center; justify-content: center; min-height: 42px; padding: 8px 16px; border-radius: 999px; color: rgba(255,255,255,0.88); background: rgba(47,115,255,0.14); border: 1px solid rgba(47,115,255,0.28); text-align: center; line-height: 1.2; white-space: normal; }
.vacancyForm { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.field { display: grid; gap: 8px; }
.field--full, .summaryBox, .actions { grid-column: 1 / -1; }
.field--narrow { max-width: 180px; }
.field span { color: rgba(255,255,255,0.7); font-size: 13px; font-weight: 600; }
.input { min-height: 52px; border-radius: 16px; padding: 0 16px; background: rgba(8,10,16,0.96); border: 1px solid rgba(255,255,255,0.08); color: #eef2ff; outline: none; }
.input:focus { border-color: rgba(47,115,255,0.6); box-shadow: 0 0 0 4px rgba(47,115,255,0.14); }
.input--textarea { min-height: 200px; padding: 14px 16px; resize: vertical; }
.toggleRow { grid-column: 1 / -1; display: inline-grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.toggle { min-height: 48px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.72); cursor: pointer; font-weight: 700; }
.toggle.active { color: #fff; border-color: rgba(47,115,255,0.34); background: rgba(47,115,255,0.18); }
.actions { display: flex; justify-content: flex-start; }
.primaryBtn { min-height: 48px; border-radius: 16px; padding: 0 18px; border: 1px solid rgba(47,115,255,0.4); background: linear-gradient(135deg, #2f73ff, #5a93ff); color: #fff; font-weight: 700; cursor: pointer; box-shadow: 0 10px 22px rgba(47,115,255,0.24); }
.primaryBtn:disabled { opacity: 0.65; cursor: not-allowed; }
.successText { margin: 16px 0 0; color: #91f2b0; }
.errorText { margin: 16px 0 0; color: #ff9d9d; }
@media (max-width: 1080px) { .pageGrid { grid-template-columns: 1fr; } }
@media (max-width: 780px) { .panelHeader { flex-direction: column; align-items: flex-start; } .vacancyForm, .toggleRow { grid-template-columns: 1fr; } .field--full, .summaryBox, .actions { grid-column: auto; } .field--narrow { max-width: none; } }
</style>
