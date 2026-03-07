<template>
  <div class="wrap" role="status" aria-live="polite">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
    <span v-if="text" class="text">{{ text }}</span>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: "" },
});
</script>

<style scoped>
.wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 0;
  opacity: 0.8;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: rgba(255,255,255,0.75);
  animation: pulse 1s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: .15s; }
.dot:nth-child(3) { animation-delay: .3s; }

.text { font-size: 13px; opacity: 0.75; margin-left: 6px; }

@keyframes pulse {
  0%, 100% { transform: translateY(0); opacity: .35; }
  50% { transform: translateY(-3px); opacity: 1; }
}
</style>