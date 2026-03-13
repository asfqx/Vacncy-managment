<template>
  <DashboardShell
    :title="pageTitle"
    :subtitle="pageSubtitle"
    :role-label="roleLabel"
    :nav-items="navItems"
    :primary-action="primaryAction"
    :secondary-action="secondaryAction"
    :home-path="homePath"
    :avatar-letter="avatarLetter"
  >
    <InlineLoader v-if="loading" text="Загружаем профиль..." />
    <div v-else-if="error" class="errorPanel">{{ error }}</div>

    <template v-else>
      <section class="heroCard">
        <div class="heroCard__identity">
          <div class="heroCard__avatarWrap">
            <img v-if="avatarImageSrc" :src="avatarImageSrc" alt="Аватар" class="heroCard__avatarImage" />
            <div v-else class="heroCard__avatar">{{ avatarLetter }}</div>

            <label class="avatarUploadBtn">
              <input class="avatarUploadInput" type="file" accept="image/png,image/jpeg,image/webp" @change="onAvatarSelected" />
              {{ avatarUploading ? "Загрузка..." : "Обновить фото" }}
            </label>
          </div>

          <div>
            <p class="heroCard__role">{{ roleLabel }}</p>
            <h2 class="heroCard__name">{{ displayName }}</h2>
            <p class="heroCard__login">@{{ profile.username }}</p>
            <p v-if="avatarMessage" class="avatarMessage">{{ avatarMessage }}</p>
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
        <div class="contentStack">
          <article class="panel formPanel">
            <div class="panelIntro">
              <div>
                <p class="panelEyebrow">Личные данные</p>
                <h3 class="panel__title">Редактирование профиля</h3>
              </div>
              <p class="panelHint">Изменения применяются сразу к аккаунту.</p>
            </div>

            <form class="formGrid" @submit.prevent="submitProfile">
              <label class="field field--wide">
                <span>Email</span>
                <div class="inputActionWrap">
                  <input
                    v-model="form.email"
                    class="input input--withAction"
                    type="email"
                    placeholder="you@example.com"
                  />
                  <button
                    v-if="profile && !profile.email_confirmed"
                    class="inputActionBtn"
                    type="button"
                    :disabled="emailConfirmLoading || !form.email.trim()"
                    @click="requestEmailConfirmation"
                  >
                    {{ emailConfirmLoading ? "\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430..." : "\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c \u043f\u043e\u0447\u0442\u0443" }}
                  </button>
                </div>
              </label>
              <label class="field">
                <span>Username</span>
                <input v-model="form.username" class="input" type="text" placeholder="username" />
              </label>

              <label class="field">
                <span>{{ employer ? "Имя владельца или бренд" : "ФИО" }}</span>
                <input
                  v-model="form.fio"
                  class="input"
                  type="text"
                  :placeholder="employer ? 'Например, Иван Петров или HR Team' : 'Иванов Иван Иванович'"
                />
              </label>

              <div class="formActions">
                <button class="primaryBtn" type="submit" :disabled="saving">
                  {{ saving ? "Сохраняем..." : "Сохранить изменения" }}
                </button>
              </div>
            </form>

            <p v-if="successMessage" class="successText">{{ successMessage }}</p>
            <p v-if="formError" class="errorText">{{ formError }}</p>
          </article>

          <article v-if="employer" class="panel formPanel companyCard">
            <div class="panelIntro">
              <div>
                <p class="panelEyebrow">Компания</p>
                <h3 class="panel__title">{{ hasCompany ? "Карточка компании" : "Создание компании" }}</h3>
              </div>
              <p class="panelHint">
                {{ hasCompany ? "Эти данные увидят кандидаты в вакансиях и профиле." : "Сначала создайте компанию, чтобы публиковать вакансии от имени организации." }}
              </p>
            </div>

            <form class="formGrid" @submit.prevent="submitCompany">
              <label class="field field--wide">
                <span>Название компании</span>
                <input v-model="companyForm.title" class="input" type="text" placeholder="ООО Ромашка" />
              </label>

              <label class="field">
                <span>Сайт</span>
                <input v-model="companyForm.website" class="input" type="url" placeholder="https://company.ru" />
              </label>

              <label class="field">
                <span>Размер компании</span>
                <input v-model.number="companyForm.company_size" class="input" type="number" min="0" placeholder="50" />
              </label>

              <label class="field field--full">
                <span>Описание</span>
                <textarea
                  v-model="companyForm.description"
                  class="input input--textarea"
                  placeholder="Коротко расскажите о компании, продукте и команде."
                  rows="5"
                />
              </label>

              <div class="formActions">
                <button class="primaryBtn" type="submit" :disabled="companySaving">
                  {{ companySaving ? (hasCompany ? "Обновляем..." : "Создаем...") : (hasCompany ? "Сохранить компанию" : "Создать компанию") }}
                </button>
              </div>
            </form>

            <p v-if="companySuccessMessage" class="successText">{{ companySuccessMessage }}</p>
            <p v-if="companyError" class="errorText">{{ companyError }}</p>
          </article>
        </div>

        <div class="sideStack">
          <article class="panel securityCard">
            <div class="panelIntro panelIntro--compact">
              <div>
                <p class="panelEyebrow">Безопасность</p>
                <h3 class="panel__title">Пароль и доступ</h3>
              </div>
            </div>

            <p class="securityText">
              Пароль обновляется через подтверждение по email, чтобы не выбивать пользователя из текущей сессии.
            </p>

            <button class="secondaryBtn secondaryBtn--full" type="button" :disabled="passwordLoading" @click="startPasswordReset">
              {{ passwordLoading ? "Отправляем код..." : "Обновить пароль" }}
            </button>
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
        </div>
      </section>
    </template>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { authApi } from "../api/auth";
