<template>
  <div class="leaderboard-page">
    <PageHeader
      eyebrow="TAMKANG SOFT TENNIS"
      title="淡江軟網排行榜"
      :subtitle="`依最近 20 場的局數表現計分・至少 ${MIN_MATCHES} 場比賽才會上榜`"
    >
      <template #actions>
        <n-button v-if="authStore.isAuthenticated" secondary @click="router.push({ name: 'DetailLeaderboard' })">
          <template #icon><n-icon :component="StatsChartOutline" /></template>
          詳細數據
        </n-button>
      </template>
    </PageHeader>

    <div class="board-switch">
      <div class="tabs" role="tablist" aria-label="排行榜範圍">
        <span class="tab-indicator" :style="{ transform: `translateX(${scopeIndex * 100}%)` }"></span>
        <button
          v-for="option in SCOPES"
          :key="option.value"
          type="button"
          role="tab"
          class="tab"
          :class="{ active: scope === option.value }"
          :aria-selected="scope === option.value"
          @click="setBoard({ scope: option.value })"
        >
          {{ option.label }}
        </button>
      </div>
      <div class="genders" role="group" aria-label="性別">
        <button
          v-for="option in GENDERS"
          :key="option.label"
          type="button"
          class="gender"
          :class="{ active: gender === option.value }"
          :aria-pressed="gender === option.value"
          @click="setBoard({ gender: option.value })"
        >
          {{ option.label }}
        </button>
      </div>
      <span class="board-hint">{{ SCOPES[scopeIndex].hint }}</span>
    </div>

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

    <div v-else :key="boardKey" class="board">
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
    </div>

    <RatingGuide class="guide" />
  </div>
</template>

<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
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
  import RatingGuide from '@/components/leaderboard/RatingGuide.vue'
  import { useAuthStore } from '@/stores/authStore'
  import { organizationLabel } from '@/utils/player'

  const MIN_MATCHES = 5
  const SCOPES = [
    { value: 'team', label: '校隊', hint: '淡江大學軟網隊' },
    { value: 'combined', label: '綜合', hint: '校隊＋校友會' }
  ]
  const GENDERS = [
    { value: null, label: '全部' },
    { value: 'male', label: '男生' },
    { value: 'female', label: '女生' }
  ]
  const SORT_OPTIONS = [
    { value: 'score', label: '分數', key: p => p.rating },
    { value: 'win_rate', label: '勝率', key: p => p.win_rate },
    { value: 'matches', label: '場次', key: p => p.total_matches }
  ]

  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()

  const loading = ref(true)
  const error = ref(null)
  const players = ref([])
  const statistics = ref(null)
  const sortBy = ref('score')
  const keyword = ref('')

  // 目前的排行榜存在網址上，方便分享
  const scope = computed(() => (SCOPES.some(s => s.value === route.query.scope) ? route.query.scope : 'team'))
  const gender = computed(() => (['male', 'female'].includes(route.query.gender) ? route.query.gender : null))
  const scopeIndex = computed(() => SCOPES.findIndex(option => option.value === scope.value))
  const boardKey = computed(() => `${scope.value}-${gender.value}`)

  const setBoard = changes => {
    const next = { scope: scope.value, gender: gender.value, ...changes }
    router.replace({ query: { ...route.query, scope: next.scope, gender: next.gender || undefined } })
  }

  /** 列表排序後依序顯示，排名欄位反映目前的排序方式。 */
  const listedPlayers = computed(() => {
    const key = SORT_OPTIONS.find(option => option.value === sortBy.value).key
    const sorted = [...players.value].sort((a, b) => key(b) - key(a))
    const term = keyword.value.trim().toLowerCase()
    return term ? sorted.filter(p => p.name.toLowerCase().includes(term)) : sorted
  })

  const loadPlayers = async () => {
    loading.value = true
    error.value = null
    try {
      const { items } = await leaderboardApi.list({
        scope: scope.value,
        gender: gender.value || undefined,
        min_matches: MIN_MATCHES,
        per_page: 500
      })
      players.value = items.map(player => ({ ...player, organization_name: organizationLabel(player) }))
    } catch (err) {
      error.value = err.response?.data?.message || '載入排行榜時發生錯誤'
    } finally {
      loading.value = false
    }
  }

  watch(boardKey, loadPlayers)

  onMounted(async () => {
    loadPlayers()
    try {
      statistics.value = await leaderboardApi.statistics()
    } catch {
      // 統計數字只是輔助資訊，載入失敗時顯示 0
    }
  })
</script>

<style scoped>
  .board-switch {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px 16px;
    margin-bottom: 20px;
  }
  .tabs {
    position: relative;
    display: grid;
    grid-template-columns: repeat(2, 96px);
    padding: 4px;
    border-radius: var(--radius-full);
    background: var(--blue-900);
    box-shadow: var(--shadow-md);
  }
  .tab-indicator {
    position: absolute;
    top: 4px;
    left: 4px;
    width: 96px;
    height: calc(100% - 8px);
    border-radius: var(--radius-full);
    background: linear-gradient(135deg, var(--red-500), var(--red-600));
    box-shadow: 0 4px 12px rgba(229, 56, 63, 0.4);
    transition: transform var(--duration-base) var(--ease-spring);
  }
  .tab {
    position: relative;
    padding: 8px 0;
    border: 0;
    background: transparent;
    color: rgba(255, 255, 255, 0.7);
    font: inherit;
    font-size: 15px;
    font-weight: 800;
    cursor: pointer;
    transition: color var(--duration-fast) var(--ease-out);
  }
  .tab.active {
    color: #fff;
  }
  .genders {
    display: flex;
    gap: 6px;
  }
  .gender {
    padding: 6px 14px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-full);
    background: var(--color-surface);
    color: var(--gray-700);
    font: inherit;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition:
      background var(--duration-fast) var(--ease-out),
      color var(--duration-fast) var(--ease-out),
      transform var(--duration-fast) var(--ease-spring);
  }
  .gender:hover {
    transform: translateY(-1px);
  }
  .gender.active {
    border-color: var(--blue-700);
    background: var(--blue-700);
    color: #fff;
  }
  .board-hint {
    font-size: 13px;
    color: var(--color-text-muted);
  }
  .board {
    animation: board-in var(--duration-slow) var(--ease-out);
  }
  @keyframes board-in {
    from {
      opacity: 0;
      transform: translateY(12px);
    }
  }
  .guide {
    margin-top: 28px;
  }
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
