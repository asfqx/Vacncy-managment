<template>
  <DashboardShell
    title="Главная"
    :subtitle="pageSubtitle"
    :role-label="roleLabel"
    :nav-items="navItems"
    :primary-action="primaryAction"
    :secondary-action="secondaryAction"
    home-path="/home"
    :avatar-letter="avatarLetter"
  >
    <section class="hero panel">
      <div class="hero__content">
        <p class="eyebrow">Vacancy Management</p>
        <h2 class="hero__title">Найти работу и сотрудников можно быстрее и спокойнее</h2>
        <p class="hero__text">
          Vacancy Management объединяет поиск, отклики, рекомендации и управление вакансиями в одном месте.
          Соискателю проще сосредоточиться на сильных откликах, а работодателю быстрее находить релевантных кандидатов.
        </p>
        <p class="hero__text">
          Мы собрали удобный сценарий и для кандидатов, и для компаний: от первого поиска до финального выбора.
        </p>
      </div>

      <div class="hero__actions">
        <RouterLink class="heroButton heroButton--primary" :to="searchStartPath">Начать поиск</RouterLink>
      </div>
    </section>

    <section class="reasonsGrid">
      <article class="panel reasonCard reasonCard--wide">
        <p class="eyebrow">Почему сервис удобен</p>
        <h3 class="sectionTitle">Не просто список вакансий, а цельный процесс найма</h3>
        <p class="reasonText">
          Платформа помогает пройти весь путь целиком: искать, фильтровать, откликаться, оформлять профиль и управлять наймом без лишней рутины.
        </p>
      </article>

      <article class="panel reasonCard">
        <h3 class="reasonTitle">Экономит время</h3>
        <p class="reasonText">
          Кандидату не нужно заново собирать информацию для каждого отклика. Работодатель не тратит часы на хаотичный просмотр нерелевантных анкет.
        </p>
      </article>

      <article class="panel reasonCard">
        <h3 class="reasonTitle">Подходит и большим, и небольшим командам</h3>
        <p class="reasonText">
          Сервис одинаково полезен как для крупных HR-команд, так и для малого бизнеса, студий и стартапов.
        </p>
      </article>
    </section>

    <section class="audienceGrid">
      <article class="panel audienceCard">
        <p class="eyebrow">Для соискателей</p>
        <ul class="featureList">
          <li>Ищите вакансии с удобными фильтрами</li>
          <li>Получайте более точные рекомендации</li>
          <li>Создавайте сильное резюме и отклики</li>
          <li>Быстрее ориентируйтесь в актуальных предложениях</li>
        </ul>
      </article>

      <article class="panel audienceCard">
        <p class="eyebrow">Для работодателей</p>
        <ul class="featureList">
          <li>Публикуйте вакансии и обновляйте их в одном месте</li>
          <li>Ищите подходящие резюме по фильтрам</li>
          <li>Управляйте откликами и воронкой найма</li>
          <li>Держите профиль компании и контакты под рукой</li>
        </ul>
      </article>
    </section>
  </DashboardShell>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";
import DashboardShell from "../components/layouts/DashboardShell.vue";
import { getRoleLabel, getUserRoleFromToken, isAdminRole, isEmployerRole } from "../utils/auth";

const role = getUserRoleFromToken();
const employer = isEmployerRole(role);
const roleLabel = computed(() => getRoleLabel(role));
const avatarLetter = computed(() => String(roleLabel.value || "V").slice(0, 1).toUpperCase());
const pageSubtitle = computed(() => (
  employer
    ? "Ключевые возможности сервиса для найма, вакансий и откликов в одном рабочем пространстве."
    : "Ключевые возможности сервиса для поиска вакансий, откликов и развития карьеры."
));
const primaryAction = computed(() => (
  employer
    ? { to: "/employer/vacancies/create", label: "Создать вакансию" }
    : { to: "/vacancies", label: "Найти работу" }
));
const searchStartPath = computed(() => (employer ? "/employer/resumes" : "/vacancies"));
const secondaryAction = computed(() => (
  employer && isAdminRole(role) ? { to: "/vacancies", label: "Страница кандидата" } : null
));
const navItems = computed(() => (
  employer
    ? [
        { to: "/home", label: "Главная" },
        { to: "/employer/resumes", label: "Поиск резюме" },
        { to: "/employer/vacancies", label: "Мои вакансии" },
        { to: "/employer/applications", label: "Отклики" },
        { to: "/employer/vacancies/create", label: "Создать вакансию" },
        { to: "/profile", label: "Профиль" },
      ]
    : [
        { to: "/home", label: "Главная" },
        { to: "/vacancies", label: "Поиск вакансий" },
        { to: "/candidate/applications", label: "Мои отклики" },
        { to: "/candidate/resume", label: "Мои резюме" },
        { to: "/profile", label: "Профиль" },
      ]
));
</script>

<style scoped>
.panel { border-radius: 28px; border: 1px solid rgba(255,255,255,0.08); background: linear-gradient(180deg, rgba(18,19,27,0.96), rgba(11,12,17,0.98)); box-shadow: 0 18px 44px rgba(0,0,0,0.24); }
.eyebrow { margin: 0 0 12px; color: #8eb4ff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; }
.hero { padding: 34px; display: grid; gap: 28px; }
.hero__content { max-width: 920px; }
.hero__title { margin: 0; max-width: 18ch; font-size: clamp(36px, 5vw, 60px); line-height: 1.02; }
.hero__text { margin: 18px 0 0; max-width: 68ch; color: rgba(255,255,255,0.76); line-height: 1.75; font-size: 16px; }
.hero__actions { display: flex; gap: 12px; }
.heroButton { min-height: 48px; padding: 0 18px; border-radius: 999px; display: inline-flex; align-items: center; justify-content: center; text-decoration: none; font-weight: 700; }
.heroButton--primary { background: linear-gradient(135deg, #2f73ff, #5a93ff); color: #fff; border: 1px solid rgba(47,115,255,0.4); }
.reasonsGrid, .audienceGrid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.reasonCard, .audienceCard { padding: 24px; }
.reasonCard--wide { grid-column: 1 / -1; }
.sectionTitle { margin: 0; font-size: clamp(28px, 4vw, 42px); line-height: 1.1; }
.reasonTitle { margin: 0; font-size: 30px; line-height: 1.1; }
.reasonText { margin: 16px 0 0; color: rgba(255,255,255,0.74); line-height: 1.75; }
.featureList { margin: 18px 0 0; padding: 0; list-style: none; display: grid; gap: 10px; }
.featureList li { position: relative; padding-left: 18px; color: rgba(255,255,255,0.82); line-height: 1.6; }
.featureList li::before { content: ""; position: absolute; left: 0; top: 10px; width: 8px; height: 8px; border-radius: 999px; background: #2f73ff; box-shadow: 0 0 0 6px rgba(47,115,255,0.14); }
@media (max-width: 980px) { .reasonsGrid, .audienceGrid { grid-template-columns: 1fr; } .reasonCard--wide { grid-column: auto; } .hero, .reasonCard, .audienceCard { padding: 22px; } .hero__title { max-width: none; } }
</style>
