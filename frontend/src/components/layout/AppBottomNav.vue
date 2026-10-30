<template>
  <nav class="bottom-nav">
    <router-link
      v-for="item in items"
      :key="item.name"
      :to="{ name: item.name }"
      class="tab"
      :class="{ active: isActive(item) }"
    >
      <n-icon :component="item.icon" size="20" />
      <span class="label">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
  import { useNavItems } from '@/composables/useNavItems'

  /** 手機底部分頁列；只有幹部有多個入口，所以只在幹部登入時顯示（見 App.vue）。 */
  const { items, isActive } = useNavItems()
</script>

<style scoped>
  .bottom-nav {
    position: fixed;
    inset: auto 0 0 0;
    height: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
    padding-bottom: env(safe-area-inset-bottom);
    display: flex;
    align-items: stretch;
    background: color-mix(in srgb, var(--surface) 94%, transparent);
    backdrop-filter: blur(12px);
    border-top: 1px solid var(--line-soft);
    z-index: 20;
  }
  .tab {
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    color: var(--ink-3);
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.06em;
    transition: color var(--duration-fast);
  }
  .tab.active {
    color: var(--ink);
  }
  /* 目前位置：上方一條重點色 */
  .tab.active::before {
    content: '';
    position: absolute;
    top: 0;
    left: 30%;
    right: 30%;
    height: 2px;
    background: var(--accent);
  }
</style>
