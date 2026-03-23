<template>
  <div class="panel">
    <div class="panel__badge">{{ badge }}</div>
    <h2 class="panel__title">{{ title }}</h2>
    <p class="panel__text">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  badge: { type: String, default: "Скоро" },
  title: { type: String, required: true },
  description: { type: String, required: true },
});
</script>

<style scoped>
.panel {
  padding: 24px;
  border-radius: 24px;
  background: rgba(15, 16, 22, 0.94);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.panel__badge {
  display: inline-flex;
  margin-bottom: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.76);
  font-size: 13px;
  font-weight: 700;
}
.panel__title { margin: 0; font-size: 26px; }
.panel__text {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.6;
}
</style>