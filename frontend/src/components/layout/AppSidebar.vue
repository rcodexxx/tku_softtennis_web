<template>
  <aside class="sidebar">
    <BrandMark class="brand" />

    <nav class="nav">
      <span class="hud-label nav-title">Menu</span>
      <router-link
        v-for="item in items"
        :key="item.name"
        :to="{ name: item.name }"
        class="nav-item"
        :class="{ active: isActive(item) }"
      >
        <span class="code">{{ item.code }}</span>
        <span class="label">{{ item.label }}</span>
        <n-icon :component="item.icon" size="18" class="icon" />
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <ThemeToggle label class="theme" />
      <UserMenu />
    </div>
  </aside>
</template>

<script setup>
  import { useNavItems } from '@/composables/useNavItems'
  import BrandMark from './BrandMark.vue'
  import ThemeToggle from './ThemeToggle.vue'
  import UserMenu from './UserMenu.vue'

  const { items, isActive } = useNavItems()
</script>

<style scoped>
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    width: var(--sidebar-width);
    display: flex;
    flex-direction: column;
    padding: 22px 16px 16px;
    background: var(--surface);
    border-right: 1px solid var(--line-soft);
    z-index: 20;
  }
  .brand {
    padding: 0 6px 26px;
  }
  .nav {
    display: flex;
    flex-direction: column;
    gap: 2px;
    flex: 1;
  }
  .nav-title {
    padding: 0 10px 8px;
  }
  .nav-item {
    position: relative;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 10px;
    color: var(--ink-3);
    transition:
      background var(--duration-fast),
      color var(--duration-fast);
  }
  .nav-item:hover {
    background: var(--surface-sunk);
    color: var(--ink);
  }
  .code {
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--ink-4);
  }
  .label {
    flex: 1;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 0.04em;
  }
  .icon {
    opacity: 0.6;
  }
  /* 目前位置：反白成墨色，左邊一條重點色 */
  .nav-item.active {
    background: var(--ink);
    color: var(--bg);
  }
  .nav-item.active .code {
    color: var(--accent);
  }
  .nav-item.active .icon {
    opacity: 1;
  }
  .nav-item.active::before {
    content: '';
    position: absolute;
    left: -16px;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--accent);
  }
  .sidebar-footer {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding-top: 14px;
    border-top: 1px solid var(--line-soft);
  }
  .theme {
    align-self: flex-start;
  }
</style>
