<template>
  <button
    type="button"
    class="theme-toggle"
    :aria-label="isDark ? '切換成淺色模式' : '切換成深色模式'"
    @click="toggleTheme"
  >
    <n-icon :component="isDark ? Sun : Moon" size="18" />
    <span v-if="label" class="hud-label">{{ isDark ? 'Light' : 'Dark' }}</span>
  </button>
</template>

<script setup>
  import { Moon, Sun } from '@vicons/carbon'
  import { useTheme } from '@/composables/useTheme'

  defineProps({ label: { type: Boolean, default: false } })
  const { isDark, toggleTheme } = useTheme()
</script>

<style scoped>
  .theme-toggle {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 9px;
    border: 1px solid var(--line);
    background: transparent;
    color: var(--ink-2);
    cursor: pointer;
    transition:
      border-color var(--duration-fast),
      color var(--duration-fast);
  }
  .theme-toggle:hover {
    border-color: var(--ink);
    color: var(--ink);
  }
</style>
