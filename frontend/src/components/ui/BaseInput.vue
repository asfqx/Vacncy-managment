<template>
  <label class="field">
    <span v-if="label" class="label">{{ label }}</span>

    <input
      class="input"
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      v-bind="$attrs"
    />

    <span v-if="error" class="error">{{ error }}</span>
  </label>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: "" },
  label: { type: String, default: "" },
  error: { type: String, default: "" },
  type: { type: String, default: "text" },
});
defineEmits(["update:modelValue"]);
</script>

<style scoped>
.field { display: grid; gap: 6px; }
.label { font-size: 13px; color: rgba(232,232,232,0.9); }
.input {
  height: 42px;
  border-radius: 12px;
  padding: 0 12px;
  background: #0f1016;
  border: 1px solid rgba(255,255,255,0.10);
  color: #e8e8e8;
  outline: none;
}
.input:focus { border-color: rgba(255,255,255,0.25); }
.error { font-size: 12px; color: #ff6b6b; }
</style>