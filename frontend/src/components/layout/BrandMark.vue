<template>
  <router-link :to="{ name: 'Leaderboard' }" class="brand" :class="{ compact }">
    <span class="mark" aria-hidden="true">
      <span class="corner tl"></span>
      <span class="corner br"></span>
      <span class="dot"></span>
    </span>
    <span class="title">TKU 軟網</span>
  </router-link>
</template>

<script setup>
  /** 品牌標誌：一顆在準星框裡的球。 */
  defineProps({ compact: { type: Boolean, default: false } })
</script>

<style scoped>
  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .mark {
    position: relative;
    display: grid;
    place-items: center;
    width: 34px;
    height: 34px;
    border: 1px solid var(--line);
  }
  .corner {
    position: absolute;
    width: 9px;
    height: 9px;
    border: 0 solid var(--accent);
  }
  .corner.tl {
    top: -1px;
    left: -1px;
    border-top-width: 2px;
    border-left-width: 2px;
  }
  .corner.br {
    right: -1px;
    bottom: -1px;
    border-right-width: 2px;
    border-bottom-width: 2px;
  }
  .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--accent);
    animation: pulse 2.4s var(--ease-out) infinite;
  }
  @keyframes pulse {
    50% {
      transform: scale(0.75);
      opacity: 0.7;
    }
  }
  .title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--ink);
  }
  .compact .mark {
    width: 28px;
    height: 28px;
  }
  .compact .dot {
    width: 10px;
    height: 10px;
  }
</style>
