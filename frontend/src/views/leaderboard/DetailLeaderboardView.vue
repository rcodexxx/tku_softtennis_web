<template>
  <div class="detail-page">
    <PageHeader eyebrow="STATISTICS" title="詳細數據" subtitle="所有球員的評分、戰績與穩定度，點選球員可看完整分析。">
      <template #actions>
        <n-button secondary :disabled="!filteredPlayers.length" @click="exportCsv">
          <template #icon><n-icon :component="DownloadOutline" /></template>
          匯出 CSV
        </n-button>
        <n-button secondary :loading="loading" @click="load">
          <template #icon><n-icon :component="RefreshOutline" /></template>
          重新整理
        </n-button>
      </template>
    </PageHeader>

    <div class="insights">
      <StatCard label="符合條件的球員" :value="filteredPlayers.length" :icon="PeopleOutline" />
      <StatCard
        label="平均勝率"
        :value="averageWinRate"
        :decimals="1"
        suffix="%"
        :icon="PieChartOutline"
        accent="var(--green-600)"
      />
      <StatCard label="最高潛在實力" :value="topPotential" :icon="FlashOutline" accent="var(--gold-500)" />
      <div class="distribution">
        <span class="distribution-title">經驗等級分布</span>
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
            {{ level.icon }} {{ level.label }} <b class="num">{{ level.count }}</b>
          </span>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <n-input v-model:value="keyword" placeholder="搜尋球員或組織" clearable round class="search">
        <template #prefix><n-icon :component="SearchOutline" /></template>
      </n-input>
      <div class="filters">
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
      :scroll-x="1100"
      :bordered="false"
    />

    <RatingGuide class="guide" />

    <PlayerDetailModal :player="selected" :my-member-id="authStore.user?.member_id ?? null" @close="selected = null" />
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import {
    DownloadOutline,
    FlashOutline,
    PeopleOutline,
    PieChartOutline,
    RefreshOutline,
    SearchOutline
  } from '@vicons/ionicons5'
  import { leaderboardApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import StatCard from '@/components/base/StatCard.vue'
  import { detailColumns } from '@/components/leaderboard/detailColumns'
  import PlayerDetailModal from '@/components/leaderboard/PlayerDetailModal.vue'
  import RatingGuide from '@/components/leaderboard/RatingGuide.vue'
  import { useAuthStore } from '@/stores/authStore'
  import { EXPERIENCE_LEVELS } from '@/utils/experience'
  import { organizationLabel } from '@/utils/player'

  const LEVEL_COLORS = ['#c7d7fb', '#5b8cf0', '#2e64d3', '#163a80', '#f2b705']

  const authStore = useAuthStore()

  const loading = ref(true)
  const error = ref(null)
  const players = ref([])
  const includeGuests = ref(false)
  const minMatches = ref(1)
  const keyword = ref('')
  const selected = ref(null)
  const columns = detailColumns()

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
  const topPotential = computed(() => Math.round(Math.max(0, ...filteredPlayers.value.map(p => p.mu)) * 100))
  const distribution = computed(() =>
    EXPERIENCE_LEVELS.map((level, index) => ({
      ...level,
      color: LEVEL_COLORS[index],
      count: filteredPlayers.value.filter(p => p.experience_level === level.label).length
    }))
  )

  const load = async () => {
    loading.value = true
    error.value = null
    try {
      const { items } = await leaderboardApi.list({
        include_guests: includeGuests.value,
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
    const header = [
      '名次',
      '姓名',
      '組織',
      '排名分數',
      '潛在實力',
      '勝',
      '敗',
      '勝率',
      '穩定度',
      '可信度',
      '經驗等級',
      'μ',
      'σ'
    ]
    const rows = filteredPlayers.value.map(p => [
      p.rank,
      p.name,
      p.organization_name,
      Math.round(p.conservative_score * 100),
      Math.round(p.mu * 100),
      p.wins,
      p.losses,
      `${p.win_rate}%`,
      `${p.consistency_rating}%`,
      `${p.rating_confidence}%`,
      p.experience_level,
      p.mu,
      p.sigma
    ])
    const escape = value => `"${String(value ?? '').replace(/"/g, '""')}"`
    const csv = [header, ...rows].map(row => row.map(escape).join(',')).join('\n')
    const url = URL.createObjectURL(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }))
    const link = Object.assign(document.createElement('a'), {
      href: url,
      download: `淡江軟網數據_${new Date().toISOString().slice(0, 10)}.csv`
    })
    link.click()
    URL.revokeObjectURL(url)
  }

  onMounted(load)
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
    gap: 20px;
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
    color: #92400e;
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
