<template>
  <span class="recent-form" :aria-label="`最近 ${form.length} 場：${form.join('')}`">
    <span v-for="(result, index) in slots" :key="index" class="dot" :class="result ? result.toLowerCase() : 'empty'">
      {{ result === 'W' ? '勝' : result === 'L' ? '敗' : '' }}
    </span>
  </span>
</template>

<script setup>
  import { computed } from 'vue'

  /** 最近 5 場的勝負，最新的在左邊。 */
  const props = defineProps({
    form: { type: Array, default: () => [] },
    size: { type: Number, default: 5 }
  })

  const slots = computed(() => Array.from({ length: props.size }, (_, i) => props.form[i] || null))
</script>

<style scoped>
  .recent-form {
    display: inline-flex;
    gap: 4px;
  }
  .dot {
    width: 20px;
    height: 20px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: #fff;
  }
  .w {
    background: var(--color-win);
  }
  .l {
    background: var(--color-loss);
  }
  .empty {
    background: var(--gray-200);
  }
</style>
