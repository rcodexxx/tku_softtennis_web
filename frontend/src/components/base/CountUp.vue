<template>
  <span class="num">{{ display }}</span>
</template>

<script setup>
  import { computed, onMounted, ref, watch } from 'vue'

  /** 數字從 0 滾動到目標值。 */
  const props = defineProps({
    value: { type: Number, default: 0 },
    decimals: { type: Number, default: 0 },
    duration: { type: Number, default: 900 },
    suffix: { type: String, default: '' }
  })

  const current = ref(0)
  const display = computed(() => `${current.value.toFixed(props.decimals)}${props.suffix}`)

  const animate = (from, to) => {
    const start = performance.now()
    const step = now => {
      const progress = Math.min(1, (now - start) / props.duration)
      const eased = 1 - Math.pow(1 - progress, 3)
      current.value = from + (to - from) * eased
      if (progress < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }

  onMounted(() => animate(0, props.value))
  watch(
    () => props.value,
    (to, from) => animate(from ?? 0, to)
  )
</script>
