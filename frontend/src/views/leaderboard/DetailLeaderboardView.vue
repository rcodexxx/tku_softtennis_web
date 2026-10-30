<template>
  <div class="detail-page">
    <PageHeader eyebrow="STATISTICS" title="詳細數據" subtitle="所有球員的分數、戰績與近況，點選球員可看完整分析。">
      <template #actions>
        <n-button secondary :disabled="!filteredPlayers.length" @click="exportCsv">
          <template #icon><n-icon :component="Download" /></template>
          匯出 CSV
        </n-button>
        <n-button secondary :loading="loading" @click="load">
          <template #icon><n-icon :component="Renew" /></template>
          重新整理
        </n-button>
      </template>
    </PageHeader>

    <div class="insights">
      <StatCard label="符合條件的球員" :value="filteredPlayers.length" :icon="UserMultiple" />
      <StatCard
        label="平均勝率"
        :value="averageWinRate"
        :decimals="1"
        suffix="%"
        :icon="ChartPie"
        accent="var(--green-600)"
      />
      <StatCard label="最高分數" :value="topRating" :decimals="1" :icon="Flash" accent="var(--gold-500)" />
      <div class="distribution">
        <span class="distribution-title">分數分布</span>
        <div class="distribution-bar">
          <span
            v-for="level in distribution"
            :key="level.label"
            class="segment"
            :style="{ flex: level.count || 0.0001, background: level.color }"
            :title="`${level.label} ${level.count} 人`"
          ></span>
        </div>
        <div class="distribution-legend">
          <span v-for="level in distribution" :key="level.label">
            {{ level.label }} <b class="num">{{ level.count }}</b>
          </span>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <n-input v-model:value="keyword" placeholder="搜尋球員或組織" clearable round class="search">
        <template #prefix><n-icon :component="Search" /></template>
      </n-input>
      <div class="filters">
        <n-select
          v-if="seasons.length"
          v-model:value="seasonId"
          :options="seasonSelectOptions"
          size="small"
          class="filter-select"
          @update:value="load"
        />
        <n-select
          v-model:value="scope"
          :options="SCOPE_OPTIONS"
          size="small"
          class="filter-select"
          @update:value="load"
        />
        <n-select
          v-model:value="gender"
          :options="GENDER_OPTIONS"
          size="small"
          class="filter-select"
          @update:value="load"
        />
        <label class="filter">
          <n-switch v-model:value="includeGuests" @update:value="load" />
          包含訪客
        </label>
        <label class="filter">
          最少場次
          <n-input-number
            v-model:value="minMatches"
            :min="0"
            :max="50"
            size="small"
            class="min-matches"
            @update:value="load"
          />
        </label>
      </div>
    </div>

    <n-alert v-if="error" type="error" :title="error" class="block" />

    <n-data-table
      class="detail-table"
      :columns="columns"
      :data="filteredPlayers"
      :loading="loading"
      :row-key="row => row.id"
      :row-props="row => ({ class: 'clickable-row', onClick: () => (selected = row) })"
      :pagination="{ pageSize: 20 }"
      :scroll-x="900"
      :bordered="false"
    />

    <RatingGuide class="guide" />

    <!-- 比較用的是目前賽季的分數，看舊賽季時不提供 -->
    <PlayerDetailModal
      :player="selected"
      :my-member-id="viewingPast ? null : (authStore.user?.member_id ?? null)"
      @close="selected = null"
    />
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { ChartPie, Download, Flash, Renew, Search, UserMultiple } from '@vicons/carbon'
  import { leaderboardApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import StatCard from '@/components/base/StatCard.vue'
  import { detailColumns } from '@/components/leaderboard/detailColumns'
  import PlayerDetailModal from '@/components/leaderboard/PlayerDetailModal.vue'
  import RatingGuide from '@/components/leaderboard/RatingGuide.vue'
  import { useSeasons } from '@/composables/useSeasons'
  import { useAuthStore } from '@/stores/authStore'
  import { organizationLabel } from '@/utils/player'
  import { formatRating } from '@/utils/rating'

  const SCOPE_OPTIONS = [
    { label: '所有球員', value: 'all' },
    { label: '校隊', value: 'team' },
    { label: '綜合（校隊＋校友會）', value: 'combined' }
  ]
  const GENDER_OPTIONS = [
    { label: '男女皆可', value: null },
    { label: '男生', value: 'male' },
    { label: '女生', value: 'female' }
  ]
  const RATING_BANDS = [
    { label: '4 以下', max: 4, color: 'var(--line)' },
    { label: '4–5', max: 5, color: 'var(--ink-4)' },
    { label: '5–6', max: 6, color: 'var(--ink-3)' },
    { label: '6–7', max: 7, color: 'var(--ink)' },
    { label: '7 以上', max: Infinity, color: 'var(--accent)' }
  ]

  const authStore = useAuthStore()
  const { seasons, options: seasonSelectOptions, byId: seasonById, load: loadSeasons } = useSeasons()

  const loading = ref(true)
  const error = ref(null)
  const players = ref([])
  // null 為目前賽季
  const seasonId = ref(null)
  const includeGuests = ref(false)
  const scope = ref('all')
  const gender = ref(null)
  const minMatches = ref(1)
  const keyword = ref('')
  const selected = ref(null)
  const columns = detailColumns()

  const selectedSeason = computed(() => seasonById(seasonId.value))
  const viewingPast = computed(() => Boolean(selectedSeason.value && !selectedSeason.value.is_current))

  const filteredPlayers = computed(() => {
    const term = keyword.value.trim().toLowerCase()
    if (!term) return players.value
    return players.value.filter(
      p => p.name.toLowerCase().includes(term) || (p.organization_name || '').toLowerCase().includes(term)
    )
  })

  const averageWinRate = computed(() => {
    const list = filteredPlayers.value
    return list.length ? list.reduce((sum, p) => sum + p.win_rate, 0) / list.length : 0
  })
  const topRating = computed(() => Math.max(0, ...filteredPlayers.value.map(p => p.rating)))
  const distribution = computed(() =>
    RATING_BANDS.map((band, index) => ({
      ...band,
      count: filteredPlayers.value.filter(p => p.rating < band.max && p.rating >= (RATING_BANDS[index - 1]?.max ?? 0))
        .length
    }))
  )

  const load = async () => {
    loading.value = true
    error.value = null
    try {
      const { items } = await leaderboardApi.list({
        season_id: seasonId.value || undefined,
        include_guests: includeGuests.value,
        scope: scope.value,
        gender: gender.value || undefined,
        min_matches: minMatches.value ?? 0,
        per_page: 500
      })
      players.value = items.map(p => ({ ...p, organization_name: organizationLabel(p) }))
    } catch (err) {
      error.value = err.response?.data?.message || '載入數據時發生錯誤'
    } finally {
      loading.value = false
    }
  }

  const exportCsv = () => {
    const header = ['名次', '姓名', '組織', '分數', '勝', '敗', '勝率', '最近比賽']
    const rows = filteredPlayers.value.map(p => [
      p.rank,
      p.name,
      p.organization_name,
      formatRating(p.rating),
      p.wins,
      p.losses,
      `${p.win_rate}%`,
      p.last_match_date
    ])
    const escape = value => `"${String(value ?? '').replace(/"/g, '""')}"`
    const csv = [header, ...rows].map(row => row.map(escape).join(',')).join('\n')
    const url = URL.createObjectURL(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }))
    const link = Object.assign(document.createElement('a'), {
      href: url,
      download: `淡江軟網數據_${selectedSeason.value?.name ?? ''}_${new Date().toISOString().slice(0, 10)}.csv`
    })
    link.click()
    URL.revokeObjectURL(url)
  }

  onMounted(async () => {
    load()
    await loadSeasons()
    seasonId.value = seasons.value.find(season => season.is_current)?.id ?? null
  })
