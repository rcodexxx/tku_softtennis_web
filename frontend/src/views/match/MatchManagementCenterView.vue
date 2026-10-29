<template>
  <div class="matches-page">
    <PageHeader eyebrow="MATCHES" title="比賽管理" :subtitle="`共 ${total} 場比賽紀錄`">
      <template #actions>
        <n-button v-if="canRecord" type="primary" @click="router.push({ name: 'RecordMatch' })">
          <template #icon><n-icon :component="AddOutline" /></template>
          記錄新比賽
        </n-button>
      </template>
    </PageHeader>

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
  import { AddOutline } from '@vicons/ionicons5'
  import { matchesApi, membersApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import MatchCard from '@/components/match/MatchCard.vue'
  import MatchFilters from '@/components/match/MatchFilters.vue'
  import { usePermissions } from '@/composables/usePermissions'
  import { formatDate } from '@/utils/format'

  const SEARCH_DEBOUNCE_DELAY = 400
  const emptyFilters = () => ({ player_ids: [], match_type: null, match_format: null, result: null, date_range: null })

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
