<template>
  <header class="page-header">
    <div class="titles">
      <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
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
    margin: 0 0 6px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--color-accent);
  }
  .title {
    margin: 0;
    font-size: clamp(24px, 3vw, 32px);
    font-weight: 800;
    color: var(--blue-900);
    letter-spacing: 0.01em;
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
