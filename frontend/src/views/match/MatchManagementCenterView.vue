<template>
  <div class="matches-page">
    <PageHeader eyebrow="Record" title="記錄" />

    <nav v-if="canRecord" class="actions-grid" aria-label="記錄方式">
      <router-link
        v-for="(action, index) in RECORD_ACTIONS"
        :key="action.name"
        :to="{ name: action.name }"
        class="action hud-frame"
        :class="{ primary: index === 0 }"
      >
        <span class="corner tl"></span>
        <span class="corner br"></span>
        <span class="hud-label">{{ action.code }}</span>
        <span class="action-title">
          <n-icon :component="action.icon" size="20" />
          {{ action.title }}
          <span v-if="action.beta" class="beta">Beta</span>
        </span>
      </router-link>
    </nav>

    <div class="section-head">
      <span class="hud-label">{{ total }} 場紀錄</span>
      <span class="rule"></span>
    </div>

    <MatchFilters
      v-model:filters="filters"
      :player-options="playerOptions"
      :players-loading="playersLoading"
      class="filters"
      @reset="filters = emptyFilters()"
      @player-search="searchPlayers"
    />

    <n-alert v-if="error" type="error" :title="error" class="block" />

    <div v-if="loading" class="list">
      <n-skeleton v-for="n in 5" :key="n" height="112px" :sharp="false" />
    </div>
    <n-empty v-else-if="!records.length" description="沒有符合條件的比賽" size="huge" class="empty">
      <template #extra>
        <n-button v-if="canRecord" type="primary" @click="router.push({ name: 'RecordMatch' })"
          >記錄第一場比賽</n-button
        >
      </template>
    </n-empty>
    <TransitionGroup v-else name="list" tag="div" class="list">
      <MatchCard
        v-for="(record, index) in records"
        :key="record.id"
        :record="record"
        :can-edit="canRecord"
        :can-delete="canDeleteMatch"
        :highlight-ids="filters.player_ids"
        class="stagger-in"
        :style="{ '--i': index }"
        @view="row => router.push({ name: 'ViewMatch', params: { id: row.id } })"
        @edit="row => router.push({ name: 'EditMatch', params: { id: row.id } })"
        @delete="confirmDelete"
      />
    </TransitionGroup>

    <div v-if="total > pageSize" class="pagination">
      <n-pagination
        :page="page"
        :page-size="pageSize"
        :item-count="total"
        :page-sizes="[10, 15, 30, 50]"
        show-size-picker
        @update:page="changePage"
        @update:page-size="changePageSize"
      />
    </div>
  </div>
</template>

