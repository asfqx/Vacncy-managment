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
  variant: { type: String, default: "primary" }, // primary | ghost
  full: { type: Boolean, default: true },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
});
</script>

<style scoped>
.btn {
  height: 44px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0 14px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.btn--full { width: 100%; }

.btn--primary {
  background: #ffffff;
  color: #0b0c10;
}
.btn--ghost {
  background: transparent;
  border-color: rgba(255,255,255,0.14);
  color: #e8e8e8;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid rgba(0,0,0,0.25);
  border-top-color: rgba(0,0,0,0.8);
  animation: spin 0.7s linear infinite;
}
.btn--ghost .spinner {
  border-color: rgba(255,255,255,0.25);
  border-top-color: rgba(255,255,255,0.85);
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>