<template>
  <div class="page">
    <div class="orb orb--blue"></div>
    <div class="orb orb--coral"></div>

    <section class="shell">
      <aside class="brandPanel">
        <div class="brandMark">vm</div>
        <p class="eyebrow">Vacancy Management</p>
        <h1 class="brandTitle">Единое пространство для найма и откликов</h1>
        <p class="brandText">
          Управляйте аккаунтом, вакансиями и коммуникацией в одном спокойном интерфейсе.
        </p>

        <div class="brandNotes">
          <div class="note">
            <strong>Больше подходящих совпадений</strong>
            <span>Кандидат быстрее находит интересные вакансии, а работодатель получает более релевантные отклики.</span>
          </div>
          <div class="note">
            <strong>Меньше рутины</strong>
            <span>Меньше лишних шагов, больше времени на поиск работы, отклики и общение с подходящими людьми.</span>
          </div>
        </div>
      </aside>

      <div class="card">
        <div class="card__inner">
          <h2 class="title">{{ title }}</h2>
          <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
          <slot />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: "Вход" },
  subtitle: { type: String, default: "" },
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at top left, rgba(47, 115, 255, 0.22), transparent 26%),
    radial-gradient(circle at right, rgba(255, 122, 89, 0.16), transparent 22%),
    #0b0c10;
  padding: 28px;
  color: #e8e8e8;
}

.orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(70px);
  opacity: 0.45;
  pointer-events: none;
}

.orb--blue {
  width: 260px;
  height: 260px;
  top: 40px;
  left: -40px;
  background: rgba(47, 115, 255, 0.28);
}

.orb--coral {
  width: 220px;
  height: 220px;
  right: -30px;
  bottom: 30px;
  background: rgba(255, 122, 89, 0.22);
}

.shell {
  position: relative;
  z-index: 1;
  width: min(1120px, 100%);
  display: grid;
  grid-template-columns: minmax(320px, 0.9fr) minmax(380px, 0.82fr);
  gap: 22px;
  align-items: stretch;
}

.brandPanel,
.card {
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(18, 19, 27, 0.96), rgba(11, 12, 17, 0.98));
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}

.brandPanel {
  padding: 28px;
  display: grid;
  align-content: start;
  gap: 18px;
}

.brandMark {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #ff7a59, #2f73ff);
  color: #fff;
  font-weight: 900;
  text-transform: uppercase;
}

.eyebrow {
  margin: 0;
  color: #8eb4ff;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.brandTitle {
  margin: 0;
  font-size: 38px;
  line-height: 1.05;
}

.brandText {
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.7;
  max-width: 42ch;
}

.brandNotes {
  display: grid;
  gap: 12px;
  margin-top: 6px;
}

.note {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: grid;
  gap: 6px;
}

.note strong {
  font-size: 15px;
}

.note span {
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.55;
}

.card {
  padding: 28px;
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card__inner {
  width: 100%;
  display: grid;
  align-content: center;
}

.title {
  font-size: 28px;
  line-height: 1.1;
  margin: 0 0 8px;
  text-align: center;
}

.subtitle {
  margin: 0 0 20px;
  color: rgba(232, 232, 232, 0.66);
  font-size: 14px;
  line-height: 1.55;
  text-align: center;
}

@media (max-width: 920px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .brandPanel {
    gap: 14px;
  }

  .brandTitle {
    font-size: 32px;
  }

  .card {
    min-height: auto;
  }
}
</style>