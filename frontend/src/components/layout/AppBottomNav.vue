<template>
  <nav class="bottom-nav">
    <router-link
      v-for="item in bottomItems"
      :key="item.name"
      :to="{ name: item.name }"
      class="tab"
      :class="{ primary: item.name === 'RecordMatch' }"
      active-class="active"
    >
      <span class="icon-wrap">
        <n-icon :component="item.icon" :size="item.name === 'RecordMatch' ? 28 : 22" />
      </span>
      <span class="label">{{ item.label }}</span>
    </router-link>
    <router-link v-if="!authStore.isAuthenticated" :to="{ name: 'Login' }" class="tab" active-class="active">
      <span class="icon-wrap"><n-icon :component="LogInOutline" size="22" /></span>
      <span class="label">登入</span>
    </router-link>
  </nav>
</template>

<script setup>
  import { LogInOutline } from '@vicons/ionicons5'
  import { useNavItems } from '@/composables/useNavItems'
  import { useAuthStore } from '@/stores/authStore'

  const authStore = useAuthStore()
  const { bottomItems } = useNavItems()
</script>

<style scoped>
  .bottom-nav {
    position: fixed;
    inset: auto 0 0 0;
    height: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
    padding-bottom: env(safe-area-inset-bottom);
    display: flex;
    align-items: stretch;
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(12px);
    border-top: 1px solid var(--color-border);
    box-shadow: 0 -6px 20px rgba(11, 31, 77, 0.06);
    z-index: 20;
  }
  .tab {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    color: var(--gray-500);
    font-size: 11px;
    font-weight: 600;
    transition: color var(--duration-fast);
  }
  .tab.active {
    color: var(--color-primary);
  }
  .tab.active .icon-wrap {
    transform: translateY(-2px) scale(1.08);
  }
  .icon-wrap {
    display: flex;
    transition: transform var(--duration-base) var(--ease-spring);
  }
  .tab.primary .icon-wrap {
    width: 52px;
    height: 52px;
    margin-top: -22px;
    border-radius: 50%;
    align-items: center;
    justify-content: center;
    color: #fff;
    background: linear-gradient(135deg, var(--red-500), var(--red-600));
    box-shadow: 0 8px 18px rgba(214, 35, 42, 0.35);
  }
  .tab.primary.active {
    color: var(--red-600);
  }
</style>
