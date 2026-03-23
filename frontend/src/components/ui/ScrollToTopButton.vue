<template>
  <Transition name="scroll-top-fade">
    <button
      v-if="visible"
      class="scrollTopButton"
      type="button"
      aria-label="Наверх"
      @click="scrollToTop"
    >
      <span class="scrollTopButton__icon">↑</span>
      <span class="scrollTopButton__text">Наверх</span>
    </button>
  </Transition>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

const visible = ref(false);
const route = useRoute();
const revealOffset = 280;

function getScrollTop() {
  return window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
}

function updateVisibility() {
  visible.value = getScrollTop() > revealOffset;
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

watch(
  () => route.fullPath,
  async () => {
    await nextTick();
    updateVisibility();
  }
);

onMounted(() => {
  updateVisibility();
  window.addEventListener("scroll", updateVisibility, { passive: true });
  window.addEventListener("resize", updateVisibility, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener("scroll", updateVisibility);
  window.removeEventListener("resize", updateVisibility);
});
</script>

<style scoped>
.scrollTopButton {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 60;
  min-height: 52px;
  padding: 0 18px;
  border: 1px solid rgba(47, 115, 255, 0.3);
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(23, 27, 39, 0.96), rgba(10, 12, 18, 0.98)),
    linear-gradient(135deg, rgba(47, 115, 255, 0.18), rgba(90, 147, 255, 0.08));
  box-shadow:
    0 18px 30px rgba(0, 0, 0, 0.34),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  color: #eef4ff;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.scrollTopButton:hover {
  transform: translateY(-2px);
  border-color: rgba(90, 147, 255, 0.5);
  box-shadow:
    0 22px 34px rgba(0, 0, 0, 0.38),
    0 0 0 6px rgba(47, 115, 255, 0.1);
}

.scrollTopButton__icon {
  width: 24px;
  height: 24px;
  border-radius: 999px;
  display: inline-grid;
  place-items: center;
  background: rgba(47, 115, 255, 0.18);
  font-size: 14px;
  font-weight: 800;
}

.scrollTopButton__text {
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.scroll-top-fade-enter-active,
.scroll-top-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.scroll-top-fade-enter-from,
.scroll-top-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 720px) {
  .scrollTopButton {
    right: 16px;
    bottom: 16px;
    min-height: 48px;
    padding: 0 16px;
  }

  .scrollTopButton__text {
    display: none;
  }
}
</style>