<script setup>
  import { onMounted, onUnmounted, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog, useMessage } from 'naive-ui'
  import { Add, Layers, Timer, Trophy } from '@vicons/carbon'
  import { matchesApi, membersApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import MatchCard from '@/components/match/MatchCard.vue'
  import MatchFilters from '@/components/match/MatchFilters.vue'
  import { usePermissions } from '@/composables/usePermissions'
  import { formatDate } from '@/utils/format'

  const SEARCH_DEBOUNCE_DELAY = 400
  const RECORD_ACTIONS = [
    {
      name: 'RecordMatch',
      code: 'A // Single',
      title: '記錄一場',
      icon: Add
    },
    {
      name: 'BatchRecordMatch',
      code: 'B // Batch',
      title: '批次補登',
      icon: Layers
    },
    {
      name: 'Events',
      code: 'C // Events',
      title: '賽事',
      icon: Trophy
    },
    {
      name: 'RefereeMode',
      code: 'D // Referee',
      title: '裁判模式',
      icon: Timer,
      beta: true
    }
  ]
  const emptyFilters = () => ({
    player_ids: [],
    category: null,
    match_type: null,
    match_format: null,
    result: null,
    date_range: null
  })

  const router = useRouter()
  const dialog = useDialog()
  const message = useMessage()
  const { hasManagementAccess: canRecord, canDeleteMatch } = usePermissions()

  const loading = ref(true)
  const error = ref(null)
  const records = ref([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(15)
  const filters = ref(emptyFilters())
  const playerOptions = ref([])
  const playersLoading = ref(false)

  const queryParams = () => {
    const f = filters.value
    const params = { page: page.value, per_page: pageSize.value, sort_by: 'match_date', sort_order: 'desc' }
    if (f.player_ids.length) params.player_ids = f.player_ids.join(',')
    if (f.result && f.player_ids.length) params.result = f.result
    if (f.category) params.category = f.category
    if (f.match_type) params.match_type = f.match_type
    if (f.match_format) params.match_format = f.match_format
    if (f.date_range?.length === 2) {
      params.start_date = formatDate(f.date_range[0])
      params.end_date = formatDate(f.date_range[1])
    }
    return params
  }

  const fetchRecords = async () => {
    loading.value = true
    error.value = null
    try {
      const { items, meta } = await matchesApi.list(queryParams())
      records.value = items
      total.value = meta.total ?? items.length
    } catch (err) {
      error.value = err.response?.data?.message || '無法載入比賽記錄'
    } finally {
      loading.value = false
    }
  }

  const changePage = value => {
    page.value = value
    fetchRecords()
  }
  const changePageSize = value => {
    pageSize.value = value
    page.value = 1
    fetchRecords()
  }

  let searchTimer = null
  watch(filters, () => {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      page.value = 1
      fetchRecords()
    }, SEARCH_DEBOUNCE_DELAY)
  })

  const toOption = member => ({ label: member.name, value: member.id })

  const loadPlayers = async () => {
    const members = await membersApi.list({
      include_guests: true,
      include_inactive: true,
      sort_by: 'name',
      sort_order: 'asc'
    })
    playerOptions.value = members.map(toOption)
  }

  const searchPlayers = async query => {
    if (!query || query.length < 2) return
    playersLoading.value = true
    try {
      const members = await membersApi.list({ q: query, limit: 20, include_guests: true, include_inactive: true })
      const known = new Set(playerOptions.value.map(p => p.value))
      playerOptions.value = [...playerOptions.value, ...members.filter(m => !known.has(m.id)).map(toOption)]
    } finally {
      playersLoading.value = false
    }
  }

  const confirmDelete = record => {
    dialog.error({
      title: '刪除比賽紀錄',
      content: `確定要刪除 ${record.match_date} 這場比賽嗎？球員的分數會重新計算，且無法復原。`,
      positiveText: '刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await matchesApi.remove(record.id)
          message.success('比賽紀錄已刪除')
          await fetchRecords()
        } catch (err) {
          message.error(err.response?.data?.message || '刪除失敗')
        }
      }
    })
  }

  onMounted(() => {
    fetchRecords()
    loadPlayers().catch(() => message.error('載入球員列表失敗'))
  })
  onUnmounted(() => clearTimeout(searchTimer))
</script>

<style scoped>
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 28px;
  }
  .action {
    --corner-color: var(--ink);
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 16px 18px;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--ink);
    transition:
      border-color var(--duration-fast),
      background var(--duration-fast);
  }
  .action .corner {
    opacity: 0;
  }
  .action:hover {
    border-color: var(--ink);
  }
  .action:hover .corner {
    opacity: 1;
  }
  .action:hover .corner.tl {
    transform: translate(-3px, -3px);
  }
  .action:hover .corner.br {
    transform: translate(3px, 3px);
  }
  /* 最常用的「記錄一場」反白，視線先看到它 */
  .action.primary {
    --corner-color: var(--accent);
    border-color: var(--ink);
    background: var(--ink);
    color: var(--bg);
  }
  .action.primary .hud-label {
    color: var(--accent);
  }
  .action-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }
  .beta {
    padding: 0 6px;
    border: 1px solid var(--accent-soft);
    color: var(--accent-text);
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 500;
  }
  .section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }
  .rule {
    flex: 1;
    height: 1px;
    background: var(--line);
  }
  /* 窄螢幕：入口排成一列，只留圖示和名稱 */
  @media (max-width: 900px) {
    .actions-grid {
      gap: 8px;
      margin-bottom: 20px;
    }
    .action {
      align-items: center;
      padding: 12px 6px;
    }
    .action .hud-label,
    .beta {
      display: none;
    }
    .action-title {
      flex-direction: column;
      gap: 6px;
      font-size: 16px;
    }
  }

  .filters,
  .block {
    margin-bottom: 18px;
  }
  .list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .empty {
    padding: 64px 0;
  }
  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }
</style>
