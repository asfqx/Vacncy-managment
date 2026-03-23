<template>
  <AuthCard
    title="Сброс пароля"
    subtitle="Введите email, мы отправим код для восстановления"
  >
    <form class="form" @submit.prevent="onSubmit">
      <BaseInput
        v-model="email"
        label="Email"
        type="email"
        placeholder="user@example.com"
        autocomplete="email"
        :error="fieldErrors.email"
      />

      <BaseButton :loading="loading">Отправить код</BaseButton>

      <p v-if="success" class="success">{{ success }}</p>
      <p v-if="error" class="error">{{ error }}</p>

      <p class="hint">
        Вспомнили пароль?
        <RouterLink class="link" to="/login">Войти</RouterLink>
      </p>
    </form>
  </AuthCard>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter, RouterLink } from "vue-router";
import AuthCard from "../components/ui/AuthCard.vue";
import BaseInput from "../components/ui/BaseInput.vue";
import BaseButton from "../components/ui/BaseButton.vue";
import { authApi } from "../api/auth";

const router = useRouter();
const email = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");
const fieldErrors = reactive({ email: "" });

function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function validate() {
  fieldErrors.email = "";
  error.value = "";
  success.value = "";

  const e = email.value.trim();
  if (!e) fieldErrors.email = "Введите email";
  else if (!isEmail(e)) fieldErrors.email = "Некорректный email";

  return !fieldErrors.email;
}

async function onSubmit() {
  if (!validate()) return;

  loading.value = true;
  try {
    await authApi.passwordResetRequest(email.value.trim());
    success.value = "Код отправлен на почту. Введите его на следующем шаге.";
    setTimeout(() => {
      router.push({ path: "/password-reset/confirm", query: { email: email.value.trim() } });
    }, 700);
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) error.value = "Пользователь с таким email не найден";
    else if (status === 422) error.value = "Ошибка валидации";
    else error.value = "Ошибка сервера или сети";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.form { display: grid; gap: 12px; }
.success { margin: 6px 0 0; color: #7cff9b; font-size: 15px; }
.error { margin: 6px 0 0; color: #ff6b6b; font-size: 15px; }
.hint { margin-top: 10px; text-align: center; font-size: 15px; color: rgba(232, 232, 232, 0.75); }
.link { color: #ffffff; text-decoration: none; border-bottom: 1px solid rgba(255,255,255,0.35); }
.link:hover { border-bottom-color: rgba(255,255,255,0.9); }
</style>