import { companyApi } from "../api/company";
import { usersApi } from "../api/users";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import { getRoleLabel, getUserRoleFromToken, isAdminRole, isEmployerRole } from "../utils/auth";

const router = useRouter();
const role = getUserRoleFromToken();
const employer = isEmployerRole(role);
const profile = ref(null);
const loading = ref(true);
const saving = ref(false);
const companySaving = ref(false);
const passwordLoading = ref(false);
const emailConfirmLoading = ref(false);
const avatarUploading = ref(false);
const error = ref("");
const formError = ref("");
const companyError = ref("");
const successMessage = ref("");
const companySuccessMessage = ref("");
const avatarMessage = ref("");
const avatarPreviewUrl = ref("");
const persistedAvatarUrl = ref("");

const form = reactive({
  email: "",
  username: "",
  fio: "",
});

const companyForm = reactive({
  title: "",
  website: "",
  company_size: null,
  description: "",
});

const roleLabel = computed(() => getRoleLabel(profile.value?.role || role));
const pageTitle = computed(() => (employer ? "Профиль работодателя" : "Профиль кандидата"));
const pageSubtitle = computed(() => (
  employer
    ? "Управляйте аккаунтом работодателя, безопасностью и публичной карточкой компании в одном месте."
    : "Обновляйте личные данные, следите за безопасностью и активностью аккаунта."
));
const homePath = computed(() => "/home");
const hasCompany = computed(() => Boolean(profile.value?.company));
const displayName = computed(() => {
  if (employer && hasCompany.value) return profile.value.company.title;
  return profile.value?.fio || profile.value?.username || "Профиль";
});
const avatarLetter = computed(() => {
  const nameSource = displayName.value || roleLabel.value || "П";
  return String(nameSource).trim().slice(0, 1).toUpperCase();
});
const primaryAction = computed(() => (
  employer
    ? { to: "/employer/vacancies/create", label: "Создать вакансию" }
    : { to: "/candidate/resume", label: "Создать резюме" }
));
const secondaryAction = computed(() => (
  employer && isAdminRole(role) ? { to: "/vacancies", label: "Страница кандидата" } : null
));
const navItems = computed(() => (
  employer
    ? [
        { to: "/home", label: "Главная" },
        { to: "/employer/resumes", label: "Поиск резюме" },
        { to: "/employer/vacancies", label: "Мои вакансии" },
        { to: "/employer/applications", label: "Отклики" },
        { to: "/employer/vacancies/create", label: "Создать вакансию" },
        { to: "/profile", label: "Профиль" },
      ]
    : [
        { to: "/home", label: "Главная" },
        { to: "/vacancies", label: "Поиск вакансий" },
        { to: "/candidate/applications", label: "Мои отклики" },
        { to: "/candidate/resume", label: "Мои резюме" },
        { to: "/profile", label: "Профиль" },
      ]
));
const avatarImageSrc = computed(() => avatarPreviewUrl.value || buildAvatarUrl(profile.value?.avatar_url));

