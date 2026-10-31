<template>
  <div class="leaderboard-page">
    <header class="board-head">
      <div class="titles">
        <p class="hud-label eyebrow">TKU // Ranking · {{ selectedSeason?.name ?? '全部比賽' }}</p>
        <h1 class="title">排行榜</h1>
      </div>
      <div class="head-actions">
        <n-select
          v-if="seasons.length > 1"
          :value="selectedSeason?.id ?? null"
          :options="seasonSelectOptions"
          size="small"
          class="season-select"
          aria-label="賽季"
          @update:value="id => setBoard({ season: id === currentSeason?.id ? null : id })"
        />
        <n-button v-if="authStore.isAuthenticated" size="small" @click="router.push({ name: 'DetailLeaderboard' })">
          <template #icon><n-icon :component="Analytics" /></template>
          詳細數據
        </n-button>
      </div>
    </header>

    <div class="controls">
      <div class="scopes" role="tablist" aria-label="排行榜範圍">
        <button
          v-for="option in scopeTabs"
          :key="option.value"
          type="button"
          role="tab"
          class="scope"
          :class="{ active: scope === option.value }"
          :aria-selected="scope === option.value"
          @click="setBoard({ scope: option.value })"
        >
          <span class="scope-label">{{ option.label }}</span>
          <span v-if="option.custom" class="custom-mark" aria-hidden="true">◆</span>
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
    </div>

    <div v-if="viewingPast" class="past-banner">
      <n-icon :component="Archive" size="18" />
      <span
        ><b>{{ selectedSeason.name }}</b> · 已封存</span
      >
      <n-button size="small" @click="setBoard({ season: null })">回到 {{ currentSeason.name }}</n-button>
    </div>

    <n-alert v-if="error" type="error" :title="error" class="block" />

    <template v-if="loading">
      <div class="skeleton-top">
        <n-skeleton height="300px" />
        <div class="skeleton-runners">
          <n-skeleton height="143px" />
          <n-skeleton height="143px" />
        </div>
      </div>
      <n-skeleton v-for="n in 5" :key="n" height="52px" class="row-skeleton" />
    </template>

    <n-empty v-else-if="!players.length" description="這個範圍還沒有球員" size="large" class="empty" />

    <div v-else :key="boardKey" class="board">
      <TopThree
        v-if="board.ranked.length"
        :players="board.ranked.slice(0, 3)"
        :highlight-id="myId"
        @select="openPlayer"
      />
      <div v-else class="awaiting hud-frame">
        <span class="corner tl"></span>
        <span class="corner br"></span>
        <span class="hud-label">Rank // Pending</span>
        <p class="awaiting-title">本季還沒有比賽</p>
        <n-button v-if="previousSeason && !viewingPast" size="small" @click="setBoard({ season: previousSeason.id })">
          看 {{ previousSeason.name }}
        </n-button>
      </div>

      <section v-if="restRanked.length || keyword" class="section">
        <div class="section-head">
          <span class="hud-label">{{ keyword ? '搜尋結果' : '名單' }}</span>
          <span class="rule"></span>
          <n-input v-model:value="keyword" placeholder="搜尋球員" clearable size="small" class="search">
            <template #prefix><n-icon :component="Search" /></template>
          </n-input>
        </div>
        <RankingList v-if="restRanked.length" :players="restRanked" :highlight-id="myId" @select="openPlayer" />
        <p v-else class="no-match">沒有符合的球員</p>
      </section>
    </div>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { Analytics, Archive, Search } from '@vicons/carbon'
  import { boardsApi, leaderboardApi } from '@/api'
  import RankingList from '@/components/leaderboard/RankingList.vue'
  import TopThree from '@/components/leaderboard/TopThree.vue'
  import { usePermissions } from '@/composables/usePermissions'
  import { useSeasons } from '@/composables/useSeasons'
  import { useAuthStore } from '@/stores/authStore'
  import { organizationLabel } from '@/utils/player'
  import { rankPlayers } from '@/utils/rating'

  const SCOPES = [
    { value: 'team', label: '校隊' },
    { value: 'combined', label: '綜合' }
  ]
  const GENDERS = [
    { value: null, label: '全部' },
    { value: 'male', label: '男' },
    { value: 'female', label: '女' }
  ]

  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()
  const { hasManagementAccess } = usePermissions()
  const {
    seasons,
    current: currentSeason,
    options: seasonSelectOptions,
    byId: seasonById,
    load: loadSeasons
  } = useSeasons()

  const loading = ref(true)
  const error = ref(null)
  const players = ref([])
  const keyword = ref('')
  const openPlayer = player => router.push({ name: 'Player', params: { id: player.id } })
  const myId = computed(() => authStore.user?.member_id ?? null)

  // 目前的排行榜存在網址上，方便分享
  // 自訂榜單（例如「打球嗎」）目前只給幹部看，分頁值為 board:<id>
  const boards = ref([])
  const scopeTabs = computed(() => [
    ...SCOPES,
    ...boards.value.map(board => ({ value: `board:${board.id}`, label: board.name, custom: true }))
  ])
  const scope = computed(() => {
    const requested = route.query.scope
    if (SCOPES.some(s => s.value === requested)) return requested
    return /^board:\d+$/.test(requested ?? '') && hasManagementAccess.value ? requested : 'team'
  })
  const boardId = computed(() => (scope.value.startsWith('board:') ? Number(scope.value.slice(6)) : null))
  const gender = computed(() => (['male', 'female'].includes(route.query.gender) ? route.query.gender : null))
  // 沒指定賽季時看目前賽季
  const seasonId = computed(() => Number(route.query.season) || null)
  const boardKey = computed(() => `${seasonId.value}-${scope.value}-${gender.value}`)

  const selectedSeason = computed(() => (seasonId.value && seasonById(seasonId.value)) || currentSeason.value)
  const viewingPast = computed(() => Boolean(selectedSeason.value && !selectedSeason.value.is_current))
  // 新賽季剛開始還沒人上榜時，提供上個賽季的連結
  const previousSeason = computed(() => seasons.value.find(season => !season.is_current) ?? null)

  const setBoard = changes => {
    const next = { season: seasonId.value, scope: scope.value, gender: gender.value, ...changes }
    router.replace({
      query: {
        ...route.query,
        season: next.season || undefined,
        scope: next.scope,
        gender: next.gender || undefined
      }
    })
  }

  // 打滿上榜場數的人才有名次（依分數）；其他人（包含還沒比賽的）列在後面
  const board = computed(() => rankPlayers(players.value))

  const matches = player => player.name.toLowerCase().includes(keyword.value.trim().toLowerCase())
  // 前三名在上面另外顯示；其他人依名次排下來，還沒比賽的在最後。搜尋時列出所有符合的人
  const restRanked = computed(() =>
    keyword.value.trim()
      ? [...board.value.ranked, ...board.value.unranked].filter(matches)
      : [...board.value.ranked.slice(3), ...board.value.unranked]
  )

  const loadPlayers = async () => {
    loading.value = true
    error.value = null
    try {
      const { items } = await leaderboardApi.list({
        season_id: seasonId.value || undefined,
        ...(boardId.value ? { board_id: boardId.value } : { scope: scope.value }),
        gender: gender.value || undefined,
        min_matches: 0,
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

  const loadBoards = async () => {
    if (!hasManagementAccess.value) return
    try {
      boards.value = await boardsApi.list()
    } catch {
      boards.value = []
    }
  }

  onMounted(() => {
    loadPlayers()
    loadSeasons()
    loadBoards()
  })
</script>

<style scoped>
  .board-head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    padding-bottom: 16px;
    margin-bottom: 18px;
    border-bottom: 1px solid var(--line);
  }
  .eyebrow {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 8px;
  }
  .eyebrow::before {
    content: '';
    width: 6px;
    height: 6px;
    background: var(--accent);
  }
  .title {
    margin: 0;
    font-size: clamp(28px, 4vw, 40px);
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--ink);
  }
  .head-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .season-select {
    width: 170px;
  }

  .controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 20px;
  }
  .scopes {
    display: flex;
    gap: 24px;
  }
  .scope {
    position: relative;
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 4px 0 8px;
    border: 0;
    background: none;
    color: var(--ink-3);
    font: inherit;
    cursor: pointer;
  }
  .scope-label {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.06em;
  }
  .scope::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 2px;
    background: var(--accent);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform var(--duration-base) var(--ease-out);
  }
  .scope.active {
    color: var(--ink);
  }
  .custom-mark {
    font-size: 11px;
    color: var(--accent);
  }
  .scope.active::after {
    transform: scaleX(1);
  }
  .genders {
    display: flex;
    border: 1px solid var(--line);
  }
  .gender {
    min-width: 52px;
    padding: 6px 12px;
    border: 0;
    border-left: 1px solid var(--line);
    background: transparent;
    color: var(--ink-3);
    font: inherit;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition:
      background var(--duration-fast),
      color var(--duration-fast);
  }
  .gender:first-child {
    border-left: 0;
  }
  .gender:hover {
    color: var(--ink);
  }
  .gender.active {
    background: var(--ink);
    color: var(--bg);
  }

  .past-banner {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 18px;
    padding: 10px 14px;
    border: 1px solid var(--accent-soft);
    border-left: 3px solid var(--accent);
    background: var(--accent-tint);
    color: var(--ink);
    font-size: 16px;
  }
  .past-banner span {
    flex: 1;
    min-width: 200px;
  }
  .block {
    margin-bottom: 16px;
  }

  .board {
    animation: board-in var(--duration-slow) var(--ease-out);
  }
  @keyframes board-in {
    from {
      opacity: 0;
    }
  }
  .awaiting {
    --corner-color: var(--accent);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    padding: 28px 24px;
    border: 1px dashed var(--line);
    background: var(--surface);
  }
  .awaiting-title {
    margin: 6px 0 8px;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--ink);
  }
  .section {
    margin-top: 26px;
  }
  .section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }
  .rule {
    flex: 1;
    height: 1px;
    background: var(--line);
  }
  .search {
    width: 200px;
  }
  .no-match {
    padding: 20px;
    color: var(--ink-3);
    text-align: center;
  }
  .empty {
    padding: 64px 0;
  }
  .skeleton-top {
    display: grid;
    grid-template-columns: 1.55fr 1fr;
    gap: 14px;
    margin-bottom: 26px;
  }
  .skeleton-runners {
    display: grid;
    gap: 14px;
  }
  .row-skeleton {
    margin-bottom: 6px;
  }

  @media (max-width: 640px) {
    .head-actions {
      width: 100%;
    }
    .season-select {
      flex: 1;
    }
    .controls {
      flex-direction: column;
      align-items: stretch;
    }
    .genders {
      align-self: flex-start;
    }
    .search {
      width: 140px;
    }
    .skeleton-top {
      grid-template-columns: 1fr;
    }
  }
</style>
