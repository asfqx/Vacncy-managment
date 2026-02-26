<template>
  <div class="wrap">
    <h2>Вы вошли ✅</h2>
    <p>Дальше сделаем страницы вакансий/профиля.</p>

    <button class="logout" @click="onLogout">Выйти</button>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuth } from "../composables/useAuth";

const router = useRouter();
const { logout } = useAuth();

async function onLogout() {
  await logout();
  await router.push("/login");
}
</script>

<style scoped>
.wrap { padding: 24px; font-family: system-ui; }
.logout {
  margin-top: 12px;
  height: 40px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.2);
  cursor: pointer;
}
</style>