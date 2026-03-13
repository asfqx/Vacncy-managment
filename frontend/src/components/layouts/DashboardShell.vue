<template>
  <div class="page" :class="pageClass">
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
        <RouterLink v-if="adminPanelAction" class="ghostAction" :to="adminPanelAction.to">
          {{ adminPanelAction.label }}
        </RouterLink>

        <RouterLink v-if="secondaryAction" class="ghostAction" :to="secondaryAction.to">
          {{ secondaryAction.label }}
        </RouterLink>

        <RouterLink v-if="primaryAction" class="pill" :to="primaryAction.to">
          {{ primaryAction.label }}
        </RouterLink>

        <RouterLink class="avatar" :to="profilePath">
          <img v-if="avatarImageSrc" :src="avatarImageSrc" :alt="avatarAlt" class="avatar__image" />
          <span v-else>{{ avatarLetterValue }}</span>
        </RouterLink>

        <button class="logout" type="button" @click="onLogout">
          {{ logoutLabel }}
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
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { usersApi } from "../../api/users";
import { useAuth } from "../../composables/useAuth";
import { getUserRoleFromToken, isAdminRole } from "../../utils/auth";

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
  secondaryAction: {
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
  backgroundVariant: {
    type: String,
    default: "default",
  },
});

const route = useRoute();
const router = useRouter();
const { logout } = useAuth();
const profile = ref(null);
const role = getUserRoleFromToken();

const avatarLetterValue = computed(() => {
  const usernameLetter = String(profile.value?.username || "").trim().slice(0, 1);
  return (usernameLetter || String(props.avatarLetter || "U").slice(0, 1)).toUpperCase();
});

const avatarImageSrc = computed(() => buildAvatarUrl(profile.value?.avatar_url));
const adminPanelAction = computed(() => (
  isAdminRole(role) && route.path !== "/admin" ? { to: "/admin", label: "Панель администратора" } : null
));
const pageClass = computed(() => ({
  "page--solid": props.backgroundVariant === "solid",
}));
const avatarAlt = "Аватар";
const logoutLabel = "Выйти";

function buildAvatarUrl(objectName) {
  if (!objectName) return "";
  const baseUrl = (import.meta.env.VITE_S3_PUBLIC_BASE_URL || "http://localhost:9000").replace(/\/$/, "");
  const normalizedPath = String(objectName)
    .split("/")
    .map((part) => encodeURIComponent(part))
    .join("/");
  return `${baseUrl}/avatars/${normalizedPath}`;
}

async function loadProfile() {
  try {
    profile.value = await usersApi.getMe();
  } catch {
    profile.value = null;
  }
}

async function onLogout() {
  await logout();
  await router.push("/login");
}

onMounted(loadProfile);
</script>

<style scoped>
.page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 0% 24%, rgba(19, 58, 145, 0.3), transparent 26%),
    radial-gradient(circle at 100% 0%, rgba(118, 24, 33, 0.12), transparent 16%),
    linear-gradient(180deg, rgba(6, 8, 14, 0.995), rgba(4, 6, 10, 1));
  color: #eaeaf0;
}
.page--solid {
  background: linear-gradient(180deg, rgba(6, 8, 14, 0.995), rgba(4, 6, 10, 1));
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
.topbar__right { display: flex; align-items: center; gap: 12px; }
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
.nav { display: flex; flex-wrap: wrap; gap: 8px; }
.nav__item {
  padding: 10px 12px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.76);
  text-decoration: none;
  transition: background 0.2s ease, color 0.2s ease;
}
.nav__item:hover,
.nav__item.is-active { color: #fff; background: rgba(255, 255, 255, 0.08); }
.pill,
.ghostAction,
.logout,
.avatar {
  border-radius: 999px;
  text-decoration: none;
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: #fff;
}
.pill { padding: 10px 14px; background: #2f73ff; }
.ghostAction { padding: 10px 14px; background: transparent; }
.avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.08);
  font-weight: 800;
}
.avatar__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.logout { height: 38px; padding: 0 14px; background: transparent; cursor: pointer; }
.layout {
  max-width: 1240px;
  margin: 0 auto;
  padding: 24px 16px 32px;
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 20px;
}
.left,
.right { display: grid; gap: 14px; align-content: start; }
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
.summaryCard__title { margin: 0; font-size: 28px; line-height: 1.15; }
.summaryCard__text {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.5;
}
@media (max-width: 980px) {
  .topbar { align-items: flex-start; flex-direction: column; }
  .topbar__left,
  .topbar__right { width: 100%; flex-wrap: wrap; }
  .layout { grid-template-columns: 1fr; }
}
</style>
