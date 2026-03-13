<template>
  <DashboardShell
    title="Мои резюме"
    subtitle="Соберите сильное резюме и поддерживайте его в актуальном состоянии."
    role-label="Кандидат"
    :nav-items="navItems"
    :primary-action="{ to: '/candidate/resume', label: 'Мои резюме' }"
    :secondary-action="secondaryAction"
    home-path="/home"
    avatar-letter="К"
  >
    <template #aside>
      <UiCard title="Образование" :subtitle="String(resume?.educations?.length || 0)" />
      <UiCard title="Опыт" :subtitle="String(resume?.experiences?.length || 0)" />
    </template>

    <InlineLoader v-if="loading" text="Загружаем резюме..." />
    <div v-else class="pageGrid">
      <article class="panel formPanel">
        <div class="panelHeader">
          <div>
            <p class="eyebrow">Основное</p>
            <h2 class="title">Профиль резюме</h2>
          </div>
          <span class="chip">{{ resume ? 'Черновик сохранен' : 'Новое резюме' }}</span>
        </div>

        <form class="formGrid" @submit.prevent="saveResume">
          <label class="field field--full">
            <span>Заголовок</span>
            <input v-model="resumeForm.title" class="input" type="text" placeholder="Frontend разработчик Vue.js" />
          </label>

          <label class="field field--full">
            <span>О себе</span>
            <textarea
              v-model="resumeForm.about_me"
              class="input input--textarea"
              rows="7"
              placeholder="Коротко опишите свой опыт, сильные стороны и стек."
            />
          </label>

          <label class="field">
            <span>Ожидаемая зарплата</span>
            <input v-model.number="resumeForm.salary" class="input" type="number" min="0" placeholder="180000" />
          </label>

          <label class="field field--narrow">
            <span>Валюта</span>
            <AppSelect v-model="resumeForm.currency" :options="currencyOptions" />
          </label>

          <label class="field field--narrow">
            <span>Пол</span>
            <AppSelect v-model="resumeForm.gender" :options="genderOptions" />
          </label>

          <label class="field field--date">
            <span>Дата рождения</span>
            <AppDateInput v-model="resumeForm.birth_date" />
          </label>

          <div class="actions">
            <button class="primaryBtn" type="submit" :disabled="savingResume">
              {{ savingResume ? 'Сохраняем...' : 'Сохранить резюме' }}
            </button>
          </div>
        </form>

        <p v-if="resumeSuccess" class="successText">{{ resumeSuccess }}</p>
        <p v-if="resumeError" class="errorText">{{ resumeError }}</p>
      </article>

      <article class="panel previewPanel">
        <div class="previewHeader">
          <p class="eyebrow">Предпросмотр</p>
        </div>
        <ResumeCard v-if="previewResume" :resume="previewResume" :interactive="Boolean(resume?.uuid)" />
        <p v-else class="mutedText">Заполните основные поля, чтобы увидеть карточку резюме.</p>
      </article>

      <article class="panel stackPanel">
        <div class="panelHeader">
          <div>
            <p class="eyebrow">Образование</p>
          </div>
        </div>

        <p v-if="!resume" class="mutedText">Сначала сохраните основное резюме, затем добавьте образование.</p>

        <form v-else class="stackForm" @submit.prevent="addEducation">
          <label class="field">
            <span>Учебное заведение</span>
            <input v-model="educationForm.institution" class="input" type="text" placeholder="МГУ" />
          </label>
          <label class="field field--narrow">
            <span>Уровень</span>
            <AppSelect v-model="educationForm.level" :options="educationLevelOptions" />
          </label>
          <label class="field">
            <span>Специализация</span>
            <input v-model="educationForm.specialization" class="input" type="text" placeholder="Прикладная информатика" />
          </label>
          <label class="field field--date">
            <span>Начало</span>
            <AppDateInput v-model="educationForm.start_date" />
          </label>
          <label class="field field--date">
            <span>Окончание</span>
            <AppDateInput v-model="educationForm.end_date" :disabled="educationForm.is_current" />
          </label>
          <label class="checkRow checkRow--inline">
            <input v-model="educationForm.is_current" class="checkInput" type="checkbox" />
            <span class="checkMark"></span>
            <span>Учусь сейчас</span>
          </label>
          <label class="field field--full">
            <span>Описание</span>
            <textarea v-model="educationForm.description" class="input input--textarea" rows="4" placeholder="Достижения, курсы, фокус обучения." />
          </label>
          <div class="actions">
            <button class="secondaryBtn" type="submit" :disabled="savingEducation">
              {{ savingEducation ? 'Добавляем...' : 'Добавить образование' }}
            </button>
          </div>
        </form>

        <div v-if="resume?.educations?.length" class="itemList">
          <article v-for="item in resume.educations" :key="item.uuid" class="itemCard">
            <div>
              <h3 class="itemTitle">{{ item.institution }}</h3>
              <p class="itemMeta">{{ educationLevelLabel(item.level) }}{{ item.specialization ? ` · ${item.specialization}` : '' }}</p>
              <p class="itemMeta">{{ formatPeriod(item.start_date, item.end_date, item.is_current) }}</p>
              <p v-if="item.description" class="itemText">{{ item.description }}</p>
            </div>
            <button class="dangerBtn" type="button" :disabled="deletingEducationUuid === item.uuid" @click="removeEducation(item.uuid)">
              {{ deletingEducationUuid === item.uuid ? 'Удаляем...' : 'Удалить' }}
            </button>
          </article>
        </div>
      </article>

      <article class="panel stackPanel">
        <div class="panelHeader">
          <div>
            <p class="eyebrow">Опыт работы</p>
          </div>
        </div>

        <p v-if="!resume" class="mutedText">Сначала сохраните основное резюме, затем добавьте опыт.</p>

        <form v-else class="stackForm" @submit.prevent="addExperience">
          <label class="field">
            <span>Компания</span>
            <input v-model="experienceForm.company_name" class="input" type="text" placeholder="ООО Продукт" />
          </label>
          <label class="field">
            <span>Должность</span>
            <input v-model="experienceForm.position" class="input" type="text" placeholder="Frontend разработчик" />
          </label>
          <label class="field field--date">
            <span>Начало</span>
            <AppDateInput v-model="experienceForm.start_date" />
          </label>
          <label class="field field--date">
            <span>Окончание</span>
            <AppDateInput v-model="experienceForm.end_date" :disabled="experienceForm.is_current" />
          </label>
          <label class="checkRow checkRow--inline">
            <input v-model="experienceForm.is_current" class="checkInput" type="checkbox" />
            <span class="checkMark"></span>
            <span>Работаю сейчас</span>
          </label>
          <label class="field field--full">
            <span>Описание</span>
            <textarea v-model="experienceForm.description" class="input input--textarea" rows="4" placeholder="Основные задачи, достижения, стек." />
          </label>
          <div class="actions">
            <button class="secondaryBtn" type="submit" :disabled="savingExperience">
              {{ savingExperience ? 'Добавляем...' : 'Добавить опыт' }}
            </button>
          </div>
        </form>

        <div v-if="resume?.experiences?.length" class="itemList">
          <article v-for="item in resume.experiences" :key="item.uuid" class="itemCard">
            <div>
              <h3 class="itemTitle">{{ item.position }}</h3>
              <p class="itemMeta">{{ item.company_name }}</p>
              <p class="itemMeta">{{ formatPeriod(item.start_date, item.end_date, item.is_current) }}</p>
              <p v-if="item.description" class="itemText">{{ item.description }}</p>
            </div>
            <button class="dangerBtn" type="button" :disabled="deletingExperienceUuid === item.uuid" @click="removeExperience(item.uuid)">
              {{ deletingExperienceUuid === item.uuid ? 'Удаляем...' : 'Удалить' }}
            </button>
          </article>
        </div>
      </article>
    </div>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { getUserRoleFromToken, isAdminRole } from "../utils/auth";
