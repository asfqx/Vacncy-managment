<template>
  <div class="card">
    <div class="row">
      <div class="title">{{ title }}</div>
      <div v-if="subtitle" class="badge">{{ subtitle }}</div>
    </div>

    <button class="link" type="button" disabled>
      Подробнее
    </button>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});
</script>

<style scoped>
.card {
  background: rgba(15,16,22,0.92);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  padding: 12px;
  display: grid;
  gap: 10px;
}
.row { display:flex; justify-content: space-between; gap: 10px; align-items: center; }
.title { font-weight: 800; font-size: 14px; }
.badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid rgba(124,255,155,0.35);
  opacity: 0.9;
}
.link {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.75);
  border-radius: 12px;
  height: 36px;
  cursor: not-allowed;
}
</style>