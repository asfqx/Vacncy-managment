<template>
  <div ref="root" class="dateInput">
    <button
      class="dateInput__trigger"
      :class="{ 'is-open': isOpen, 'is-empty': !modelValue, 'is-disabled': disabled }"
      type="button"
      :disabled="disabled"
      @click="toggle"
    >
      <span>{{ displayValue }}</span>
      <span class="dateInput__icon"></span>
    </button>

    <div v-if="isOpen && !disabled" class="dateInput__popup">
      <div class="dateInput__header">
        <button class="dateInput__nav" type="button" @click="changeMonth(-1)">‹</button>
        <button class="dateInput__month" type="button" @click="goToTodayMonth">{{ monthLabel }}</button>
        <button class="dateInput__nav" type="button" @click="changeMonth(1)">›</button>
      </div>

      <div class="dateInput__weekdays">
        <span v-for="day in weekdays" :key="day">{{ day }}</span>
      </div>

      <div class="dateInput__grid">
        <button
          v-for="day in calendarDays"
          :key="day.key"
          class="dateInput__day"
          :class="{
            'is-outside': !day.isCurrentMonth,
            'is-selected': day.value === modelValue,
            'is-today': day.isToday,
          }"
          type="button"
          @click="selectDate(day.value)"
        >
          {{ day.dayNumber }}
        </button>
      </div>

      <div class="dateInput__footer">
        <button class="dateInput__action dateInput__action--muted" type="button" @click="clearValue">Очистить</button>
        <button class="dateInput__action" type="button" @click="selectToday">Сегодня</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  disabled: { type: Boolean, default: false },
  placeholder: { type: String, default: "ДД.ММ.ГГГГ" },
});

const emit = defineEmits(["update:modelValue"]);

const weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
const monthNames = [
  "Январь",
  "Февраль",
  "Март",
  "Апрель",
  "Май",
  "Июнь",
  "Июль",
  "Август",
  "Сентябрь",
  "Октябрь",
  "Ноябрь",
  "Декабрь",
];

const root = ref(null);
const isOpen = ref(false);
const viewDate = ref(getInitialViewDate(props.modelValue));

watch(
  () => props.modelValue,
  (value) => {
    if (value) {
      viewDate.value = getInitialViewDate(value);
    }
  }
);

const displayValue = computed(() => {
  if (!props.modelValue) return props.placeholder;
  const parsed = parseModelDate(props.modelValue);
  if (!parsed) return props.placeholder;
  return formatDisplayDate(parsed);
});

const monthLabel = computed(() => `${monthNames[viewDate.value.getMonth()]} ${viewDate.value.getFullYear()}`);

const calendarDays = computed(() => {
  const year = viewDate.value.getFullYear();
  const month = viewDate.value.getMonth();
  const firstDay = new Date(year, month, 1);
  const startWeekday = (firstDay.getDay() + 6) % 7;
  const startDate = new Date(year, month, 1 - startWeekday);
  const todayValue = formatModelDate(new Date());

  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + index);
    const value = formatModelDate(date);

    return {
      key: `${value}-${index}`,
      value,
      dayNumber: date.getDate(),
      isCurrentMonth: date.getMonth() === month,
      isToday: value === todayValue,
    };
  });
});

function parseModelDate(value) {
  if (!value) return null;
  const [year, month, day] = String(value).split("-").map(Number);
  if (!year || !month || !day) return null;
  const date = new Date(year, month - 1, day);
  if (Number.isNaN(date.getTime())) return null;
  return date;
}

function formatModelDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatDisplayDate(date) {
  return new Intl.DateTimeFormat("ru-RU").format(date);
}

function getInitialViewDate(value) {
  return parseModelDate(value) || new Date();
}

function toggle() {
  if (props.disabled) return;
  isOpen.value = !isOpen.value;
}

function changeMonth(offset) {
  const next = new Date(viewDate.value);
  next.setMonth(next.getMonth() + offset);
  viewDate.value = next;
}