import { RouterLink } from "vue-router";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import ResumeCard from "../components/resumes/ResumeCard.vue";
import AppDateInput from "../components/ui/AppDateInput.vue";
import AppSelect from "../components/ui/AppSelect.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import UiCard from "../components/ui/UiCard.vue";
import { resumeApi } from "../api/resume";

const role = getUserRoleFromToken();
const secondaryAction = computed(() => (isAdminRole(role) ? { to: "/employer/vacancies", label: "Страница компании" } : null));
const navItems = [
  { to: "/home", label: "Главная" },
  { to: "/vacancies", label: "Поиск вакансий" },
  { to: "/candidate/applications", label: "Мои отклики" },
  { to: "/candidate/resume", label: "Мои резюме" },
  { to: "/profile", label: "Профиль" },
];

const currencyOptions = [
  { value: "RUB", label: "RUB" },
  { value: "USD", label: "USD" },
  { value: "EUR", label: "EUR" },
];

const genderOptions = [
  { value: "", label: "Не указан" },
  { value: "MALE", label: "Мужчина" },
  { value: "FEMALE", label: "Женщина" },
];

const educationLevelOptions = [
  { value: "SECONDARY", label: "Среднее" },
  { value: "SECONDARY_SPECIAL", label: "Среднее специальное" },
  { value: "INCOMPLETE_HIGHER", label: "Неоконченное высшее" },
  { value: "BACHELOR", label: "Бакалавр" },
  { value: "SPECIALIST", label: "Специалист" },
  { value: "MASTER", label: "Магистр" },
  { value: "POSTGRADUATE", label: "Аспирантура" },
  { value: "DOCTORATE", label: "Докторантура" },
];

