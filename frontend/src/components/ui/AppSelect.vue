<template>
  <div ref="root" class="select">
    <button
      class="select__trigger"
      :class="{ 'is-open': open }"
      type="button"
      @click="toggle"
    >
      <span class="select__value">{{ selectedLabel }}</span>
      <span class="select__arrow"></span>
    </button>

    <div v-if="open" class="select__menu">
      <button
        v-for="option in options"
        :key="option.value || '__empty'"
        class="select__option"
        :class="{ 'is-selected': modelValue === option.value }"
        type="button"
        @click="selectOption(option.value)"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  options: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue"]);
const open = ref(false);
const root = ref(null);

const selectedLabel = computed(() => {
  const selected = props.options.find((option) => option.value === props.modelValue);
  return selected?.label || "Выберите";
});

function toggle() {
  open.value = !open.value;
}

function selectOption(value) {
  emit("update:modelValue", value);
  open.value = false;
}

function handleClickOutside(event) {
  if (!root.value?.contains(event.target)) {
    open.value = false;
  }
}

onMounted(() => {
  document.addEventListener("mousedown", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", handleClickOutside);
});
</script>

<style scoped>
.select {
  position: relative;
}

.select__trigger {
  width: 100%;
  min-height: 52px;
  border-radius: 16px;
  padding: 0 16px;
  background: rgba(8, 10, 16, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.select__trigger:hover,
.select__trigger.is-open {
  border-color: rgba(47, 115, 255, 0.6);
  box-shadow: 0 0 0 4px rgba(47, 115, 255, 0.14);
}

.select__value {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.select__arrow {
  width: 10px;
  height: 10px;
  border-right: 2px solid rgba(255, 255, 255, 0.72);
  border-bottom: 2px solid rgba(255, 255, 255, 0.72);
  transform: rotate(45deg) translateY(-2px);
  flex: 0 0 auto;
}

.select__menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 20;
  padding: 8px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.98), rgba(11, 12, 17, 1));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.32);
  display: grid;
  gap: 6px;
}

.select__option {
  min-height: 40px;
  padding: 0 12px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: transparent;
  color: rgba(255, 255, 255, 0.88);
  text-align: left;
  cursor: pointer;
}

.select__option:hover {
  background: rgba(255, 255, 255, 0.05);
}

.select__option.is-selected {
  background: rgba(47, 115, 255, 0.18);
  border-color: rgba(47, 115, 255, 0.32);
  color: #fff;
}
</style>
