<template>
  <div class="page">
    <header class="topbar">
      <div class="topbar__left">
        <RouterLink class="logo" :to="homePath">vm</RouterLink>

        <nav class="nav">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            class="nav__item"
            :class="{ 'is-active': route.path === item.to }"
            :to="item.to"
          >
            {{ item.label }}
          </RouterLink>
        </nav>
      </div>

      <div class="topbar__right">
        <RouterLink v-if="primaryAction" class="pill" :to="primaryAction.to">
          {{ primaryAction.label }}
        </RouterLink>

        <RouterLink class="avatar" :to="profilePath">
          {{ avatarLetterValue }}
        </RouterLink>

        <button class="logout" type="button" @click="onLogout">
          Выйти
        </button>
      </div>
    </header>

    <main class="layout">
      <aside class="left">
        <div class="summaryCard">
          <span class="summaryCard__label">{{ roleLabel }}</span>
          <h1 class="summaryCard__title">{{ title }}</h1>
          <p v-if="subtitle" class="summaryCard__text">{{ subtitle }}</p>
        </div>

        <slot name="aside" />
      </aside>

      <section class="right">
        <slot />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useAuth } from "../../composables/useAuth";

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  roleLabel: { type: String, required: true },
  navItems: {
    type: Array,
    default: () => [],
  },
  primaryAction: {
    type: Object,
    default: null,
  },
  avatarLetter: {
    type: String,
    default: "U",
  },
  homePath: {
    type: String,
    required: true,
  },
  profilePath: {
    type: String,
    default: "/profile",
  },
});

const route = useRoute();
const router = useRouter();
const { logout } = useAuth();

const avatarLetterValue = computed(() => String(props.avatarLetter || "U").slice(0, 1).toUpperCase());

async function onLogout() {
  await logout();
  await router.push("/login");
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(47, 115, 255, 0.22), transparent 28%),
    radial-gradient(circle at top right, rgba(255, 91, 91, 0.18), transparent 24%),
    #0b0c10;
  color: #eaeaf0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  min-height: 64px;
  background: rgba(7, 8, 12, 0.88);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 20px;
}

.topbar__left,
.topbar__right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #ff5b5b, #2f73ff);
  color: #fff;
  text-decoration: none;
  font-weight: 900;
  text-transform: uppercase;
}

.nav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.nav__item {
  padding: 10px 12px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.76);
  text-decoration: none;
  transition: background 0.2s ease, color 0.2s ease;
}

.nav__item:hover,
.nav__item.is-active {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.pill,
.logout,
.avatar {
  border-radius: 999px;
  text-decoration: none;
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: #fff;
}

.pill {
  padding: 10px 14px;
  background: #2f73ff;
}

.avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.08);
  font-weight: 800;
}

.logout {
  height: 38px;
  padding: 0 14px;
  background: transparent;
  cursor: pointer;
}

.layout {
  max-width: 1240px;
  margin: 0 auto;
  padding: 24px 16px 32px;
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 20px;
}

.left,
.right {
  display: grid;
  gap: 14px;
  align-content: start;
}

.summaryCard {
  padding: 18px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(22, 24, 34, 0.96), rgba(12, 13, 18, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.summaryCard__label {
  display: inline-flex;
  margin-bottom: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(47, 115, 255, 0.14);
  color: #8eb4ff;
  font-size: 13px;
  font-weight: 700;
}

.summaryCard__title {
  margin: 0;
  font-size: 28px;
  line-height: 1.15;
}

.summaryCard__text {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.5;
}

@media (max-width: 980px) {
  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .topbar__left,
  .topbar__right {
    width: 100%;
    flex-wrap: wrap;
  }

  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
