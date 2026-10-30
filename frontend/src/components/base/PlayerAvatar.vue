<template>
  <span class="player-avatar" :class="[`ring-${ring}`]" :style="{ '--size': `${size}px` }">
    <img v-if="src && !imageFailed" :src="src" :alt="name" @error="imageFailed = true" />
    <svg v-else viewBox="-1.25 -1.25 7.5 7.5" role="img" :aria-label="name" shape-rendering="crispEdges">
      <rect
        v-for="[x, y] in pattern.cells"
        :key="`${x}-${y}`"
        :x="x"
        :y="y"
        width="1.02"
        height="1.02"
        :fill="`var(--avatar-${pattern.tone})`"
      />
    </svg>
  </span>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'
  import { identicon } from '@/utils/identicon'

  /** 球員頭像：有照片顯示照片，沒有則顯示 GitHub 風格的幾何圖案（依球員 id 或姓名產生）。ring 加上名次外框（gold 為重點色準星）。 */
  const props = defineProps({
    name: { type: String, default: '' },
    id: { type: Number, default: null },
    src: { type: String, default: null },
    size: { type: Number, default: 40 },
    ring: { type: String, default: 'none', validator: value => ['none', 'gold', 'silver', 'bronze'].includes(value) }
  })

  const imageFailed = ref(false)
  watch(
    () => props.src,
    () => (imageFailed.value = false)
  )

  const pattern = computed(() => identicon(props.id ?? props.name))
</script>

<style scoped>
  .player-avatar {
    position: relative;
    width: var(--size);
    height: var(--size);
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 3px;
    background: var(--avatar-bg);
  }
  .player-avatar svg,
  .player-avatar img {
    width: 100%;
    height: 100%;
  }
  .player-avatar img {
    object-fit: cover;
  }
  /* 名次外框：第一名重點色、二三名墨色，外圈留一點間距像準星 */
  .ring-gold,
  .ring-silver,
  .ring-bronze {
    overflow: visible;
    outline: 1px solid var(--ring-color);
    outline-offset: 3px;
  }
  .ring-gold {
    --ring-color: var(--accent);
    outline-width: 2px;
  }
  .ring-silver {
    --ring-color: var(--ink);
  }
  .ring-bronze {
    --ring-color: var(--ink-3);
  }
  .ring-gold img,
  .ring-silver img,
  .ring-bronze img,
  .ring-gold svg,
  .ring-silver svg,
  .ring-bronze svg {
    border-radius: 3px;
  }
</style>
