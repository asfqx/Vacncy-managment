<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from "vue-router";
</script>

<style>
* { box-sizing: border-box; }
html, body, #app { height: 100%; }

body {
  margin: 0;
  background: #0b0c10;
  color: #e8e8e8;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
}

button, input { font: inherit; }
</style>