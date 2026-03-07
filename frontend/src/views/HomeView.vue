<template>
  <div class="page">
    <header class="topbar">
      <div class="topbar__left">
        <div class="logo">vm</div>
        <nav class="nav">
          <button class="nav__item is-active" type="button">Поиск</button>
          <button class="nav__item" type="button" disabled>Отклики</button>
          <button class="nav__item" type="button" disabled>Сервисы</button>
          <button class="nav__item" type="button" disabled>Карьера</button>
          <button class="nav__item" type="button" disabled>Помощь</button>
        </nav>
      </div>

      <div class="topbar__right">
        <button class="iconBtn" type="button" disabled title="Избранное">♡</button>
        <button class="iconBtn" type="button" disabled title="Уведомления">🔔</button>
        <button class="pill" type="button" disabled>Создать резюме</button>
        <button class="avatar" type="button" disabled>П</button>
      </div>
    </header>

    <main class="layout">
      <aside class="left">
        <UiCard title="Отклики и приглашения"/>
        <UiCard title="Просмотры резюме"/>
        <UiCard title="Избранные вакансии"/>

        <div class="spacer"></div>

      </aside>

      <section class="right">
        <div class="searchRow">
          <div class="searchInputWrap">
            <span class="searchIcon">🔎</span>
            <input
              v-model="query"
              class="searchInput"
              placeholder="Профессия, должность или компания"
              @keydown.enter.prevent="onSearch"
            />
          </div>
          <button class="searchBtn" type="button" @click="onSearch" :disabled="loading">
            Найти
          </button>
        </div>

        <div class="filtersLine">
          <input v-model="filters.city" class="miniInput" placeholder="Город" />
        <div class="workFormat">
          <button
            class="formatBtn"
            :class="{ active: filters.remote === null }"
            @click="filters.remote = null"
            type="button"
          >
            Любой
          </button>

          <button
            class="formatBtn"
            :class="{ active: filters.remote === true }"
            @click="filters.remote = true"
            type="button"
          >
            Удалённо
          </button>

          <button
            class="formatBtn"
            :class="{ active: filters.remote === false }"
            @click="filters.remote = false"
            type="button"
          >
            Офис
          </button>
        </div>
          <input v-model="filters.salary_from" class="miniInput" placeholder="З/п от" inputmode="numeric" />
          <input v-model="filters.salary_to" class="miniInput" placeholder="З/п до" inputmode="numeric" />

          <button class="ghostBtn" type="button" @click="clearAll" :disabled="loading">
            Сбросить
          </button>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <InlineLoader v-else-if="loading" text="Загружаем вакансии…" />

        <div v-if="!loading" class="list">
          <VacancyCardHH v-for="v in items" :key="v.uuid" :vacancy="v" />

          <InlineLoader
            v-if="loadingMore"
            text="Подгружаем ещё…"
          />

          <InfiniteSentinel
            v-if="hasMore"
            :disabled="loadingMore || loading"
            :onReach="loadMore"
          />

          <p v-if="isEmpty" class="muted center">Ничего не найдено</p>
          <p v-else-if="!hasMore && items.length" class="muted center">Это все вакансии</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import UiCard from "../components/ui/UiCard.vue";
import InlineLoader from "../components/ui/InlineLoader.vue";
import InfiniteSentinel from "../components/ui/InfiniteSentinel.vue";
import VacancyCardHH from "../components/vacancies/VacancyCard.vue";

import { useVacancies } from "../composables/useVacancies";

const {
  items,
  loading,
  loadingMore,
  error,
  query,
  filters,
  mode,
  hasMore,
  isEmpty,
  loadFirst,
  loadMore,
  reset,
} = useVacancies();

async function onSearch() {
  await loadFirst();
}

function clearAll() {
  query.value = "";
  filters.city = "";
  filters.remote = null;
  filters.salary_from = "";
  filters.salary_to = "";
  filters.company_id = "";
  reset();
  loadFirst();
}

onMounted(loadFirst);
</script>

