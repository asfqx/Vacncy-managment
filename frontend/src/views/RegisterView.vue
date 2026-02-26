<template>
  <AuthCard
    title="Регистрация"
    subtitle="Создайте аккаунт, затем подтвердите email"
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

      <BaseInput
        v-model="username"
        label="Username"
        placeholder="username"
        autocomplete="username"
        :error="fieldErrors.username"
      />

      <BaseInput
        v-model="fio"
        label="ФИО"
        placeholder="Иванов Иван Иванович"
        autocomplete="name"
        :error="fieldErrors.fio"
      />

      <BaseInput
        v-model="password"
        label="Пароль"
        type="password"
        placeholder="Минимум 8 символов"
        autocomplete="new-password"
        :error="fieldErrors.password"
      />

      <BaseButton :loading="loading">Создать аккаунт</BaseButton>

      <p v-if="error" class="error">{{ error }}</p>

      <p class="hint">
        Уже есть аккаунт?
        <RouterLink class="link" to="/login">Войти</RouterLink>
      </p>
    </form>
  </AuthCard>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter, RouterLink } from "vue-router";
import { useAuth } from "../composables/useAuth";
import AuthCard from "../components/ui/AuthCard.vue";
import BaseInput from "../components/ui/BaseInput.vue";
import BaseButton from "../components/ui/BaseButton.vue";

const router = useRouter();
const { register, loading, error } = useAuth();

const email = ref("");
const username = ref("");
const fio = ref("");
const password = ref("");

const fieldErrors = reactive({
  email: "",
  username: "",
  fio: "",
  password: "",
});

function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function validate() {
  fieldErrors.email = "";
  fieldErrors.username = "";
  fieldErrors.fio = "";
  fieldErrors.password = "";

  const e = email.value.trim();
  const u = username.value.trim();
  const f = fio.value.trim();

  if (!e) fieldErrors.email = "Введите email";
  else if (!isEmail(e)) fieldErrors.email = "Некорректный email";

  if (!u) fieldErrors.username = "Введите username";
  else if (u.length < 3) fieldErrors.username = "Минимум 3 символа";

  if (!f) fieldErrors.fio = "Введите ФИО";
  else if (f.length < 5) fieldErrors.fio = "Минимум 5 символов";

  if (!password.value) fieldErrors.password = "Введите пароль";
  else if (password.value.length < 8) fieldErrors.password = "Минимум 8 символов";

  return !fieldErrors.email && !fieldErrors.username && !fieldErrors.fio && !fieldErrors.password;
}

async function onSubmit() {
  if (!validate()) return;

  await register({
    email: email.value.trim(),
    username: username.value.trim(),
    password: password.value,
    fio: fio.value.trim(),
    role: "employer",
  });

  // ✅ следующий шаг: форма подтверждения почты
  // можно передать email в query, чтобы показать "куда отправили"
  await router.push({ path: "/email-confirm", query: { email: email.value.trim() } });
}
</script>

<style scoped>
.form { display: grid; gap: 12px; }
.error { margin: 6px 0 0; color: #ff6b6b; font-size: 13px; }
.hint { margin: 8px 0 0; font-size: 13px; color: rgba(232,232,232,0.75); text-align: center; }
.link { color: #ffffff; text-decoration: none; border-bottom: 1px solid rgba(255,255,255,0.35); }
.link:hover { border-bottom-color: rgba(255,255,255,0.8); }
</style>