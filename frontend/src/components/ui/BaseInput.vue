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
.field {
  display: grid;
  gap: 8px;
}

.label {
  font-size: 13px;
  font-weight: 600;
  color: rgba(232, 232, 232, 0.9);
}

.input {
  min-height: 50px;
  border-radius: 16px;
  padding: 0 16px;
  background: rgba(8, 10, 16, 0.96);
  border: 1px solid rgba(255,255,255,0.10);
  color: #e8e8e8;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input:focus {
  border-color: rgba(47,115,255,0.55);
  box-shadow: 0 0 0 4px rgba(47,115,255,0.14);
}

.error {
  font-size: 12px;
  color: #ff7d7d;
}
</style>
