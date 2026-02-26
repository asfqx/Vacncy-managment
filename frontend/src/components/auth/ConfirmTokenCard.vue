<template>
  <AuthCard :title="title" :subtitle="subtitle">
    <form class="form" @submit.prevent="confirm">
      <div class="info">
        <p class="text">
          Email:
          <b>{{ email || "не указан" }}</b>
        </p>
        <p v-if="hint" class="muted">{{ hint }}</p>
      </div>

      <!-- Token input with inline ghost resend button -->
      <div class="code-field">
        <label class="label">{{ tokenLabel }}</label>

        <div class="input-wrapper">
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
            class="resend-btn"
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

      <p v-if="bottomLinkText && bottomLinkTo" class="hint-center">
        <RouterLink class="link" :to="bottomLinkTo">{{ bottomLinkText }}</RouterLink>
      </p>
    </form>
  </AuthCard>
</template>

<script setup>
import { ref, onUnmounted, computed } from "vue";
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

  // hooks
  onConfirm: { type: Function, required: true }, // async (token) => void
  onResend: { type: Function, default: null },  // async () => void

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
    // наружу лучше кидать понятные ошибки текстом.
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
.form { display: grid; gap: 12px; }

.info { display: grid; gap: 6px; margin-bottom: 6px; }
.text { margin: 0; font-size: 14px; }
.muted { margin: 0; font-size: 13px; opacity: 0.75; line-height: 1.4; }

.code-field { display: grid; gap: 6px; }
.label { font-size: 13px; color: rgba(232,232,232,0.9); }

.input-wrapper { position: relative; }

.input {
  width: 100%;
  height: 42px;
  border-radius: 12px;
  padding: 0 110px 0 12px; /* место под кнопку */
  background: #0f1016;
  border: 1px solid rgba(255,255,255,0.10);
  color: #e8e8e8;
  outline: none;
}
.input:focus { border-color: rgba(255,255,255,0.25); }

.resend-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  height: 28px;
  padding: 0 10px;
  border-radius: 8px;

  background: transparent;
  border: 1px solid rgba(255,255,255,0.18);
  color: rgba(255,255,255,0.85);

  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  min-width: 80px;
  text-align: center;
  transition: all 0.2s ease;
}

.resend-btn:hover:not(:disabled) {
  border-color: rgba(255,255,255,0.4);
  color: #ffffff;
}

.resend-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.success { margin: 6px 0 0; color: #7CFF9B; font-size: 13px; }
.error { margin: 6px 0 0; color: #ff6b6b; font-size: 13px; }

.hint-center {
  margin-top: 10px;
  text-align: center;
  font-size: 13px;
  color: rgba(232,232,232,0.75);
}

.link {
  color: #ffffff;
  text-decoration: none;
  border-bottom: 1px solid rgba(255,255,255,0.35);
}
.link:hover { border-bottom-color: rgba(255,255,255,0.9); }
</style>