<template>
  <ConfirmTokenCard
    :email="email"
    title="Подтверждение email"
    subtitle="Введите код из письма"
    hint="Если письма нет, проверьте папку Спам или отправьте код повторно."
    token-label="Код из письма"
    confirm-text="Подтвердить"
    :show-resend="true"
    resend-text="Отправить снова"
    :cooldown-seconds="60"
    :on-confirm="handleConfirm"
    :on-resend="handleResend"
    bottom-link-text="Перейти ко входу"
    bottom-link-to="/login"
  />
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import ConfirmTokenCard from "../components/auth/ConfirmTokenCard.vue";
import { authApi } from "../api/auth";

const route = useRoute();
const router = useRouter();
const email = computed(() => String(route.query.email || "").trim());

async function handleConfirm(token) {
  try {
    await authApi.emailConfirmConfirm({ email: email.value, token });
    setTimeout(() => router.push("/login"), 800);
  } catch (e) {
    const status = e?.response?.status;
    if (status === 400) throw new Error("Неверный или просроченный код");
    throw new Error("Не удалось подтвердить email");
  }
}

async function handleResend() {
  try {
    await authApi.emailConfirmRequest(email.value);
  } catch (e) {
    const status = e?.response?.status;
    if (status === 429) throw new Error("Слишком часто. Попробуйте позже.");
    throw new Error("Не удалось отправить код");
  }
}
</script>