function buildAvatarUrl(objectName) {
  if (!objectName) return "";
  const baseUrl = (import.meta.env.VITE_S3_PUBLIC_BASE_URL || "http://localhost:9000").replace(/\/$/, "");
  const normalizedPath = String(objectName)
    .split("/")
    .map((part) => encodeURIComponent(part))
    .join("/");
  return `${baseUrl}/avatars/${normalizedPath}`;
}

function extractObjectName(uploadUrl) {
  try {
    const url = new URL(uploadUrl);
    const marker = "/avatars/";
    const index = url.pathname.indexOf(marker);
    if (index === -1) return "";
    return decodeURIComponent(url.pathname.slice(index + marker.length));
  } catch {
    return "";
  }
}
function syncProfileForm() {
  form.email = profile.value?.email || "";
  form.username = profile.value?.username || "";
  form.fio = profile.value?.fio || "";
}

function syncCompanyForm() {
  companyForm.title = profile.value?.company?.title || "";
  companyForm.website = profile.value?.company?.website || "";
  companyForm.description = profile.value?.company?.description || "";
  companyForm.company_size = profile.value?.company?.company_size ?? null;
}

function formatDate(value) {
  if (!value) return "Нет данных";
  try {
    return new Date(value).toLocaleString("ru-RU");
  } catch {
    return value;
  }
}

async function loadProfile() {
  loading.value = true;
  error.value = "";

  try {
    const userProfile = await usersApi.getMe();
    profile.value = {
      ...userProfile,
      company: null,
    };

    if (isEmployerRole(userProfile.role)) {
      try {
        const company = await companyApi.getMine();
        profile.value.company = company;
      } catch (companyErrorResponse) {
        if (companyErrorResponse?.response?.status !== 404) throw companyErrorResponse;
      }
    }

    syncProfileForm();
    syncCompanyForm();
  } catch (e) {
    const status = e?.response?.status;
    if (status === 401) error.value = "Сессия истекла. Войдите снова.";
    else if (status === 404) error.value = "Профиль не найден.";
    else error.value = "Не удалось загрузить профиль.";
  } finally {
    loading.value = false;
  }
}

async function onAvatarSelected(event) {
  const file = event.target.files?.[0];
  avatarMessage.value = "";
  formError.value = "";

  if (!file) return;
  if (!file.type.startsWith("image/")) {
    avatarMessage.value = "Выберите изображение PNG, JPG или WEBP.";
    return;
  }

  avatarUploading.value = true;

  try {
    const previewUrl = URL.createObjectURL(file);
    avatarPreviewUrl.value = previewUrl;

    const { upload_url } = await usersApi.getAvatarUploadUrl();
    const uploadResponse = await fetch(upload_url, {
      method: "PUT",
      body: file,
      headers: {
        "Content-Type": file.type || "image/png",
      },
    });

    const objectName = extractObjectName(upload_url);
    if (!objectName) throw new Error("Не удалось определить путь до файла.");

    await usersApi.updateMe({ avatar_url: objectName });
    avatarMessage.value = "Аватар обновлен.";
    avatarPreviewUrl.value = "";
    await loadProfile();
  } catch {
    avatarMessage.value = "Не удалось обновить аватар.";
  } finally {
    avatarUploading.value = false;
    event.target.value = "";
  }
}

