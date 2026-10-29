<template>
  <header class="topbar">
    <router-link :to="{ name: 'Leaderboard' }" class="brand">
      <span class="brand-ball" aria-hidden="true"></span>
      <span class="brand-title">TKU 軟網</span>
    </router-link>
    <UserMenu compact />
  </header>
</template>

<script setup>
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
    padding: 10px 16px;
    background: linear-gradient(90deg, var(--blue-900), var(--blue-700));
    color: #fff;
    box-shadow: var(--shadow-md);
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .brand-ball {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #fff 0 18%, var(--gold-300) 19% 100%);
  }
  .brand-title {
    font-weight: 800;
    font-size: 17px;
    letter-spacing: 0.04em;
  }
</style>
