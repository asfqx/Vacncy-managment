<template>
  <RouterView v-slot="{ Component, route }">
    <div class="screen-stage">
      <Transition name="screen-morph">
        <component :is="Component" :key="route.fullPath" class="screen-layer" />
      </Transition>
      <ScrollToTopButton />
    </div>
  </RouterView>
</template>

<script setup>
import { RouterView } from "vue-router";
import ScrollToTopButton from "./components/ui/ScrollToTopButton.vue";
</script>

<style>
* { box-sizing: border-box; }
html, body, #app {
  height: 100%;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(170, 201, 255, 0.72) transparent;
}

body {
  margin: 0;
  background: #0b0c10;
  color: #e8e8e8;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
}

button, input { font: inherit; }

*::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

*::-webkit-scrollbar-track {
  background: transparent;
}

*::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(178, 208, 255, 0.72), rgba(92, 142, 255, 0.44));
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.08),
    0 4px 18px rgba(76, 124, 255, 0.18);
}

*::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(196, 221, 255, 0.84), rgba(110, 156, 255, 0.56));
}

*::-webkit-scrollbar-corner {
  background: transparent;
}

.screen-stage {
  position: relative;
  min-height: 100%;
  width: 100%;
  overflow-x: hidden;
}

.screen-layer {
  width: 100%;
}

.screen-morph-enter-active,
.screen-morph-leave-active {
  transition: opacity 0.18s ease, filter 0.18s ease;
  will-change: opacity, filter;
}

.screen-morph-enter-active {
  position: relative;
  z-index: 1;
}

.screen-morph-leave-active {
  position: absolute;
  inset: 0;
  width: 100%;
  z-index: 0;
  pointer-events: none;
}

.screen-morph-enter-from {
  opacity: 0;
  filter: blur(4px) saturate(1.02) brightness(1.01);
}

.screen-morph-enter-to {
  opacity: 1;
  filter: blur(0) saturate(1) brightness(1);
}

.screen-morph-leave-from {
  opacity: 1;
  filter: blur(0) saturate(1) brightness(1);
}

.screen-morph-leave-to {
  opacity: 0;
  filter: blur(4px) saturate(1.01) brightness(0.995);
}
</style>