async function submitProfile() {
  saving.value = true;
  formError.value = "";
  successMessage.value = "";

  try {
    await usersApi.updateMe({
      email: form.email.trim(),
      username: form.username.trim(),
      fio: form.fio.trim(),
    });

    successMessage.value = "Профиль успешно обновлен.";
    avatarPreviewUrl.value = "";
    await loadProfile();
  } catch (e) {
    const status = e?.response?.status;
    if (status === 409) formError.value = "Этот email уже используется.";
    else if (status === 422) formError.value = "Проверьте корректность введенных данных.";
    else formError.value = "Не удалось обновить профиль.";
  } finally {
    saving.value = false;
  }
}

async function submitCompany() {
  companySaving.value = true;
  companyError.value = "";
  companySuccessMessage.value = "";

  try {
    const payload = {
      title: companyForm.title.trim(),
      website: companyForm.website.trim() || null,
      company_size: Number.isFinite(companyForm.company_size) ? companyForm.company_size : 0,
      description: companyForm.description.trim() || null,
    };

    if (hasCompany.value) await companyApi.updateMine(payload);
    else await companyApi.createMine(payload);

    companySuccessMessage.value = hasCompany.value ? "Компания успешно обновлена." : "Компания успешно создана.";
    avatarPreviewUrl.value = "";
    await loadProfile();
  } catch (e) {
    const status = e?.response?.status;
    if (status === 409) companyError.value = "Компания с таким названием уже существует или уже привязана к аккаунту.";
    else if (status === 422) companyError.value = "Проверьте корректность данных компании.";
    else companyError.value = "Не удалось сохранить компанию.";
  } finally {
    companySaving.value = false;
  }
}

