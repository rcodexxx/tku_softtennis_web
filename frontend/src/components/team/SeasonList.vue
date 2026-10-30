<template>
  <div class="seasons">
    <div class="toolbar">
      <p class="intro">每個賽季重新計分；比賽依日期自動歸到所屬的賽季。</p>
      <n-button v-if="canStartSeason" type="primary" @click="router.push({ name: 'NewSeason' })">
        <template #icon><n-icon :component="FlagOutline" /></template>
        開新賽季
      </n-button>
    </div>

    <div v-if="loading" class="timeline">
      <n-skeleton v-for="n in 2" :key="n" height="96px" :sharp="false" />
    </div>
    <n-empty v-else-if="!seasons.length" description="還沒有賽季，所有比賽算在同一個排行榜" class="empty" />
    <ol v-else class="timeline">
      <li
        v-for="(season, index) in seasons"
        :key="season.id"
        class="season stagger-in"
        :class="{ current: season.is_current }"
        :style="{ '--i': index }"
      >
        <span class="dot" aria-hidden="true"></span>
        <div class="card">
          <div class="head">
            <h3>{{ season.name }}</h3>
            <span class="chip">{{ season.is_current ? '進行中' : '已封存' }}</span>
          </div>
          <p class="range num">{{ seasonRangeLabel(season) }}・{{ season.match_count }} 場比賽</p>
          <n-button text type="primary" @click="openBoard(season)">
            看排行榜
            <template #icon><n-icon :component="ArrowForwardOutline" /></template>
          </n-button>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup>
  import { onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { ArrowForwardOutline, FlagOutline } from '@vicons/ionicons5'
  import { usePermissions } from '@/composables/usePermissions'
  import { useSeasons } from '@/composables/useSeasons'
  import { seasonRangeLabel } from '@/utils/season'

  const router = useRouter()
  const { canStartSeason } = usePermissions()
  const { seasons, load } = useSeasons()
  const loading = ref(true)

  const openBoard = season =>
    router.push({ name: 'Leaderboard', query: season.is_current ? {} : { season: season.id } })

  onMounted(async () => {
    await load()
    loading.value = false
  })
</script>

<style scoped>
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 20px;
  }
  .intro {
    margin: 0;
    color: var(--color-text-muted);
  }
  .timeline {
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .season {
    position: relative;
    padding-left: 28px;
  }
  /* 時間軸的線與圓點 */
  .season::before {
    content: '';
    position: absolute;
    top: 22px;
    bottom: -14px;
    left: 7px;
    width: 2px;
    background: var(--color-border);
  }
  .season:last-child::before {
    display: none;
  }
  .dot {
    position: absolute;
    top: 16px;
    left: 0;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 3px solid var(--gray-400);
    background: var(--color-surface);
  }
  .current .dot {
    border-color: var(--red-500);
    box-shadow: 0 0 0 4px rgba(229, 56, 63, 0.18);
  }
  .card {
    padding: 14px 18px;
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    box-shadow: var(--shadow-sm);
  }
  .current .card {
    border-color: var(--blue-200);
    background: linear-gradient(135deg, var(--blue-50), var(--color-surface));
  }
  .head {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .head h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 800;
    color: var(--blue-900);
  }
  .chip {
    padding: 2px 10px;
    border-radius: var(--radius-full);
    background: var(--gray-100);
    color: var(--gray-700);
    font-size: 12px;
    font-weight: 700;
  }
  .current .chip {
    background: var(--red-500);
    color: #fff;
  }
  .range {
    margin: 4px 0 6px;
    font-size: 13px;
    color: var(--color-text-muted);
  }
  .empty {
    padding: 48px 0;
  }
</style>
