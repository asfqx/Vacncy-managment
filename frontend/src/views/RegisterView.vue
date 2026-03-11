<template>
  <AuthCard :title="pageTitle" :subtitle="pageSubtitle">
    <form class="form" @submit.prevent="onSubmit">
      <div class="roleSwitch">
        <RouterLink class="roleBtn" :class="{ active: selectedRole === candidateRole }" to="/register/candidate">
          Кандидат
        </RouterLink>
        <RouterLink class="roleBtn" :class="{ active: selectedRole === employerRole }" to="/register/employer">
          ������������
        </RouterLink>
      </div>

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
        :label="nameLabel"
        :placeholder="namePlaceholder"
        autocomplete="name"
        :error="fieldErrors.fio"
      />

      <BaseInput
        v-model="password"
        label="Пароль"
        type="password"
        placeholder="Минимум 8 сим�����"
        autocomplete="new-password"
        :error="fieldErrors.password"
      />

      <BaseButton :loading="loading">{{ submitLabel }}</BaseButton>

      <p v-if="error" class="error">{{ error }}</p>

      <p class="hint">
        Уже есть аккаунт?
        <RouterLink class="link" to="/login">Войти</RouterLink>
      </p>
    </form>
  </AuthCard>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import { useAuth } from "../composables/useAuth";
import { USER_ROLES } from "../utils/auth";
import AuthCard from "../components/ui/AuthCard.vue";
import BaseInput from "../components/ui/BaseInput.vue";
import BaseButton from "../components/ui/BaseButton.vue";

const candidateRole = USER_ROLES.CANDIDATE;
const employerRole = USER_ROLES.COMPANY;

const route = useRoute();
const router = useRouter();
const { register, loading, error } = useAuth();

const email = ref("");
const username = ref("");
const fio = ref("");
const password = ref("");

const fieldErrors = reactive({ email: "", username: "", fio: "", password: "" });

const selectedRole = computed(() => {
  return route.params.role === "employer" ? employerRole : candidateRole;
});

const isEmployerRegistration = computed(() => selectedRole.value === employerRole);
const pageTitle = computed(() => (isEmployerRegistration.value ? "����������� ������������" : "����������� ���������"));
const pageSubtitle = computed(() => (
  isEmployerRegistration.value
    ? "�������� ������� ������������, ����� ����������� email"
    : "�������� ������� ���������, ����� ����������� email"
));
const submitLabel = computed(() => (isEmployerRegistration.value ? "������� ������� ������������" : "������� �������"));
const nameLabel = computed(() => (isEmployerRegistration.value ? "Наз����� �������� ��� ���" : "ФИО"));
const namePlaceholder = computed(() => (
  isEmployerRegistration.value ? "ООО ������� ��� ������ ����" : "И����� ���� ��������"
));

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

  if (!e) fieldErrors.email = "В������ email";
  else if (!isEmail(e)) fieldErrors.email = "Некорректный email";

  if (!u) fieldErrors.username = "В������ username";
  else if (u.length < 3) fieldErrors.username = "Минимум 3 сим����";

  if (!f) fieldErrors.fio = isEmployerRegistration.value ? "В������ �������� �������� ��� ���" : "В������ ���";
  else if (f.length < 5) fieldErrors.fio = "Минимум 5 сим�����";

  if (!password.value) fieldErrors.password = "В������ ������";
  else if (password.value.length < 8) fieldErrors.password = "Минимум 8 сим�����";

  return !fieldErrors.email && !fieldErrors.username && !fieldErrors.fio && !fieldErrors.password;
}

async function onSubmit() {
  if (!validate()) return;

  await register({
    email: email.value.trim(),
    username: username.value.trim(),
    password: password.value,
    fio: fio.value.trim(),
    role: selectedRole.value,
  });

  await router.push({ path: "/email-confirm", query: { email: email.value.trim() } });
}
</script>

<style scoped>
.form { display: grid; gap: 12px; }
.roleSwitch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.roleBtn {
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  text-decoration: none;
  color: rgba(255,255,255,0.78);
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
}
.roleBtn.active {
  background: #2f73ff;
  color: #fff;
  border-color: rgba(47,115,255,0.45);
}
.error { margin: 6px 0 0; color: #ff6b6b; font-size: 13px; }
.hint { margin: 8px 0 0; font-size: 13px; color: rgba(232,232,232,0.75); text-align: center; }
.link { color: #ffffff; text-decoration: none; border-bottom: 1px solid rgba(255,255,255,0.35); }
.link:hover { border-bottom-color: rgba(255,255,255,0.8); }
</style>