function goToTodayMonth() {
  viewDate.value = new Date();
}

function selectDate(value) {
  emit("update:modelValue", value);
  isOpen.value = false;
}

function clearValue() {
  emit("update:modelValue", "");
  isOpen.value = false;
}

function selectToday() {
  selectDate(formatModelDate(new Date()));
}

function handleClickOutside(event) {
  if (!root.value?.contains(event.target)) {
    isOpen.value = false;
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
.dateInput {
  position: relative;
}

.dateInput__trigger {
  width: 100%;
  min-height: 52px;
  border-radius: 16px;
  padding: 0 16px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0)),
    rgba(8, 10, 16, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.dateInput__trigger:hover,
.dateInput__trigger.is-open {
  border-color: rgba(47, 115, 255, 0.6);
  box-shadow: 0 0 0 4px rgba(47, 115, 255, 0.14);
}

.dateInput__trigger.is-empty {
  color: rgba(255, 255, 255, 0.4);
}

.dateInput__trigger.is-disabled {
  opacity: 0.34;
  background: rgba(255, 255, 255, 0.02);
  border-color: rgba(255, 255, 255, 0.05);
  cursor: not-allowed;
  box-shadow: none;
}

.dateInput__icon {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: 1px solid rgba(47, 115, 255, 0.2);
  background:
    linear-gradient(180deg, rgba(47, 115, 255, 0.24), rgba(47, 115, 255, 0.06)),
    rgba(255, 255, 255, 0.04);
  position: relative;
  flex: 0 0 auto;
}

.dateInput__icon::before,
.dateInput__icon::after {
  content: "";
  position: absolute;
  left: 3px;
  right: 3px;
}

.dateInput__icon::before {
  top: 4px;
  height: 2px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 999px;
}

.dateInput__icon::after {
  top: 8px;
  bottom: 3px;
  border-top: 1px solid rgba(255, 255, 255, 0.28);
}

.dateInput__popup {
  position: absolute;
  top: calc(100% + 10px);
  left: 0;
  z-index: 30;
  width: 290px;
  padding: 14px;
  border-radius: 22px;
  background:
    radial-gradient(circle at top right, rgba(47, 115, 255, 0.14), transparent 26%),
    linear-gradient(180deg, rgba(18, 19, 27, 0.98), rgba(11, 12, 17, 1));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 24px 54px rgba(0, 0, 0, 0.4);
  display: grid;
  gap: 12px;
}

.dateInput__header,
.dateInput__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.dateInput__month,
.dateInput__nav,
.dateInput__action {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: #eef2ff;
  cursor: pointer;
}

.dateInput__month {
  min-height: 38px;
  padding: 0 14px;
  border-radius: 12px;
  font-weight: 700;
}

.dateInput__nav {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  font-size: 20px;
  line-height: 1;
}

.dateInput__weekdays,
.dateInput__grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 6px;
}

.dateInput__weekdays span {
  min-height: 28px;
  display: grid;
  place-items: center;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.48);
}

.dateInput__day {
  min-height: 34px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: transparent;
  color: rgba(255, 255, 255, 0.92);
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease, color 0.2s ease;
}

.dateInput__day:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.08);
}

.dateInput__day.is-outside {
  color: rgba(255, 255, 255, 0.28);
}

.dateInput__day.is-today {
  border-color: rgba(47, 115, 255, 0.3);
  background: rgba(47, 115, 255, 0.08);
}

.dateInput__day.is-selected {
  background: linear-gradient(135deg, #2f73ff, #5a93ff);
  border-color: rgba(47, 115, 255, 0.55);
  color: #fff;
  box-shadow: 0 10px 22px rgba(47, 115, 255, 0.28);
  transform: translateY(-1px);
}

.dateInput__action {
  min-height: 34px;
  padding: 0 12px;
  border-radius: 10px;
  font-weight: 600;
}

.dateInput__action--muted {
  color: rgba(255, 255, 255, 0.68);
}
</style>
