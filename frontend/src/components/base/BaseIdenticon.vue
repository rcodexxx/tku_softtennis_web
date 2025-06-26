<!-- frontend/src/components/base/BaseIdenticon.vue -->
<template>
  <svg
    ref="svgRef"
    :width="size"
    :height="size"
    class="identicon"
    :class="{ 'rounded': rounded }"
  />
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { generateUserIdenticon } from '@/utils/identicon'

const props = defineProps({
  user: { type: Object, required: true },
  size: { type: Number, default: 40 },
  useRealName: { type: Boolean, default: true },
  rounded: { type: Boolean, default: true }
})

const svgRef = ref()

watchEffect(async () => {
  if (props.user && svgRef.value) {
    await generateUserIdenticon(svgRef.value, props.user, {
      useRealName: props.useRealName
    })
  }
})
</script>

<style scoped>
.identicon {
  display: block;
}

.identicon.rounded {
  border-radius: 50%;
}
</style>