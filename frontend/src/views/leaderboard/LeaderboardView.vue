<template>
  <div class="leaderboard-page">
    <PageHeader
      eyebrow="TAMKANG SOFT TENNIS"
      title="淡江軟網排行榜"
      :subtitle="`依 TrueSkill 保守分數排名・至少 ${MIN_MATCHES} 場比賽才會上榜`"
    >
      <template #actions>
        <n-button v-if="authStore.isAuthenticated" secondary @click="router.push({ name: 'DetailLeaderboard' })">
          <template #icon><n-icon :component="StatsChartOutline" /></template>
          詳細數據
        </n-button>
      </template>
    </PageHeader>

    <div class="stats-row">
      <StatCard label="上榜球員" :value="players.length" :icon="PeopleOutline" />
      <StatCard
        label="累計比賽"
        :value="statistics?.total_matches ?? 0"
        :icon="TennisballOutline"
        accent="var(--red-500)"
      />
      <StatCard
        label="近 30 天比賽"
        :value="statistics?.matches_last_month ?? 0"
        :icon="CalendarOutline"
        accent="var(--gold-500)"
      />
    </div>

    <n-alert v-if="error" type="error" :title="error" class="error" />

    <template v-if="loading">
      <div class="podium-skeleton">
        <n-skeleton v-for="n in 3" :key="n" height="260px" :sharp="false" />
      </div>
      <n-skeleton v-for="n in 6" :key="n" height="60px" :sharp="false" class="row-skeleton" />
    </template>

    <n-empty v-else-if="!players.length" description="目前還沒有球員達到上榜門檻" size="huge" class="empty" />

    <template v-else>
      <LeaderboardPodium :players="players.slice(0, 3)" />

      <div class="list-toolbar">
        <n-radio-group v-model:value="sortBy" size="medium">
          <n-radio-button v-for="option in SORT_OPTIONS" :key="option.value" :value="option.value">
            {{ option.label }}
          </n-radio-button>
        </n-radio-group>
        <n-input v-model:value="keyword" placeholder="搜尋球員" clearable round class="search">
          <template #prefix><n-icon :component="SearchOutline" /></template>
        </n-input>
      </div>

      <RankingList :players="listedPlayers" :start-rank="1" :highlight-id="authStore.user?.member_id ?? null" />
    </template>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import {
    CalendarOutline,
    PeopleOutline,
    SearchOutline,
    StatsChartOutline,
    TennisballOutline
  } from '@vicons/ionicons5'
  import { leaderboardApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import StatCard from '@/components/base/StatCard.vue'
  import LeaderboardPodium from '@/components/leaderboard/LeaderboardPodium.vue'
  import RankingList from '@/components/leaderboard/RankingList.vue'
  import { useAuthStore } from '@/stores/authStore'
  import { organizationLabel } from '@/utils/player'

  const MIN_MATCHES = 5
  const SORT_OPTIONS = [
    { value: 'score', label: '排名分數', key: p => p.conservative_score },
    { value: 'win_rate', label: '勝率', key: p => p.win_rate },
    { value: 'matches', label: '場次', key: p => p.total_matches }
  ]

  const router = useRouter()
  const authStore = useAuthStore()

  const loading = ref(true)
  const error = ref(null)
  const players = ref([])
  const statistics = ref(null)
  const sortBy = ref('score')
  const keyword = ref('')

  /** 列表排序後依序顯示，排名欄位反映目前的排序方式。 */
  const listedPlayers = computed(() => {
    const key = SORT_OPTIONS.find(option => option.value === sortBy.value).key
    const sorted = [...players.value].sort((a, b) => key(b) - key(a))
    const term = keyword.value.trim().toLowerCase()
    return term ? sorted.filter(p => p.name.toLowerCase().includes(term)) : sorted
  })

  onMounted(async () => {
    try {
      const [{ items }, stats] = await Promise.all([
        leaderboardApi.list({ include_guests: false, min_matches: MIN_MATCHES, per_page: 500 }),
        leaderboardApi.statistics()
      ])
      players.value = items.map(player => ({ ...player, organization_name: organizationLabel(player) }))
      statistics.value = stats
    } catch (err) {
      error.value = err.response?.data?.message || '載入排行榜時發生錯誤'
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .stats-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 36px;
  }
  .error {
    margin-bottom: 16px;
  }
  .podium-skeleton {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 28px;
  }
  .row-skeleton {
    margin-bottom: 8px;
  }
  .empty {
    padding: 64px 0;
  }
  .list-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }
  .search {
    width: 220px;
  }

  @media (max-width: 640px) {
    .stats-row {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 24px;
    }
    .stats-row :deep(.stat-card) {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
      padding: 12px;
    }
    .stats-row :deep(.value) {
      font-size: 24px;
    }
    .search {
      width: 100%;
    }
  }
</style>
