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
        <h2 class="hero__title">Vacancy Management — найти работу и сотрудников проще, быстрее и умнее</h2>
        <p class="hero__text">
          Не тратьте часы на однотипные отклики и бесконечный просмотр вакансий.
          Vacancy Management помогает соискателям находить действительно подходящие предложения, а компаниям — быстрее закрывать вакансии.
        </p>

        <p class="hero__text">
          Мы объединили удобный поиск вакансий, интеллектуальные рекомендации, помощь с резюме и сопроводительными письмами, а для работодателей — понятное управление вакансиями, откликами и этапами подбора.
        </p>
      </div>

      <div class="hero__actions">
        <RouterLink class="heroButton heroButton--primary" :to="searchStartPath">Начать поиск</RouterLink>
      </div>
    </section>

    <section class="reasonsGrid">
      <article class="panel reasonCard reasonCard--wide">
        <p class="eyebrow">Почему выбирают нас</p>
        <h3 class="sectionTitle">Мы решаем не одну задачу, а весь процесс целиком</h3>
        <p class="reasonText">
          Большинство платформ дают только размещение вакансий или базовый поиск. Vacancy Management помогает пройти весь путь: от поиска подходящей вакансии до грамотного отклика, от публикации вакансии до выбора подходящего кандидата.
        </p>
      </article>

      <article class="panel reasonCard">
        <h3 class="reasonTitle">Мы экономим время</h3>
        <p class="reasonText">
          Соискателю не нужно заново писать одно и то же под каждую вакансию. Работодателю не нужно вручную просматривать десятки нерелевантных откликов.
        </p>
      </article>

      <article class="panel reasonCard">
        <h3 class="reasonTitle">Мы удобны не только крупным компаниям</h3>
        <p class="reasonText">
          Наше решение подходит не только большим HR-командам, но и малому бизнесу, стартапам и компаниям, которым нужен понятный и доступный инструмент найма.
        </p>
      </article>
    </section>

    <section class="audienceGrid">
      <article class="panel audienceCard">
        <p class="eyebrow">Для соискателей</p>
        <ul class="featureList">
          <li>Получайте рекомендации на основе ваших навыков и опыта</li>
          <li>Быстро фильтруйте вакансии по важным параметрам</li>
          <li>Создавайте более сильные отклики с помощью AI</li>
          <li>Генерируйте сопроводительные письма под конкретную вакансию</li>
          <li>Понимайте, где вы подходите лучше всего и что можно усилить</li>
        </ul>
        <p class="sectionText">
          Начать карьеру или найти следующую работу бывает сложно: вакансий много, времени мало, а хорошие отклики требуют сил. Vacancy Management берет рутину на себя и помогает сосредоточиться на главном — выбрать лучшие возможности и показать себя работодателю с сильной стороны.
        </p>
      </article>

      <article class="panel audienceCard">
        <p class="eyebrow">Для работодателей</p>
        <p class="sectionLead">Меньше рутины. Больше подходящих кандидатов. Больше контроля над наймом.</p>
        <ul class="featureList">
          <li>Публикуйте и редактируйте вакансии в одном месте</li>
          <li>Получайте отклики и управляйте ими без хаоса</li>
          <li>Быстрее находите релевантных кандидатов</li>
          <li>Отслеживайте этапы подбора и историю взаимодействий</li>
          <li>Работайте удобнее даже без большой HR-команды</li>
        </ul>
        <p class="sectionText">
          Когда бизнес растет, времени на долгий ручной подбор просто нет. Vacancy Management помогает структурировать процесс найма, сократить лишние действия и быстрее находить людей, которые действительно подходят вашей команде.
        </p>
      </article>
    </section>

    <section class="panel strengthSection">
      <p class="eyebrow">Преимущества</p>
      <h3 class="sectionTitle">Что делает Vacancy Management сильнее обычных платформ</h3>
      <div class="strengthGrid">
        <article class="strengthItem">
          <h4>Интеллектуальный подбор</h4>
          <p>Сервис помогает находить более релевантные вакансии и кандидатов, а не просто показывает список по ключевым словам.</p>
        </article>
        <article class="strengthItem">
          <h4>Помощь с откликом</h4>
          <p>Сопроводительные письма и подготовка отклика становятся быстрее, проще и качественнее.</p>
        </article>
        <article class="strengthItem">
          <h4>Удобство для обеих сторон</h4>
          <p>Платформа одинаково полезна и соискателям, и работодателям.</p>
        </article>
        <article class="strengthItem">
          <h4>Современный подход</h4>
          <p>Поиск, рекомендации, отклики и управление вакансиями собраны в одной системе.</p>
        </article>
      </div>
    </section>

    <section class="panel emotionSection">
      <h3 class="sectionTitle">Мы создали сервис, который помогает и людям, и компаниям встретиться вовремя.</h3>
    </section>

    <section class="panel ctaSection">
      <div>
        <p class="eyebrow">Попробуйте сервис</p>
        <h3 class="sectionTitle">Попробуйте Vacancy Management и убедитесь, что поиск работы и подбор сотрудников могут быть удобными</h3>
        <p class="sectionText">
          Начните с нескольких кликов: создайте профиль, загрузите резюме или опубликуйте вакансию — остальное мы поможем упростить.
        </p>
      </div>
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
.panel {
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}

