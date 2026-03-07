<template>
  <div ref="el" class="sentinel"></div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const props = defineProps({
  onReach: { type: Function, required: true },
  disabled: { type: Boolean, default: false },
  rootMargin: { type: String, default: "600px" }, // заранее подгружать
});

const el = ref(null);
let observer = null;

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      if (!entry?.isIntersecting) return;
      if (props.disabled) return;
      props.onReach();
    },
    { root: null, rootMargin: props.rootMargin, threshold: 0.0 }
  );

  if (el.value) observer.observe(el.value);
});

onBeforeUnmount(() => {
  if (observer && el.value) observer.unobserve(el.value);
  observer?.disconnect();
});
</script>

<style scoped>
.sentinel {
  height: 1px;
}
</style>