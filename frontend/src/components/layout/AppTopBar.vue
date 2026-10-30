<template>
  <header class="topbar">
    <BrandMark compact />
    <div class="actions">
      <ThemeToggle />
      <UserMenu compact />
    </div>
  </header>
</template>

<script setup>
  import BrandMark from './BrandMark.vue'
  import ThemeToggle from './ThemeToggle.vue'
  import UserMenu from './UserMenu.vue'
</script>

<style scoped>
  .topbar {
    position: sticky;
    top: 0;
    z-index: 20;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: color-mix(in srgb, var(--surface) 92%, transparent);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--line-soft);
  }
  .actions {
    display: flex;
    align-items: center;
    gap: 10px;
  }
</style>
