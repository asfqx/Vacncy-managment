<template>
    <router-link class="link" :to="`/vacancies/${vacancy.uuid}`">
    <article class="card">
        <div class="top">
        <h3 class="title">{{ vacancy.title }}</h3>
        <span class="badge" :class="{ remote: vacancy.remote }">
            {{ vacancy.remote ? "Удалённо" : "Офис" }}
        </span>
        </div>

        <!-- КРУПНАЯ ЗАРПЛАТА -->
        <p class="salary">
        {{ formatSalary(vacancy.salary, vacancy.currency) }}
        </p>

        <p class="meta">
        <span v-if="vacancy.city">{{ vacancy.city }}</span>
        <span v-else>Город не указан</span>
        </p>

        <p class="desc">
        {{ short(vacancy.description) }}
        </p>

        <div class="bottom">
        <span class="muted">{{ formatDate(vacancy.created_at) }}</span>
        </div>
    </article>
    </router-link>
</template>

<script setup>
defineProps({ vacancy: { type: Object, required: true } });

function short(text) {
  if (!text) return "";
  const t = String(text).replace(/\s+/g, " ").trim();
  return t.length > 220 ? t.slice(0, 220) + "…" : t;
}

function formatSalary(salary, currency) {
  if (!salary) return "З/п не указана";
  const cur = currency || "RUB";
  return `${salary.toLocaleString("ru-RU")} ${cur}`;
}

function formatDate(iso) {
  try { return new Date(iso).toLocaleString("ru-RU"); } catch { return iso; }
}
</script>
<style scoped>
.link { text-decoration: none; color: inherit; display: block; }
.card {
  background: rgba(15, 16, 22, 0.92);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  padding: 14px;
  display: grid;
  gap: 8px;
}

.link:hover .card {
  transform: translateY(-1px);
  border-color: rgba(255,255,255,0.18);
}

.top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.title {
  margin: 0;
  font-size: 18px;
  line-height: 1.25;
}

.badge {
  font-size: 14px;
  padding: 5px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  opacity: 0.9;
}
.badge.remote {
  border-color: rgba(124, 255, 155, 0.35);
}

.salary {
  margin: 0;
  font-size: 22px;          /* крупнее */
  font-weight: 500;         /* жирный */
  letter-spacing: -0.3px;
  color: #ffffff;
}

.meta {
  margin: 0;
  font-size: 15px;
  opacity: 0.75;
  display: flex;
  gap: 8px;
  align-items: center;
}
.dot { opacity: 0.6; }

.desc {
  margin: 0;
  font-size: 15px;
  line-height: 1.45;
  opacity: 0.9;
}

.bottom {
  display: flex;
  justify-content: right;
  gap: 10px;
  font-size: 14px;
}
.muted { opacity: 0.65; }
</style>