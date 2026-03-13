<template>
  <ConfirmTokenCard
    v-if="step === 1"
    :email="email"
    title="Сброс пароля"
    subtitle="Введите код из письма"
    hint="Код приходит на почту после запроса сброса пароля."
    token-label="Код из письма"
    confirm-text="Продолжить"
    :show-resend="true"
    resend-text="Отправить снова"
    :cooldown-seconds="60"
    :on-confirm="handleTokenSubmit"
    :on-resend="handleResend"
    bottom-link-text="Вернуться ко входу"
    bottom-link-to="/login"
  />

  <AuthCard
    v-else
    title="Новый пароль"
    subtitle="Введите новый пароль для входа в аккаунт"
  >
    <form class="form" @submit.prevent="submitNewPassword">
      <BaseInput
        v-model="newPassword"
        label="Новый пароль"
        type="password"
        placeholder="Минимум 8 символов"
        autocomplete="new-password"
        :error="fieldErrors.newPassword"
      />

      <BaseInput
        v-model="newPassword2"
        label="Повторите пароль"
        type="password"
        placeholder="Повторите новый пароль"
        autocomplete="new-password"
        :error="fieldErrors.newPassword2"
      />

      <BaseButton :loading="pwdLoading">Сменить пароль</BaseButton>

      <p v-if="pwdSuccess" class="success">{{ pwdSuccess }}</p>
      <p v-if="pwdError" class="error">{{ pwdError }}</p>

      <p class="hint-center">
        <button class="link-btn" type="button" @click="backToToken">Назад к коду</button>
      </p>
    </form>
  </AuthCard>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import ConfirmTokenCard from "../components/auth/ConfirmTokenCard.vue";
import AuthCard from "../components/ui/AuthCard.vue";
import BaseInput from "../components/ui/BaseInput.vue";
import BaseButton from "../components/ui/BaseButton.vue";
import { authApi } from "../api/auth";

const route = useRoute();
const router = useRouter();
const email = computed(() => String(route.query.email || "").trim());

const step = ref(1);
const savedToken = ref("");
const newPassword = ref("");
const newPassword2 = ref("");
const pwdLoading = ref(false);
const pwdError = ref("");
const pwdSuccess = ref("");
const fieldErrors = reactive({ newPassword: "", newPassword2: "" });

async function handleTokenSubmit(token) {
  savedToken.value = token;
  pwdError.value = "";
  step.value = 2;
}

async function handleResend() {
  try {
    await authApi.passwordResetRequest(email.value);
  } catch (e) {
    const status = e?.response?.status;
    if (status === 429) throw new Error("Слишком часто. Попробуйте позже.");
    throw new Error("Не удалось отправить код");
  }
}

function validatePassword() {
  fieldErrors.newPassword = "";
  fieldErrors.newPassword2 = "";
  pwdError.value = "";
  pwdSuccess.value = "";

  if (!savedToken.value) {
    pwdError.value = "Сначала введите код.";
    step.value = 1;
    return false;
  }

  if (!newPassword.value) fieldErrors.newPassword = "Введите новый пароль";
  else if (newPassword.value.length < 8) fieldErrors.newPassword = "Минимум 8 символов";

  if (!newPassword2.value) fieldErrors.newPassword2 = "Повторите пароль";
  else if (newPassword2.value !== newPassword.value) fieldErrors.newPassword2 = "Пароли не совпадают";

  return !fieldErrors.newPassword && !fieldErrors.newPassword2;
}

async function submitNewPassword() {
  if (!validatePassword()) return;

  pwdLoading.value = true;
  try {
    await authApi.passwordResetConfirm({
      email: email.value,
      token: savedToken.value,
      new_password: newPassword.value,
    });
    pwdSuccess.value = "Пароль успешно обновлен. Сейчас откроется вход.";
    setTimeout(() => router.push("/login"), 900);
  } catch (e) {
    const status = e?.response?.status;
    if (status === 400) pwdError.value = "Неверный или просроченный код";
    else if (status === 422) pwdError.value = "Проверьте корректность нового пароля";
    else pwdError.value = "Не удалось сменить пароль";
  } finally {
    pwdLoading.value = false;
  }
}

function backToToken() {
  pwdError.value = "";
  pwdSuccess.value = "";
  step.value = 1;
}
</script>

<style scoped>
.form { display: grid; gap: 12px; }
.success { margin: 6px 0 0; color: #7cff9b; font-size: 15px; }
.error { margin: 6px 0 0; color: #ff6b6b; font-size: 15px; }
.hint-center { margin-top: 10px; text-align: center; }
.link-btn { border: none; background: transparent; color: #ffffff; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.35); padding: 0; }
.link-btn:hover { border-bottom-color: rgba(255,255,255,0.9); }
</style>
