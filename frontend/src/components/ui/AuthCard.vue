<template>
  <div class="page">
    <div class="card">
      <h1 class="title">{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: "Вход" },
  subtitle: { type: String, default: "" },
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #0b0c10;
  padding: 24px;
  color: #e8e8e8;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
}
.card {
  width: 100%;
  max-width: 420px;
  background: #111218;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.45);
}
.title { font-size: 22px; margin: 0 0 6px 0; }
.subtitle {
  margin: 0 0 18px 0;
  color: rgba(232,232,232,0.65);
  font-size: 13px;
  line-height: 1.4;
}
</style>