<template>
  <div class="stat-card" :style="{ '--accent': accent }">
    <span class="icon"><n-icon :component="icon" size="22" /></span>
    <div class="body">
      <span class="label">{{ label }}</span>
      <CountUp class="value" :value="value" :decimals="decimals" :suffix="suffix" />
    </div>
  </div>
</template>

<script setup>
  import CountUp from './CountUp.vue'

  defineProps({
    label: { type: String, required: true },
    value: { type: Number, default: 0 },
    icon: { type: [Object, Function], required: true },
    accent: { type: String, default: 'var(--blue-600)' },
    decimals: { type: Number, default: 0 },
    suffix: { type: String, default: '' }
  })
</script>

<style scoped>
  .stat-card {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 18px;
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    transition:
      transform var(--duration-base) var(--ease-spring),
      box-shadow var(--duration-base);
  }
  .stat-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
  }
  .icon {
    width: 44px;
    height: 44px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent);
    background: color-mix(in srgb, var(--accent) 12%, transparent);
  }
  .body {
    display: flex;
    flex-direction: column;
  }
  .label {
    font-size: 13px;
    color: var(--color-text-muted);
    font-weight: 600;
  }
  .value {
    font-size: 30px;
    font-weight: 700;
    line-height: 1.1;
    color: var(--blue-900);
  }
</style>
