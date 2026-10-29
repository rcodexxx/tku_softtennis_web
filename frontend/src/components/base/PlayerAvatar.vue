<template>
  <span class="player-avatar" :class="[`ring-${ring}`]" :style="{ '--size': `${size}px`, '--bg': color }">
    <img v-if="src && !imageFailed" :src="src" :alt="name" @error="imageFailed = true" />
    <span v-else class="initial">{{ initial }}</span>
  </span>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'
  import { playerColor, playerInitial } from '@/utils/player'

  /** 球員頭像：有照片顯示照片，沒有則顯示姓名第一個字。ring 可加上金銀銅外框。 */
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

  const initial = computed(() => playerInitial(props.name))
  const color = computed(() => playerColor(props.id ?? [...props.name].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)))
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
    background: var(--bg);
    color: #fff;
    font-weight: 700;
    font-size: calc(var(--size) * 0.42);
    box-shadow: 0 0 0 2px #fff;
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