</script>

<style scoped>
  .insights {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr)) minmax(0, 1.6fr);
    gap: 16px;
    margin-bottom: 24px;
  }
  .distribution {
    padding: 14px 18px;
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
  }
  .distribution-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--color-text-muted);
  }
  .distribution-bar {
    display: flex;
    height: 14px;
    margin: 10px 0;
    border-radius: var(--radius-full);
    overflow: hidden;
    gap: 2px;
  }
  .segment {
    transform-origin: left;
    animation: grow 900ms var(--ease-out) both;
  }
  @keyframes grow {
    from {
      transform: scaleX(0);
    }
  }
  .distribution-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 12px;
    font-size: 12px;
    color: var(--gray-700);
  }
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }
  .search {
    width: 260px;
  }
  .filters {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px 20px;
  }
  .filter-select {
    width: 170px;
  }
  .filter {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: var(--gray-700);
  }
  .min-matches {
    width: 90px;
  }
  .block {
    margin-bottom: 14px;
  }
  .detail-table {
    border-radius: var(--radius-xl);
    overflow: hidden;
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    background: var(--color-surface);
  }
  .guide {
    margin-top: 24px;
  }

  .detail-table :deep(.clickable-row) {
    cursor: pointer;
  }
  .detail-table :deep(.cell-rank) {
    font-size: 20px;
    font-weight: 700;
    color: var(--gray-500);
  }
  .detail-table :deep(.top-1) {
    color: var(--gold-500);
  }
  .detail-table :deep(.top-2) {
    color: var(--silver-500);
  }
  .detail-table :deep(.top-3) {
    color: var(--bronze-500);
  }
  .detail-table :deep(.cell-player) {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .detail-table :deep(.cell-player-text) {
    display: flex;
    flex-direction: column;
  }
  .detail-table :deep(.cell-player-name) {
    font-weight: 700;
    color: var(--blue-900);
  }
  .detail-table :deep(.cell-player-sub) {
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .detail-table :deep(.guest-tag) {
    margin-left: 6px;
    padding: 0 6px;
    border-radius: var(--radius-full);
    background: var(--gold-100);
    color: var(--accent-text);
    font-size: 11px;
  }
  .detail-table :deep(.cell-score) {
    display: flex;
    align-items: baseline;
    justify-content: flex-end;
    gap: 6px;
  }
  .detail-table :deep(.cell-score-value) {
    font-size: 22px;
    font-weight: 700;
    color: var(--blue-700);
  }
  .detail-table :deep(.cell-provisional) {
    padding: 1px 8px;
    border-radius: var(--radius-full);
    background: var(--gold-100);
    color: var(--accent-text);
    font-size: 12px;
    font-weight: 700;
  }
  .detail-table :deep(.cell-number) {
    font-size: 18px;
    color: var(--gray-700);
  }
  .detail-table :deep(.cell-bar) {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .detail-table :deep(.cell-bar-track) {
    flex: 1;
    height: 8px;
    border-radius: var(--radius-full);
    background: var(--gray-100);
    overflow: hidden;
  }
  .detail-table :deep(.cell-bar-fill) {
    display: block;
    height: 100%;
    border-radius: inherit;
  }
  .detail-table :deep(.cell-bar-text) {
    width: 40px;
    text-align: right;
    font-size: 16px;
  }
  .detail-table :deep(.cell-record) {
    font-size: 18px;
  }
  .detail-table :deep(.cell-record .win) {
    color: var(--color-win);
  }
  .detail-table :deep(.cell-record .loss) {
    color: var(--color-loss);
  }

  @media (max-width: 1100px) {
    .insights {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .distribution {
      grid-column: 1 / -1;
    }
  }
  @media (max-width: 640px) {
    .insights {
      grid-template-columns: 1fr;
    }
    .search {
      width: 100%;
    }
  }
</style>