const educationLevelMap = Object.fromEntries(educationLevelOptions.map((item) => [item.value, item.label]));

const loading = ref(true);
const savingResume = ref(false);
const savingEducation = ref(false);
const savingExperience = ref(false);
const deletingEducationUuid = ref("");
const deletingExperienceUuid = ref("");
const resume = ref(null);
const resumeSuccess = ref("");
const resumeError = ref("");

const resumeForm = reactive({
  title: "",
  about_me: "",
  salary: null,
  currency: "RUB",
  gender: "",
  birth_date: "",
});

const educationForm = reactive({
  institution: "",
  level: "BACHELOR",
  specialization: "",
  start_date: "",
  end_date: "",
  description: "",
  is_current: false,
});

const experienceForm = reactive({
  company_name: "",
  position: "",
  start_date: "",
  end_date: "",
  description: "",
  is_current: false,
});

const previewResume = computed(() => {
  if (!resume.value && !resumeForm.title.trim() && !resumeForm.about_me.trim()) return null;

  return {
    uuid: resume.value?.uuid || "preview",
    title: resumeForm.title.trim(),
    about_me: resumeForm.about_me.trim(),
    salary: Number.isFinite(resumeForm.salary) ? resumeForm.salary : null,
    currency: resumeForm.currency || null,
    gender: resumeForm.gender || null,
    birth_date: resumeForm.birth_date || null,
    educations: resume.value?.educations || [],
    experiences: resume.value?.experiences || [],
  };
});

function syncResumeForm(data) {
  resumeForm.title = data?.title || "";
  resumeForm.about_me = data?.about_me || "";
  resumeForm.salary = Number.isFinite(data?.salary) ? data.salary : null;
  resumeForm.currency = data?.currency || "RUB";
  resumeForm.gender = data?.gender || "";
  resumeForm.birth_date = data?.birth_date || "";
}

function resetEducationForm() {
  educationForm.institution = "";
  educationForm.level = "BACHELOR";
  educationForm.specialization = "";
  educationForm.start_date = "";
  educationForm.end_date = "";
  educationForm.description = "";
  educationForm.is_current = false;
}

