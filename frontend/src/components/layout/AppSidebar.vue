<template>
  <aside class="sidebar">
    <router-link :to="{ name: 'Leaderboard' }" class="brand">
      <span class="brand-ball" aria-hidden="true"></span>
      <span class="brand-text">
        <span class="brand-title">TKU 軟網</span>
        <span class="brand-subtitle">Soft Tennis Stats</span>
      </span>
    </router-link>

    <nav class="nav">
      <router-link
        v-for="item in sidebarItems"
        :key="item.name"
        :to="{ name: item.name }"
        class="nav-item"
        active-class="active"
        exact-active-class="active"
      >
        <n-icon :component="item.icon" size="20" />
        <span>{{ item.label }}</span>
        <span v-if="item.beta" class="beta">Beta</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <UserMenu />
    </div>
  </aside>
</template>

<script setup>
  import { useNavItems } from '@/composables/useNavItems'
  import UserMenu from './UserMenu.vue'

  const { sidebarItems } = useNavItems()
</script>

<style scoped>
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    width: var(--sidebar-width);
    display: flex;
    flex-direction: column;
    padding: 20px 14px;
    background: linear-gradient(180deg, var(--blue-900) 0%, var(--blue-950) 100%);
    color: #e6edfb;
    z-index: 20;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 10px 22px;
  }
  .brand-ball {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #fff 0 18%, var(--gold-300) 19% 100%);
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.12);
    position: relative;
    animation: ball-bounce 2.4s var(--ease-out) infinite;
  }
  @keyframes ball-bounce {
    0%,
    100% {
      transform: translateY(0) rotate(0deg);
    }
    50% {
      transform: translateY(-4px) rotate(180deg);
    }
  }
  .brand-text {
    display: flex;
    flex-direction: column;
    line-height: 1.15;
  }
  .brand-title {
    font-size: 18px;
    font-weight: 800;
    color: #fff;
    letter-spacing: 0.04em;
  }
  .brand-subtitle {
    font-family: var(--font-number);
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--blue-200);
  }
  .nav {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
  }
  .nav-item {
    position: relative;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 14px;
    border-radius: var(--radius-md);
    font-weight: 600;
    font-size: 15px;
    color: var(--blue-200);
    transition:
      background var(--duration-fast),
      color var(--duration-fast),
      transform var(--duration-fast);
  }
  .nav-item:hover {
    background: rgba(255, 255, 255, 0.06);
    color: #fff;
    transform: translateX(2px);
  }
  .nav-item.active {
    background: rgba(91, 140, 240, 0.18);
    color: #fff;
  }
  .nav-item.active::before {
    content: '';
    position: absolute;
    left: -14px;
    top: 10px;
    bottom: 10px;
    width: 4px;
    border-radius: 0 4px 4px 0;
    background: var(--red-500);
  }
  .beta {
    margin-left: auto;
    padding: 1px 8px;
    border-radius: var(--radius-full);
    background: var(--gold-500);
    color: var(--blue-950);
    font-size: 11px;
    font-weight: 800;
  }
  .sidebar-footer {
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }
</style>