<style scoped>
.page { min-height: 100vh; background: #0b0c10; color: #eaeaf0; }

/* topbar */
.topbar {
  position: sticky; top: 0; z-index: 10;
  height: 54px;
  background: rgba(0,0,0,0.85);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 14px;
}
.topbar__left { display:flex; align-items:center; gap:14px; }
.logo {
  width: 28px; height: 28px; border-radius: 8px;
  background: #ff2f54;
  display:grid; place-items:center;
  font-weight: 900; text-transform: uppercase;
}
.nav { display:flex; gap:10px; align-items:center; }
.nav__item {
  background: transparent; border: none;
  color: rgba(255,255,255,0.85);
  font-size: 15px; padding: 8px 8px;
}
.nav__item.is-active { color:#fff; }
.nav__item:disabled { opacity: 0.5; cursor:not-allowed; }

.topbar__right { display:flex; align-items:center; gap:10px; }
.iconBtn {
  width: 34px; height: 34px; border-radius: 10px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.85);
  cursor: not-allowed;
}
.pill {
  height: 34px; padding: 0 12px; border-radius: 999px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.10);
  color: rgba(255,255,255,0.9);
  font-weight: 700;
  cursor: not-allowed;
}
.avatar {
  width: 34px; height: 34px; border-radius: 999px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.12);
  color: #fff; font-weight: 800;
  cursor: not-allowed;
}

.layout {
  max-width: 1180px;
  margin: 0 auto;
  padding: 18px 14px 28px;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 18px;
}
@media (max-width: 980px) {
  .layout { grid-template-columns: 1fr; }
  .left { order: 2; }
  .right { order: 1; }
}

.left { display:grid; gap:12px; align-content:start; }
.spacer { height: 6px; }
.right { display:grid; gap:12px; }

.searchRow {
  display:grid;
  grid-template-columns: 1fr 120px;
  gap:10px;
  align-items:center;
}
.searchInputWrap {
  height: 44px;
  display:flex; align-items:center; gap:8px;
  padding: 0 12px;
  border-radius: 14px;
  background:#0f1016;
  border: 1px solid rgba(255,255,255,0.10);
}
.searchIcon { opacity: 0.7; }
.searchInput {
  width:100%; height:100%;
  border:none; background:transparent;
  color:#eaeaf0; outline:none;
  font-size: 16px;
}
.filtersBtn {
  height: 44px; border-radius: 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  color: rgba(255,255,255,0.85);
  cursor: not-allowed;
}
.searchBtn {
  height: 44px; border-radius: 14px;
  background:#2f73ff;
  border: 1px solid rgba(47,115,255,0.5);
  color:#fff; font-weight: 800;
}
.searchBtn:disabled { opacity: 0.65; cursor: not-allowed; }

.chips { display:flex; flex-wrap:wrap; gap:10px; }
.chip {
  height: 34px; padding: 0 12px; border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  color: rgba(255,255,255,0.85);
  cursor: not-allowed;
}
.chip.is-active {
  background: rgba(255,255,255,0.14);
  color: #fff;
}

.filtersLine {
  display:grid;
  grid-template-columns: 1fr 1fr 0.9fr 0.9fr auto 1fr;
  gap:10px;
  align-items:center;
}
@media (max-width: 980px) {
  .filtersLine { grid-template-columns: 1fr 1fr; }
}
.miniInput {
  height: 40px; border-radius: 12px;
  padding: 0 12px;
  background:#0f1016;
  border:1px solid rgba(255,255,255,0.10);
  color:#eaeaf0; outline:none;
}
.ghostBtn {
  height: 40px; border-radius: 12px;
  padding: 0 12px;
  background: transparent;
  border:1px solid rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.9);
  font-weight: 700;
}
.ghostBtn:disabled { opacity: 0.6; cursor:not-allowed; }
.modeHint { justify-self:end; opacity:0.75; font-size:15px; }

.list { display:grid; gap:12px; }

.error { color:#ff6b6b; font-size:15px; margin: 2px 0 0; }
.muted { opacity:0.75; font-size:15px; margin: 2px 0 0; }
.center { text-align:center; padding: 8px 0; }

.workFormat {
  display: flex;
  gap: 6px;
  padding: 4px;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
}

.formatBtn {
  height: 32px;
  padding: 0 12px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: rgba(255,255,255,0.75);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.formatBtn:hover {
  background: rgba(255,255,255,0.08);
}

.formatBtn.active {
  background: #2f73ff;
  color: white;
  box-shadow: 0 0 0 1px rgba(47,115,255,0.4);
}
</style>