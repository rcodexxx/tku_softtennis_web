<template>
  <span v-if="points !== null" class="score-change num" :class="direction">
    <span class="arrow">{{ direction === 'up' ? '▲' : direction === 'down' ? '▼' : '–' }}</span>
    {{ points === 0 ? '' : Math.abs(points).toFixed(1) }}
  </span>
</template>

<script setup>
  import { computed } from 'vue'

  /** 比賽造成的分數變化，和分數一樣顯示到小數點一位。 */
  const props = defineProps({ change: { type: Number, default: null } })

  const points = computed(() => (props.change === null ? null : Math.round(props.change * 10) / 10))
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
