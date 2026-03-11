<template>
  <button
    class="btn"
    :class="[
      variant === 'primary' && 'btn--primary',
      variant === 'ghost' && 'btn--ghost',
      full && 'btn--full'
    ]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <span v-if="loading" class="spinner" aria-hidden="true"></span>
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: "primary" },
  full: { type: Boolean, default: true },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
});
</script>

<style scoped>
.btn {
  min-height: 48px;
  border-radius: 16px;
  border: 1px solid transparent;
  padding: 0 16px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: transform 0.2s ease, opacity 0.2s ease, border-color 0.2s ease;
}

.btn--full { width: 100%; }

.btn--primary {
  background: linear-gradient(135deg, #2f73ff, #5a93ff);
  color: #fff;
  border-color: rgba(47,115,255,0.38);
  box-shadow: 0 10px 22px rgba(47,115,255,0.22);
}

.btn--ghost {
  background: transparent;
  border-color: rgba(255,255,255,0.14);
  color: #e8e8e8;
}

.btn:not(:disabled):hover {
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid rgba(255,255,255,0.28);
  border-top-color: rgba(255,255,255,0.92);
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
