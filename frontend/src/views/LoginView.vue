<template>
  <AuthCard title="Вход" subtitle="Авторизация в системе управления вакансиями">
    <form class="form" @submit.prevent="onSubmit">
      <BaseInput
        v-model="login"
        label="Email или username"
        placeholder="example@mail.com или username"
        autocomplete="username"
        :error="fieldErrors.login"
      />

      <BaseInput
        v-model="password"
        label="Пароль"
        type="password"
        placeholder="••••••••"
        autocomplete="current-password"
        :error="fieldErrors.password"
      />

      <BaseButton :loading="loading">Войти</BaseButton>

      <p v-if="error" class="error">{{ error }}</p>

      <!-- 👇 Добавили переход на регистрацию -->
      <p class="hint">
        Нет аккаунта?
        <RouterLink class="link" to="/register">
          Зарегистрироваться
        </RouterLink>
      </p>
      <p class="hint">
        <RouterLink class="link" to="/password-reset">
          Забыли пароль?
        </RouterLink>
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
const { login: doLogin, loading, error } = useAuth();

const login = ref("");
const password = ref("");

const fieldErrors = reactive({ login: "", password: "" });

function validate() {
  fieldErrors.login = "";
  fieldErrors.password = "";

  if (!login.value.trim()) fieldErrors.login = "Введите username или email";
  if (!password.value) fieldErrors.password = "Введите пароль";

  return !fieldErrors.login && !fieldErrors.password;
}

async function onSubmit() {
  if (!validate()) return;

  await doLogin({
    login: login.value.trim(),
    password: password.value,
  });

  await router.push("/");
}
</script>

<style scoped>
.form { display: grid; gap: 12px; }

.error {
  margin: 6px 0 0;
  color: #ff6b6b;
  font-size: 13px;
}

.hint {
  margin-top: 12px;
  font-size: 13px;
  color: rgba(232, 232, 232, 0.75);
  text-align: center;
}

.link {
  color: #ffffff;
  text-decoration: none;
  border-bottom: 1px solid rgba(255,255,255,0.35);
  transition: border-color 0.2s ease;
}

.link:hover {
  border-bottom-color: rgba(255,255,255,0.9);
}
</style>