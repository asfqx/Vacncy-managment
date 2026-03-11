<template>
  <AuthCard :title="title" :subtitle="subtitle">
    <form class="form" @submit.prevent="confirm">
      <div class="infoCard">
        <p class="eyebrow">Email</p>
        <p class="email">{{ email || "не указан" }}</p>
        <p v-if="hint" class="muted">{{ hint }}</p>
      </div>

      <div class="codeField">
        <label class="label">{{ tokenLabel }}</label>

        <div class="inputWrapper">
          <input
            v-model="token"
            class="input"
            :placeholder="tokenPlaceholder"
            autocomplete="one-time-code"
            inputmode="numeric"
          />

          <button
            v-if="showResend"
            type="button"
            class="resendBtn"
            :disabled="!email || resendLoading || resendCooldown > 0"
            @click="resend"
          >
            <span v-if="resendCooldown > 0">{{ resendCooldown }}с</span>
            <span v-else>{{ resendText }}</span>
          </button>
        </div>

        <span v-if="tokenError" class="error">{{ tokenError }}</span>
      </div>

      <BaseButton :loading="confirmLoading" :disabled="!email">
        {{ confirmText }}
      </BaseButton>

      <p v-if="success" class="success">{{ success }}</p>
      <p v-if="error" class="error">{{ error }}</p>

      <p v-if="bottomLinkText && bottomLinkTo" class="hintCenter">
        <RouterLink class="link" :to="bottomLinkTo">{{ bottomLinkText }}</RouterLink>
      </p>
    </form>
  </AuthCard>
</template>

<script setup>
import { ref, onUnmounted } from "vue";
import { RouterLink } from "vue-router";
import AuthCard from "../ui/AuthCard.vue";
import BaseButton from "../ui/BaseButton.vue";

const props = defineProps({
  email: { type: String, default: "" },
  title: { type: String, default: "Подтверждение" },
  subtitle: { type: String, default: "" },
  hint: { type: String, default: "" },
  tokenLabel: { type: String, default: "Код из письма" },
  tokenPlaceholder: { type: String, default: "Например: 123456" },
  confirmText: { type: String, default: "Подтвердить" },
  showResend: { type: Boolean, default: true },
  resendText: { type: String, default: "Отправить" },
  cooldownSeconds: { type: Number, default: 60 },
  onConfirm: { type: Function, required: true },
  onResend: { type: Function, default: null },
  bottomLinkText: { type: String, default: "" },
  bottomLinkTo: { type: String, default: "" },
});

const token = ref("");
const tokenError = ref("");
const error = ref("");
const success = ref("");
const confirmLoading = ref(false);
const resendLoading = ref(false);
const resendCooldown = ref(0);
let intervalId = null;

function startCooldown() {
  resendCooldown.value = props.cooldownSeconds;
  intervalId = setInterval(() => {
    resendCooldown.value -= 1;
    if (resendCooldown.value <= 0) {
      clearInterval(intervalId);
      intervalId = null;
      resendCooldown.value = 0;
    }
  }, 1000);
}

async function confirm() {
  tokenError.value = "";
  error.value = "";
  success.value = "";

  if (!props.email) {
    error.value = "Email не указан.";
    return;
  }
  if (!token.value.trim()) {
    tokenError.value = "Введите код";
    return;
  }

  confirmLoading.value = true;
  try {
    await props.onConfirm(token.value.trim());
    success.value = "Успешно.";
  } catch (e) {
    error.value = e?.message || "Ошибка подтверждения";
  } finally {
    confirmLoading.value = false;
  }
}

async function resend() {
  if (!props.onResend) return;
  if (resendCooldown.value > 0) return;

  error.value = "";
  success.value = "";

  if (!props.email) {
    error.value = "Email не указан.";
    return;
  }

  resendLoading.value = true;
  try {
    await props.onResend();
    success.value = "Код отправлен повторно.";
    startCooldown();
  } catch (e) {
    error.value = e?.message || "Не удалось отправить код";
  } finally {
    resendLoading.value = false;
  }
}

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});
</script>

<style scoped>
.form { display: grid; gap: 14px; }
.infoCard {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  display: grid;
  gap: 6px;
}
.eyebrow {
  margin: 0;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}
.email { margin: 0; font-size: 18px; font-weight: 700; }
.muted { margin: 0; font-size: 13px; opacity: 0.72; line-height: 1.5; }
.codeField { display: grid; gap: 8px; }
.label { font-size: 13px; font-weight: 600; color: rgba(232,232,232,0.9); }
.inputWrapper { position: relative; }
.input {
  width: 100%;
  min-height: 50px;
  border-radius: 16px;
  padding: 0 118px 0 16px;
  background: rgba(8, 10, 16, 0.96);
  border: 1px solid rgba(255,255,255,0.10);
  color: #e8e8e8;
  outline: none;
}
.input:focus {
  border-color: rgba(47,115,255,0.55);
  box-shadow: 0 0 0 4px rgba(47,115,255,0.14);
}
.resendBtn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  min-height: 34px;
  padding: 0 12px;
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.9);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.resendBtn:disabled { opacity: 0.5; cursor: not-allowed; }
.success { margin: 2px 0 0; color: #7cff9b; font-size: 14px; }
.error { margin: 2px 0 0; color: #ff7d7d; font-size: 14px; }
.hintCenter { margin-top: 6px; text-align: center; font-size: 14px; }
.link {
  color: #fff;
  text-decoration: none;
  border-bottom: 1px solid rgba(255,255,255,0.35);
}
.link:hover { border-bottom-color: rgba(255,255,255,0.9); }
</style>
