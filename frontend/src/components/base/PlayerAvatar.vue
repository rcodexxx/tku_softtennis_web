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
        :fill="pattern.color"
      />
    </svg>
  </span>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'
  import { identicon } from '@/utils/identicon'

  /** 球員頭像：有照片顯示照片，沒有則顯示 GitHub 風格的幾何圖案（依球員 id 或姓名產生）。ring 可加上金銀銅外框。 */
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
    width: var(--size);
    height: var(--size);
    flex-shrink: 0;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    background: #f0f2f5;
    box-shadow: 0 0 0 2px #fff;
  }
  .player-avatar svg {
    width: 100%;
    height: 100%;
  }
  .player-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .ring-gold {
    box-shadow:
      0 0 0 3px #fff,
      0 0 0 6px var(--gold-500);
  }
  .ring-silver {
    box-shadow:
      0 0 0 3px #fff,
      0 0 0 6px var(--silver-500);
  }
  .ring-bronze {
    box-shadow:
      0 0 0 3px #fff,
      0 0 0 6px var(--bronze-500);
  }
</style>
