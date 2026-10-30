<template>
  <header class="page-header">
    <div class="titles">
      <p v-if="eyebrow" class="eyebrow hud-label">{{ eyebrow }}</p>
      <h1 class="title">{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="actions">
      <slot name="actions"></slot>
    </div>
  </header>
</template>

<script setup>
  defineProps({
    title: { type: String, required: true },
    subtitle: { type: String, default: '' },
    eyebrow: { type: String, default: '' }
  })
</script>

<style scoped>
  .page-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 24px;
  }
  .eyebrow {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 8px;
  }
  /* 標籤前的小方塊，像 HUD 的狀態燈 */
  .eyebrow::before {
    content: '';
    width: 6px;
    height: 6px;
    background: var(--accent);
  }
  .title {
    margin: 0;
    font-size: clamp(24px, 3vw, 32px);
    font-weight: 700;
    color: var(--ink);
    letter-spacing: 0.04em;
  }
  .subtitle {
    margin: 6px 0 0;
    color: var(--color-text-muted);
    font-size: 14px;
  }
  .actions {
    display: flex;
    gap: 8px;
  }
</style>