async function startPasswordReset() {
  passwordLoading.value = true;
  formError.value = "";
  successMessage.value = "";
  try {
    await authApi.passwordResetRequest(profile.value.email);
    await router.push({ path: "/password-reset/confirm", query: { email: profile.value.email } });
  } catch (e) {
    const status = e?.response?.status;
    if (status === 429) formError.value = "\u0421\u043b\u0438\u0448\u043a\u043e\u043c \u0447\u0430\u0441\u0442\u043e. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043f\u043e\u0437\u0436\u0435.";
    else formError.value = "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0430\u0440\u043e\u043b\u044f.";
  } finally {
    passwordLoading.value = false;
  }
}
async function requestEmailConfirmation() {
  emailConfirmLoading.value = true;
  formError.value = "";
  successMessage.value = "";
  try {
    const email = form.email.trim();
    await authApi.emailConfirmRequest(email);
    await router.push({ path: "/email-confirm", query: { email } });
  } catch (e) {
    const status = e?.response?.status;
    if (status === 429) formError.value = "\u0421\u043b\u0438\u0448\u043a\u043e\u043c \u0447\u0430\u0441\u0442\u043e. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043f\u043e\u0437\u0436\u0435.";
    else if (status === 400) formError.value = "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435 \u0434\u043b\u044f \u044d\u0442\u043e\u0433\u043e email.";
    else formError.value = "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u043f\u0438\u0441\u044c\u043c\u043e \u0434\u043b\u044f \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f \u043f\u043e\u0447\u0442\u044b.";
  } finally {
    emailConfirmLoading.value = false;
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
.heroCard__avatarWrap { display: grid; gap: 10px; justify-items: center; }
.heroCard__avatar,
.heroCard__avatarImage { width: 92px; height: 92px; border-radius: 28px; }
.heroCard__avatar {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #ff7a59, #2f73ff);
  color: #fff;
  font-size: 34px;
  font-weight: 800;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
}
.heroCard__avatarImage { object-fit: cover; border: 1px solid rgba(255,255,255,0.12); }
.avatarUploadBtn {
  min-height: 36px;
  padding: 0 12px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.9);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}
.avatarUploadInput { display: none; }
.avatarMessage { margin: 10px 0 0; color: rgba(255,255,255,0.72); }
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
.statusBadge--action {
  cursor: pointer;
  color: #fff;
  font-weight: 700;
}
.statusBadge--action:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.statusBadge.success { color: #91f2b0; border-color: rgba(145, 242, 176, 0.35); background: rgba(20, 66, 40, 0.22); }
.statusBadge.muted { color: rgba(255, 255, 255, 0.76); }
.contentGrid { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.8fr); gap: 18px; }
.contentStack,
.sideStack { display: grid; gap: 18px; align-content: start; }
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
.panelHint { margin: 0; max-width: 280px; color: rgba(255, 255, 255, 0.6); line-height: 1.5; text-align: right; }
.formGrid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.field { display: grid; gap: 8px; }
.field--wide,
.field--full,
.formActions { grid-column: 1 / -1; }
.field span { color: rgba(255, 255, 255, 0.7); font-size: 13px; font-weight: 600; }
.inputActionWrap {
  position: relative;
  display: flex;
  align-items: stretch;
  width: 100%;
}
.input {
  width: 100%;
  box-sizing: border-box;
  min-height: 52px;
  border-radius: 16px;
  padding: 0 16px;
  background: rgba(8, 10, 16, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #eef2ff;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}
.input--withAction {
  min-width: 0;
  padding-right: 186px;
}
.input:focus { border-color: rgba(47, 115, 255, 0.6); box-shadow: 0 0 0 4px rgba(47, 115, 255, 0.14); }
.input--textarea { min-height: 136px; padding: 14px 16px; resize: vertical; }
.inputActionBtn {
  position: absolute;
  right: 8px;
  top: 7px;
  bottom: 7px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  padding: 0 12px;
  border: 1px solid rgba(47, 115, 255, 0.35);
  background: linear-gradient(135deg, rgba(47, 115, 255, 0.95), rgba(90, 147, 255, 0.95));
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  z-index: 1;
}
.inputActionBtn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.formActions { display: flex; justify-content: flex-start; padding-top: 6px; }
.primaryBtn,
.secondaryBtn {
  min-height: 46px;
  border-radius: 16px;
  padding: 0 18px;
  color: #fff;
  cursor: pointer;
  font-weight: 700;
  transition: transform 0.2s ease, opacity 0.2s ease, background 0.2s ease;
}
.primaryBtn {
  border: 1px solid rgba(47, 115, 255, 0.4);
  background: linear-gradient(135deg, #2f73ff, #5a93ff);
  box-shadow: 0 10px 22px rgba(47, 115, 255, 0.24);
}
.secondaryBtn { border: 1px solid rgba(255, 255, 255, 0.12); background: rgba(255, 255, 255, 0.03); }
.secondaryBtn--full { width: 100%; }
.primaryBtn:hover,
.secondaryBtn:hover { transform: translateY(-1px); }
.primaryBtn:disabled,
.secondaryBtn:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }
.successText { margin: 14px 0 0; color: #91f2b0; }
.errorText,
.errorPanel { color: #ff9d9d; }
.securityText { margin: 0 0 16px; color: rgba(255, 255, 255, 0.7); line-height: 1.6; }
.details { display: grid; gap: 14px; margin: 0; }
.details__row { display: grid; gap: 6px; padding: 14px 0; border-top: 1px solid rgba(255, 255, 255, 0.06); }
.details__row:first-child { padding-top: 0; border-top: none; }
.details dt { color: rgba(255, 255, 255, 0.58); font-size: 13px; }
.details dd { margin: 0; font-size: 17px; line-height: 1.45; }
.errorPanel { padding: 18px; }
@media (max-width: 1100px) {
  .contentGrid { grid-template-columns: 1fr; }
  .panelHint { max-width: none; text-align: left; }
}
@media (max-width: 780px) {
  .heroCard,
  .panelIntro { flex-direction: column; align-items: flex-start; }
  .heroCard__statusWrap { justify-content: flex-start; }
  .formGrid { grid-template-columns: 1fr; }
  .input--withAction { padding-right: 16px; }
  .inputActionWrap { display: grid; gap: 8px; }
  .inputActionBtn {
    position: static;
    width: 100%;
  }
  .field--wide,
  .field--full,
  .formActions { grid-column: auto; }
}
</style>
