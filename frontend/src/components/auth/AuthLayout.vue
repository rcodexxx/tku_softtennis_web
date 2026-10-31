<template>
  <div class="auth-layout">
    <section class="brand-panel">
      <span class="hud-label panel-label">TKU // Soft tennis</span>
      <RallyScene class="scene" />
      <h1 class="brand-title">TKU 軟網</h1>
    </section>

    <section class="form-panel">
      <div class="form-card">
        <router-link :to="{ name: 'Leaderboard' }" class="back-link">← 回到排行榜</router-link>
        <h2 class="form-title">{{ title }}</h2>
        <p v-if="subtitle" class="form-subtitle">{{ subtitle }}</p>
        <slot></slot>
      </div>
    </section>
  </div>
</template>

<script setup>
  import RallyScene from './RallyScene.vue'

  defineProps({
    title: { type: String, required: true },
    subtitle: { type: String, default: '' }
  })
</script>

<style scoped>
  .auth-layout {
    min-height: 100vh;
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    background: var(--color-bg);
  }
  .brand-panel {
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 28px;
    padding: 56px;
    background: var(--ink);
    color: var(--bg);
  }
  .panel-label {
    position: absolute;
    top: 32px;
    left: 56px;
    color: color-mix(in srgb, var(--bg) 60%, transparent);
  }
  .scene {
    align-self: center;
  }
  .brand-title {
    margin: 0;
    font-size: 40px;
    font-weight: 700;
    letter-spacing: 0.1em;
  }
  .form-panel {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 32px 20px;
  }
  .form-card {
    width: 100%;
    max-width: 400px;
    animation: stagger-in var(--duration-slow) var(--ease-out) both;
  }
  .back-link {
    display: inline-block;
    margin-bottom: 28px;
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text-muted);
  }
  .back-link:hover {
    color: var(--color-primary);
  }
  .form-title {
    margin: 0 0 24px;
    font-size: 30px;
    font-weight: 700;
    color: var(--ink);
  }
  .form-subtitle {
    margin: 8px 0 28px;
    color: var(--color-text-muted);
  }

  @media (max-width: 900px) {
    .auth-layout {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
    }
    .brand-panel {
      gap: 12px;
      padding: 56px 20px 20px;
    }
    .panel-label {
      top: 20px;
      left: 20px;
    }
    .brand-title {
      font-size: 26px;
    }
  }
</style>
