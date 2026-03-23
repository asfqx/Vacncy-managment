<template>
  <button class="card" :class="{ 'is-active': active }" type="button">
    <div class="row">
      <div class="title">{{ title }}</div>
      <div v-if="subtitle" class="badge">{{ subtitle }}</div>
    </div>
  </button>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  active: { type: Boolean, default: false },
});
</script>

<style scoped>
.card {
  width: 100%;
  background: rgba(15,16,22,0.92);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  padding: 14px;
  display: grid;
  gap: 10px;
  text-align: left;
  color: inherit;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
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
.card:hover {
  transform: translateY(-1px);
  border-color: rgba(47,115,255,0.32);
}
.card.is-active {
  border-color: rgba(47,115,255,0.42);
  background: rgba(47,115,255,0.10);
}
</style>
