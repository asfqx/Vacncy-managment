<template>
  <AuthCard
    title="Выберите тип регистрации"
    subtitle="Кандидат ищет вакансии и создает резюме, работодатель ищет резюме и публикует вакансии."
  >
    <div class="choices">
      <RouterLink class="choice" to="/register/candidate">
        <strong>Я кандидат</strong>
        <span>Поиск вакансий, отклики, резюме</span>
      </RouterLink>

      <RouterLink class="choice" to="/register/employer">
        <strong>Я работодатель</strong>
        <span>Поиск резюме, отклики, создание вакансий</span>
      </RouterLink>
    </div>

    <p class="hint">
      Уже есть аккаунт?
      <RouterLink class="link" to="/login">Войти</RouterLink>
    </p>
  </AuthCard>
</template>

<script setup>
import { RouterLink } from "vue-router";
import AuthCard from "../components/ui/AuthCard.vue";
</script>

<style scoped>
.choices {
  display: grid;
  gap: 12px;
}
.choice {
  display: grid;
  gap: 6px;
  padding: 16px;
  border-radius: 16px;
  text-decoration: none;
  color: #fff;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.10);
}
.choice:hover {
  border-color: rgba(47,115,255,0.45);
  background: rgba(47,115,255,0.08);
}
.choice span {
  color: rgba(232,232,232,0.72);
  font-size: 14px;
  line-height: 1.45;
}
.hint { margin: 14px 0 0; font-size: 13px; color: rgba(232,232,232,0.75); text-align: center; }
.link { color: #ffffff; text-decoration: none; border-bottom: 1px solid rgba(255,255,255,0.35); }
.link:hover { border-bottom-color: rgba(255,255,255,0.8); }
</style>
