<template>
  <ul class="abilities">
    <li v-for="(item, index) in items" :key="item.label" class="ability" :style="{ '--i': index }">
      <div class="ability-head">
        <span class="label">{{ item.label }}</span>
        <span class="value num">{{ item.display }}</span>
      </div>
      <div class="track">
        <span class="fill" :style="{ width: `${item.percent}%`, background: item.color }"></span>
      </div>
      <p class="hint">{{ item.hint }}</p>
    </li>
  </ul>
</template>

<script setup>
  import { computed } from 'vue'
  import { EXPERIENCE_LEVELS } from '@/utils/experience'

  const props = defineProps({ member: { type: Object, required: true } })

  const clamp = value => Math.max(0, Math.min(100, value))

  const items = computed(() => {
    const m = props.member
    const levelIndex = EXPERIENCE_LEVELS.findIndex(level => level.label === m.experience_level)
    return [
      {
        label: '潛在實力',
        display: Math.round(m.mu * 100),
        percent: clamp(((m.mu - 15) / 20) * 100),
        color: 'linear-gradient(90deg, var(--blue-400), var(--blue-700))',
        hint: 'TrueSkill μ：不考慮不確定性的實力估計'
      },
      {
        label: '穩定度',
        display: `${m.consistency_rating}%`,
        percent: m.consistency_rating,
        color: 'linear-gradient(90deg, #4ade80, var(--green-600))',
        hint: '比賽打得越多，表現越穩定'
      },
      {
        label: '評分可信度',
        display: `${m.rating_confidence}%`,
        percent: m.rating_confidence,
        color: 'linear-gradient(90deg, var(--gold-300), var(--gold-500))',
        hint: '系統對你目前分數的把握程度'
      },
      {
        label: '經驗等級',
        display: m.experience_level,
        percent: ((levelIndex + 1) / EXPERIENCE_LEVELS.length) * 100,
        color: 'linear-gradient(90deg, #f87171, var(--red-600))',
        hint: EXPERIENCE_LEVELS.map(level => level.label).join(' → ')
      }
    ]
  })
</script>

<style scoped>
  .abilities {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  .ability-head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
  }
  .label {
    font-weight: 700;
    color: var(--gray-700);
  }
  .value {
    font-size: 22px;
    font-weight: 700;
    color: var(--blue-900);
  }
  .track {
    height: 10px;
    border-radius: var(--radius-full);
    background: var(--gray-100);
    overflow: hidden;
  }
  .fill {
    display: block;
    height: 100%;
    border-radius: inherit;
    transform-origin: left;
    animation: grow 1s var(--ease-out) both;
    animation-delay: calc(var(--i) * 120ms + 200ms);
  }
  @keyframes grow {
    from {
      transform: scaleX(0);
    }
  }
  .hint {
    margin: 6px 0 0;
    font-size: 12px;
    color: var(--color-text-muted);
  }
</style>
