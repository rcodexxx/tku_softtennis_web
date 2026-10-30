<template>
  <div class="auth-layout">
    <section class="brand-panel" aria-hidden="true">
      <div class="court">
        <span class="line baseline"></span>
        <span class="line service"></span>
        <span class="line center"></span>
        <span class="net"></span>
      </div>
      <span class="ball ball-1"></span>
      <span class="ball ball-2"></span>
      <div class="brand-copy">
        <span class="brand-mark"></span>
        <h1>TKU 軟網</h1>
        <p>記錄每一場比賽，看見每一分進步。</p>
      </div>
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
    align-items: flex-end;
    padding: 56px;
    background: var(--ink);
    color: var(--bg);
  }
  .court {
    position: absolute;
    inset: 12% 10% 28% 10%;
    border: 2px solid color-mix(in srgb, var(--bg) 16%, transparent);
    border-radius: 6px;
    transform: perspective(700px) rotateX(48deg);
    transform-origin: bottom;
  }
  .line {
    position: absolute;
    background: color-mix(in srgb, var(--bg) 16%, transparent);
  }
  .service {
    left: 0;
    right: 0;
    top: 30%;
    height: 2px;
  }
  .baseline {
    left: 0;
    right: 0;
    bottom: 30%;
    height: 2px;
  }
  .center {
    top: 30%;
    bottom: 30%;
    left: 50%;
    width: 2px;
  }
  .net {
    position: absolute;
    left: -4%;
    right: -4%;
    top: 50%;
    height: 10px;
    background: repeating-linear-gradient(
      90deg,
      color-mix(in srgb, var(--bg) 35%, transparent) 0 2px,
      transparent 2px 10px
    );
    border-top: 3px solid color-mix(in srgb, var(--bg) 60%, transparent);
  }
  .ball {
    position: absolute;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  }
  .ball-1 {
    width: 54px;
    height: 54px;
    left: 18%;
    top: 22%;
    animation: rally 3.6s ease-in-out infinite;
  }
  .ball-2 {
    width: 30px;
    height: 30px;
    right: 22%;
    top: 46%;
    opacity: 0.7;
    animation: rally 3.6s ease-in-out infinite reverse;
  }
  @keyframes rally {
    0%,
    100% {
      transform: translate(0, 0);
    }
    50% {
      transform: translate(140px, -60px);
    }
  }
  .brand-copy {
    position: relative;
    z-index: 1;
  }
  .brand-mark {
    display: block;
    width: 48px;
    height: 6px;
    border-radius: 3px;
    background: var(--red-500);
    margin-bottom: 18px;
  }
  .brand-copy h1 {
    margin: 0;
    font-size: 44px;
    font-weight: 900;
    letter-spacing: 0.06em;
  }
  .brand-copy p {
    margin: 10px 0 0;
    font-size: 18px;
    color: var(--blue-200);
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
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-muted);
  }
  .back-link:hover {
    color: var(--color-primary);
  }
  .form-title {
    margin: 0;
    font-size: 30px;
    font-weight: 800;
    color: var(--blue-900);
  }
  .form-subtitle {
    margin: 8px 0 28px;
    color: var(--color-text-muted);
  }

  @media (max-width: 900px) {
    .auth-layout {
      grid-template-columns: 1fr;
      grid-template-rows: 220px 1fr;
    }
    .brand-panel {
      padding: 28px;
    }
    .brand-copy h1 {
      font-size: 32px;
    }
    .brand-copy p {
      font-size: 15px;
    }
    .court {
      inset: 10% 6% 20% 6%;
    }
  }
</style>