function resetExperienceForm() {
  experienceForm.company_name = "";
  experienceForm.position = "";
  experienceForm.start_date = "";
  experienceForm.end_date = "";
  experienceForm.description = "";
  experienceForm.is_current = false;
}

async function loadResume() {
  loading.value = true;
  resumeError.value = "";

  try {
    const data = await resumeApi.getMine();
    resume.value = data;
    syncResumeForm(data);
  } catch (e) {
    if (e?.response?.status === 404) {
      resume.value = null;
      syncResumeForm(null);
    } else {
      resumeError.value = "Не удалось загрузить резюме.";
    }
  } finally {
    loading.value = false;
  }
}

async function saveResume() {
  savingResume.value = true;
  resumeSuccess.value = "";
  resumeError.value = "";

  try {
    const payload = {
      title: resumeForm.title.trim(),
      about_me: resumeForm.about_me.trim(),
      salary: Number.isFinite(resumeForm.salary) ? resumeForm.salary : null,
      currency: resumeForm.currency || null,
      gender: resumeForm.gender || null,
      birth_date: resumeForm.birth_date || null,
    };

    resume.value = await resumeApi.upsertMine(payload);
    syncResumeForm(resume.value);
    resumeSuccess.value = "Резюме сохранено.";
  } catch (e) {
    if (e?.response?.status === 422) resumeError.value = "Проверьте корректность заполнения формы.";
    else resumeError.value = "Не удалось сохранить резюме.";
  } finally {
    savingResume.value = false;
  }
}

async function addEducation() {
  if (!resume.value?.uuid) return;

  savingEducation.value = true;
  resumeError.value = "";

  try {
    await resumeApi.createEducation(resume.value.uuid, {
      institution: educationForm.institution.trim(),
      level: educationForm.level,
      specialization: educationForm.specialization.trim() || null,
      start_date: educationForm.start_date || null,
      end_date: educationForm.is_current ? null : educationForm.end_date || null,
      description: educationForm.description.trim() || null,
      is_current: educationForm.is_current,
    });
    resetEducationForm();
    await loadResume();
  } catch {
    resumeError.value = "Не удалось добавить образование.";
  } finally {
    savingEducation.value = false;
  }
}

async function addExperience() {
  if (!resume.value?.uuid) return;

  savingExperience.value = true;
  resumeError.value = "";

  try {
    await resumeApi.createExperience(resume.value.uuid, {
      company_name: experienceForm.company_name.trim(),
      position: experienceForm.position.trim(),
      start_date: experienceForm.start_date,
      end_date: experienceForm.is_current ? null : experienceForm.end_date || null,
      description: experienceForm.description.trim() || null,
      is_current: experienceForm.is_current,
    });
    resetExperienceForm();
    await loadResume();
  } catch {
    resumeError.value = "Не удалось добавить опыт работы.";
  } finally {
    savingExperience.value = false;
  }
}

async function removeEducation(uuid) {
  if (!resume.value?.uuid) return;

  deletingEducationUuid.value = uuid;
  resumeError.value = "";

  try {
    await resumeApi.deleteEducation(resume.value.uuid, uuid);
    await loadResume();
  } catch {
    resumeError.value = "Не удалось удалить образование.";
  } finally {
    deletingEducationUuid.value = "";
  }
}

async function removeExperience(uuid) {
  if (!resume.value?.uuid) return;

  deletingExperienceUuid.value = uuid;
  resumeError.value = "";

  try {
    await resumeApi.deleteExperience(resume.value.uuid, uuid);
    await loadResume();
  } catch {
    resumeError.value = "Не удалось удалить опыт работы.";
  } finally {
    deletingExperienceUuid.value = "";
  }
}

function educationLevelLabel(value) {
  return educationLevelMap[value] || value;
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

onMounted(loadResume);
</script>

<style scoped>
.pageGrid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.95fr);
  gap: 18px;
}