.eyebrow {
  margin: 0 0 12px;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.hero {
  padding: 34px;
  display: grid;
  gap: 28px;
}

.hero__content {
  max-width: 920px;
}

.hero__title {
  margin: 0;
  max-width: 18ch;
  font-size: clamp(36px, 5vw, 60px);
  line-height: 1.02;
}

.hero__text {
  margin: 18px 0 0;
  max-width: 68ch;
  color: rgba(255, 255, 255, 0.76);
  line-height: 1.75;
  font-size: 16px;
}

.hero__actions,
.ctaActions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.heroButton {
  min-height: 48px;
  padding: 0 18px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-weight: 700;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.heroButton:hover {
  transform: translateY(-1px);
}

.heroButton--primary {
  background: linear-gradient(135deg, #2f73ff, #5a93ff);
  color: #fff;
  border: 1px solid rgba(47, 115, 255, 0.4);
}

.heroButton--secondary {
  background: rgba(255, 255, 255, 0.04);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.introSection,
.strengthSection,
.emotionSection,
.ctaSection {
  padding: 28px;
}

.sectionTitle {
  margin: 0;
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.1;
}

.sectionLead {
  margin: 16px 0 0;
  color: #eef2ff;
  font-size: 18px;
  line-height: 1.55;
}

.sectionText,
.reasonText,
.strengthItem p {
  margin: 16px 0 0;
  color: rgba(255, 255, 255, 0.74);
  line-height: 1.75;
}

.reasonsGrid,
.audienceGrid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.reasonCard,
.audienceCard {
  padding: 24px;
}

.reasonCard--wide {
  grid-column: 1 / -1;
}

.reasonTitle {
  margin: 0;
  font-size: 30px;
  line-height: 1.1;
}

.featureList {
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 10px;
}

.featureList li {
  position: relative;
  padding-left: 18px;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.6;
}

.featureList li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 10px;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #2f73ff;
  box-shadow: 0 0 0 6px rgba(47, 115, 255, 0.14);
}

.strengthGrid {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.strengthItem {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.strengthItem h4 {
  margin: 0;
  font-size: 22px;
}

.ctaSection {
  display: grid;
  gap: 22px;
}

@media (max-width: 980px) {
  .reasonsGrid,
  .audienceGrid,
  .strengthGrid {
    grid-template-columns: 1fr;
  }

  .reasonCard--wide {
    grid-column: auto;
  }

  .hero,
  .introSection,
  .strengthSection,
  .emotionSection,
  .ctaSection,
  .reasonCard,
  .audienceCard {
    padding: 22px;
  }

  .hero__title {
    max-width: none;
  }
}
</style>