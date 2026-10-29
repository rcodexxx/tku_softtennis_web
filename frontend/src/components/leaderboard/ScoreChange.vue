<template>
  <span v-if="points !== null" class="score-change num" :class="direction">
    <span class="arrow">{{ direction === 'up' ? '▲' : direction === 'down' ? '▼' : '–' }}</span>
    {{ points === 0 ? '' : Math.abs(points) }}
  </span>
</template>

<script setup>
  import { computed } from 'vue'

  /** 最近一場比賽造成的分數變化（和排行榜分數一樣乘以 100）。 */
  const props = defineProps({ change: { type: Number, default: null } })

  const points = computed(() => (props.change === null ? null : Math.round(props.change * 100)))
  const direction = computed(() => (points.value > 0 ? 'up' : points.value < 0 ? 'down' : 'flat'))
</script>

<style scoped>
  .score-change {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    font-size: 15px;
    font-weight: 600;
  }
  .arrow {
    font-size: 10px;
  }
  .up {
    color: var(--color-win);
  }
  .down {
    color: var(--color-loss);
  }
  .flat {
    color: var(--gray-400);
  }
</style>