.panel {
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
  padding: 24px;
}

.formPanel,
.previewPanel {
  height: 100%;
}

.previewPanel {
  display: flex;
  flex-direction: column;
}

.stackPanel {
  grid-column: 1 / -1;
}

.panelHeader,
.previewHeader {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.title {
  margin: 0;
  font-size: 28px;
  line-height: 1.1;
}

.title--small {
  font-size: 24px;
}

.chip,
.previewLink {
  min-height: 36px;
  padding: 0 12px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
}

.chip {
  background: rgba(47, 115, 255, 0.16);
  border: 1px solid rgba(47, 115, 255, 0.32);
  color: #dce7ff;
}

.previewLink {
  text-decoration: none;
  color: #dce7ff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
}

.formGrid,
.stackForm {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.field {
  display: grid;
  gap: 8px;
}

.field--full,
.actions {
  grid-column: 1 / -1;
}

.field--narrow,
.field--date {
  min-width: 0;
}

.field span,
.checkRow span {
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  font-weight: 600;
}

.input {
  min-height: 52px;
  border-radius: 16px;
  padding: 0 16px;
  background: rgba(8, 10, 16, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #eef2ff;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input:focus {
  border-color: rgba(47, 115, 255, 0.55);
  box-shadow: 0 0 0 4px rgba(47, 115, 255, 0.14);
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.38);
}

.input--textarea {
  min-height: 132px;
  padding: 14px 16px;
  resize: none;
}

.actions {
  display: flex;
  justify-content: flex-start;
}

.primaryBtn,
.secondaryBtn,
.dangerBtn {
  min-height: 44px;
  padding: 0 16px;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
}

.primaryBtn {
  border: 1px solid rgba(47, 115, 255, 0.4);
  background: linear-gradient(135deg, #2f73ff, #5a93ff);
  color: #fff;
}

.secondaryBtn {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #fff;
}

.dangerBtn {
  border: 1px solid rgba(255, 113, 113, 0.35);
  background: rgba(255, 113, 113, 0.12);
  color: #ffb0b0;
}

.primaryBtn:disabled,
.secondaryBtn:disabled,
.dangerBtn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.checkRow {
  display: inline-flex;
  gap: 10px;
  align-items: center;
  min-height: 52px;
}

.checkRow--inline {
  align-self: end;
  padding: 0 4px 10px 2px;
}

.checkInput {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.checkMark {
  width: 20px;
  height: 20px;
  flex: 0 0 20px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.04);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.checkMark::after {
  content: "";
  width: 10px;
  height: 6px;
  border-left: 2px solid transparent;
  border-bottom: 2px solid transparent;
  transform: rotate(-45deg) translateY(-1px);
}

.checkInput:checked + .checkMark {
  background: linear-gradient(135deg, #2f73ff, #5a93ff);
  border-color: rgba(47, 115, 255, 0.55);
  box-shadow: 0 8px 20px rgba(47, 115, 255, 0.24);
}

.checkInput:checked + .checkMark::after {
  border-left-color: #fff;
  border-bottom-color: #fff;
}

.itemList {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.itemCard {
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  padding: 16px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.itemTitle {
  margin: 0;
  font-size: 18px;
}

.itemMeta,
.itemText,
.mutedText,
.successText,
.errorText {
  margin: 8px 0 0;
  line-height: 1.6;
}

.itemMeta,
.itemText,
.mutedText {
  color: rgba(255, 255, 255, 0.72);
}

.successText {
  color: #91f2b0;
}

.errorText {
  color: #ff9d9d;
}

@media (max-width: 1100px) {
  .pageGrid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 780px) {
  .formGrid,
  .stackForm {
    grid-template-columns: 1fr;
  }

  .itemCard,
  .panelHeader,
  .previewHeader {
    flex-direction: column;
    align-items: flex-start;
  }

  .checkRow--inline {
    padding-bottom: 0;
  }
}
</style>







