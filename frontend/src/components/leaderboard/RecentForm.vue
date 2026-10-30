<template>
  <span class="recent-form" :aria-label="`最近 ${form.length} 場：${form.join('')}`">
    <span
      v-for="(result, index) in slots"
      :key="index"
      class="dot"
      :class="result ? result.toLowerCase() : 'empty'"
      :title="result === 'W' ? '勝' : result === 'L' ? '敗' : '尚無比賽'"
    ></span>
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
    gap: 3px;
  }
  /* 勝：實心綠方塊；敗：實心紅方塊；沒比賽：空框 */
  .dot {
    width: 10px;
    height: 10px;
  }
  .w {
    background: var(--win);
  }
  .l {
    background: var(--loss);
  }
  .empty {
    border: 1px solid var(--line);
  }
</style>
