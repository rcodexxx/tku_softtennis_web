<template>
  <div class="stat-card">
    <span class="icon"><n-icon :component="icon" size="18" /></span>
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
    // 舊參數，HUD 風格統一用重點色，保留以免呼叫端出錯
    accent: { type: String, default: null },
    decimals: { type: Number, default: 0 },
    suffix: { type: String, default: '' }
  })
</script>

<style scoped>
  /* HUD 讀數：細框、等寬數字，圖示只當作小記號 */
  .stat-card {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding: 14px 16px;
    background: var(--surface);
    border: 1px solid var(--line-soft);
    border-top: 2px solid var(--accent);
  }
  .icon {
    order: 2;
    display: flex;
    color: var(--ink-4);
  }
  .body {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }
  .label {
    font-family: var(--font-mono);
    font-size: 13px;
    letter-spacing: 0.1em;
    color: var(--ink-3);
  }
  .value {
    font-size: 28px;
    font-weight: 500;
    line-height: 1.1;
    color: var(--ink);
  }
</style>
