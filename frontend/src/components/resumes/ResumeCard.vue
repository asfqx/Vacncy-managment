<template>
  <component :is="wrapperTag" v-bind="wrapperProps" class="resumeCardLink">
    <article class="resumeCard" :class="{ 'resumeCard--interactive': isInteractive }">
      <div class="resumeCard__top">
        <div class="resumeCard__heading">
          <p class="resumeCard__eyebrow">{{ genderLabel }}</p>
          <h3 class="resumeCard__title">{{ resume.title }}</h3>
        </div>
        <span class="badge">{{ ageLabel }}</span>
      </div>

      <p class="resumeCard__salary">{{ salaryLabel }}</p>
      <p class="resumeCard__text">{{ resume.about_me || "Кандидат пока не добавил описание." }}</p>

      <dl class="facts">
        <div class="facts__row">
          <dt>Образование</dt>
          <dd>{{ educationLabel }}</dd>
        </div>
        <div class="facts__row">
          <dt>Опыт</dt>
          <dd>{{ experienceLabel }}</dd>
        </div>
      </dl>
    </article>
  </component>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";

const props = defineProps({
  resume: { type: Object, required: true },
  interactive: { type: Boolean, default: true },
});

const genderMap = {
  MALE: "Мужчина",
  FEMALE: "Женщина",
};

const educationMap = {
  SECONDARY: "Среднее",
  SECONDARY_SPECIAL: "Среднее специальное",
  INCOMPLETE_HIGHER: "Неоконченное высшее",
  BACHELOR: "Бакалавр",
  SPECIALIST: "Специалист",
  MASTER: "Магистр",
  POSTGRADUATE: "Аспирантура",
  DOCTORATE: "Докторантура",
};

const isInteractive = computed(() => Boolean(props.interactive && props.resume?.uuid && props.resume.uuid !== "preview"));
const wrapperTag = computed(() => (isInteractive.value ? RouterLink : "div"));
const wrapperProps = computed(() => (isInteractive.value ? { to: `/resumes/${props.resume.uuid}` } : {}));

const genderLabel = computed(() => genderMap[props.resume.gender] || "Пол не указан");

const salaryLabel = computed(() => {
  if (!props.resume.salary && props.resume.salary !== 0) return "Ожидания по зарплате не указаны";
  return `${Number(props.resume.salary).toLocaleString("ru-RU")} ${props.resume.currency || "RUB"}`;
});

const ageLabel = computed(() => {
  if (!props.resume.birth_date) return "Возраст не указан";
  const birthDate = new Date(props.resume.birth_date);
  if (Number.isNaN(birthDate.getTime())) return "Возраст не указан";

  const now = new Date();
  let age = now.getFullYear() - birthDate.getFullYear();
  const monthDelta = now.getMonth() - birthDate.getMonth();
  if (monthDelta < 0 || (monthDelta === 0 && now.getDate() < birthDate.getDate())) age -= 1;
  return `${age} лет`;
});

const educationLabel = computed(() => {
  const first = props.resume.educations?.[0];
  if (!first) return "Не указано";
  const institution = first.institution || "Учебное заведение";
  return `${educationMap[first.level] || first.level || "Образование"} · ${institution}`;
});

const experienceLabel = computed(() => {
  const list = props.resume.experiences || [];
  if (!list.length) return "Не указано";
  const current = list.find((item) => item.is_current);
  const first = current || list[0];
  return `${first.position} · ${first.company_name}`;
});
</script>

<style scoped>
.resumeCardLink {
  display: block;
  text-decoration: none;
  color: inherit;
}

.resumeCard {
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
  display: grid;
  gap: 14px;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.resumeCard--interactive:hover {
  transform: translateY(-2px);
  border-color: rgba(47, 115, 255, 0.28);
  box-shadow: 0 22px 48px rgba(0, 0, 0, 0.3);
}

.resumeCard__top {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: flex-start;
}

.resumeCard__heading {
  min-width: 0;
}

.resumeCard__eyebrow {
  margin: 0 0 8px;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.resumeCard__title {
  margin: 0;
  font-size: 24px;
  line-height: 1.2;
}

.resumeCard__salary {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}

.resumeCard__text {
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.6;
}

.badge {
  min-height: 38px;
  max-width: 100%;
  padding: 8px 14px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  line-height: 1.25;
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.04);
}

.facts {
  display: grid;
  gap: 10px;
  margin: 0;
}

.facts__row {
  display: grid;
  gap: 4px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.facts dt {
  color: rgba(255, 255, 255, 0.56);
  font-size: 13px;
}

.facts dd {
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
}

@media (max-width: 640px) {
  .resumeCard__top {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .badge {
    justify-self: flex-start;
  }
}
</style>
