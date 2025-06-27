<template>
  <div class="match-management-page">
    <!-- 1. 標題 + 統計卡片 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">比賽記錄管理</h1>
          <p class="page-subtitle">軟式網球比賽數據統計與管理</p>
        </div>

        <!-- 快速統計卡片 -->
        <div class="stats-cards">
          <div class="stat-card matches-stat">
            <div class="stat-icon">
              <n-icon :component="TableIcon" size="24" />
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ totalResults }}</span>
              <span class="stat-label">場次記錄</span>
            </div>
            <div v-if="loading" class="stat-loading">
              <n-spin size="small" />
            </div>
          </div>

          <div class="stat-card actions-stat">
            <div class="stat-icon">
              <n-icon :component="AddIcon" size="24" />
            </div>
            <div class="action-buttons">
              <n-button type="primary" size="medium" class="quick-add-btn" @click="goToRecordMatchPage">
                記錄新比賽
              </n-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 搜尋區域 -->
    <div class="search-section">
      <div class="search-container">
        <div class="search-header">
          <n-button
            :type="searchPanelVisible ? 'primary' : 'default'"
            size="large"
            class="search-toggle-btn"
            @click="toggleSearchPanel"
          >
            <template #icon>
              <n-icon :component="searchPanelVisible ? ChevronUpIcon : SearchIcon" />
            </template>
            {{ searchPanelVisible ? '收起篩選' : '進階篩選' }}
            <n-badge v-if="activeFiltersCount > 0" :value="activeFiltersCount" :offset="[10, -5]" type="error" />
          </n-button>

          <div class="search-actions">
            <n-button :loading="loading" size="large" class="refresh-btn" @click="handleRefreshData">
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              刷新
            </n-button>
          </div>
        </div>

        <!-- 搜尋面板 -->
        <n-collapse-transition :show="searchPanelVisible">
          <div class="search-panel">
            <n-form ref="searchFormRef" :model="searchForm" label-placement="top" size="medium">
              <n-grid :x-gap="20" :y-gap="20" cols="1 s:2 m:3 l:4" responsive="screen">
                <!-- 球員搜尋 -->
                <n-form-item-gi label="球員">
                  <n-select
                    v-model:value="searchForm.player_ids"
                    :options="playerOptions"
                    multiple
                    filterable
                    clearable
                    placeholder="選擇球員"
                    :loading="playersLoading"
                    :max-tag-count="2"
                    @search="handlePlayerSearch"
                  />
                </n-form-item-gi>

                <!-- 比賽類型 -->
                <n-form-item-gi label="比賽類型">
                  <n-select
                    v-model:value="searchForm.match_type"
                    :options="matchTypeOptions"
                    clearable
                    placeholder="選擇類型"
                  />
                </n-form-item-gi>

                <!-- 賽制 -->
                <n-form-item-gi label="賽制">
                  <n-select
                    v-model:value="searchForm.match_format"
                    :options="matchFormatOptions"
                    clearable
                    placeholder="選擇賽制"
                  />
                </n-form-item-gi>

                <!-- 勝負結果 -->
                <n-form-item-gi label="勝負結果">
                  <n-select
                    v-model:value="searchForm.win_loss"
                    :options="winLossOptions"
                    clearable
                    placeholder="選擇勝負"
                    :disabled="!searchForm.player_ids || searchForm.player_ids.length === 0"
                  />
                </n-form-item-gi>

                <!-- 日期範圍 -->
                <n-form-item-gi label="日期範圍" :span="2">
                  <n-date-picker
                    v-model:value="searchForm.dateRange"
                    type="daterange"
                    clearable
                    format="yyyy-MM-dd"
                    placeholder="選擇日期範圍"
                    style="width: 100%"
                  />
                </n-form-item-gi>
              </n-grid>

              <!-- 重置按鈕 -->
              <div class="search-panel-actions">
                <n-button size="medium" class="reset-btn" @click="handleResetSearch">
                  <template #icon>
                    <n-icon :component="RefreshIcon" />
                  </template>
                  重置篩選
                </n-button>
              </div>
            </n-form>
          </div>
        </n-collapse-transition>

        <!-- 活躍篩選條件 -->
        <div v-if="activeFilters.length > 0" class="active-filters">
          <div class="filters-container">
            <span class="filter-label">
              <n-icon :component="FilterIcon" />
              篩選條件:
            </span>
            <n-space size="small" wrap>
              <n-tag
                v-for="filter in activeFilters"
                :key="filter.key"
                closable
                type="info"
                size="medium"
                round
                @close="removeFilter(filter.key)"
              >
                {{ filter.label }}
              </n-tag>
            </n-space>
            <n-button size="small" text type="error" @click="handleResetSearch">
              清除全部
            </n-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. 表格內容區域 -->
    <div class="main-content-section">
      <!-- 錯誤提示 -->
      <n-alert
        v-if="fetchError"
        title="載入錯誤"
        type="error"
        closable
        class="error-alert"
        @close="fetchError = null"
      >
        {{ fetchError }}
      </n-alert>

      <!-- 搜尋結果統計 -->
      <div v-if="searchExecuted" class="search-stats">
        <n-alert type="info" :show-icon="false" class="stats-alert">
          <template #header>
            <n-space align="center">
              <n-icon :component="StatsIcon" />
              <span>找到 <strong>{{ totalResults }}</strong> 筆記錄</span>
              <span v-if="activeFiltersCount > 0" class="filter-info">
                (已套用 {{ activeFiltersCount }} 個篩選條件)
              </span>
            </n-space>
          </template>
        </n-alert>
      </div>

      <!-- 表格區域 -->
      <div class="table-container">
        <div class="table-header">
          <div class="table-title">
            <n-icon :component="TableIcon" />
            比賽記錄列表
          </div>
          <div class="table-info">
            <n-tag type="info" size="small" round>
              總計: {{ totalResults }} 筆
            </n-tag>
          </div>
        </div>

        <n-data-table
          :columns="enhancedTableColumns"
          :data="displayRecords"
          :loading="loading"
          :pagination="paginationConfig"
          :bordered="false"
          :single-line="false"
          size="medium"
          striped
          :scroll-x="1100"
          :row-key="row => row.id"
          class="modern-table enhanced-match-table"
        />

        <!-- 空狀態 -->
        <div v-if="!loading && displayRecords.length === 0" class="empty-container">
          <n-empty description="沒有找到符合條件的比賽記錄" class="empty-state">
            <template #icon>
              <n-icon :component="EmptyIcon" size="64" />
            </template>
            <template #extra>
              <n-space>
                <n-button type="primary" size="large" @click="goToRecordMatchPage">
                  <template #icon>
                    <n-icon :component="AddIcon" />
                  </template>
                  新增第一場比賽
                </n-button>
                <n-button v-if="searchExecuted" size="large" @click="handleResetSearch">
                  重置搜尋條件
                </n-button>
              </n-space>
            </template>
          </n-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, h, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usePermissions } from '@/composables/usePermissions'
import {
  NAlert,
  NBadge,
  NButton,
  NCard,
  NCollapseTransition,
  NDataTable,
  NDatePicker,
  NDivider,
  NEmpty,
  NForm,
  NFormItemGi,
  NGrid,
  NIcon,
  NInputGroup,
  NInputNumber,
  NSelect,
  NSpace,
  NSpin,
  NTag,
  NTooltip,
  useDialog,
  useMessage
} from 'naive-ui'
import {
  AddCircleOutline as AddIcon,
  BarChartOutline as StatsIcon,
  ChevronUpOutline as ChevronUpIcon,
  FunnelOutline as FilterIcon,
  GridOutline as TableIcon,
  PencilOutline as EditIcon,
  RefreshOutline as RefreshIcon,
  SearchOutline as SearchIcon,
  TrashBinOutline as DeleteIcon,
  TrophyOutline as EmptyIcon,
  EyeOutline as EyeIcon
} from '@vicons/ionicons5'
import apiClient from '@/services/apiClient.js'
import { format } from 'date-fns'
import { useOptions } from '@/composables/useOptions'

// Hooks
const router = useRouter()
const dialog = useDialog()
const message = useMessage()
const { hasManagementAccess } = usePermissions()

// 基本狀態
const loading = ref(true)
const searching = ref(false)
const playersLoading = ref(false)
const searchExecuted = ref(false)
const searchPanelVisible = ref(false)
const fetchError = ref(null)
const isResetting = ref(false)

// 數據狀態
const allMatchRecords = ref([])
const displayRecords = ref([])
const totalResults = ref(0)
const currentPage = ref(1)
const pageSize = ref(15)

// 統計數據
const winRate = computed(() => {
  if (displayRecords.value.length === 0) return 0
  const totalMatches = displayRecords.value.length
  const wins = displayRecords.value.filter(record => record.side_a_outcome === 'win').length
  return Math.round((wins / totalMatches) * 100)
})

const {
  matchTypeOptions,
  matchFormatOptions,
  timeSlotOptions,
  timeSlotOptionsWithIcon,
  courtSurfaceOptions,
  courtEnvironmentOptions,
  getTimeSlotWithIcon,
  getNextTimeSlot,
  playerOptions,
  winLossOptions,
  loadPlayerOptions
} = useOptions()

// 搜尋表單
const searchForm = reactive({
  player_ids: [],
  match_type: null,
  match_format: null,
  win_loss: null,
  dateRange: null,
  min_score_diff: null,
  max_score_diff: null
})

// 防抖搜尋
let searchTimeout = null
const SEARCH_DEBOUNCE_DELAY = 500

// ===== 搶7檢測和分數顯示邏輯 =====

// 根據賽制獲取最大局數
const getMaxGamesForFormat = (format) => {
  const formatMap = {
    'games_5': 5,
    'games_7': 7,
    'games_9': 9
  }
  return formatMap[format] || 9
}

// 檢測是否為搶7局
const isTiebreakSituation = (row) => {
  if (!row.match_format) return false

  const maxGames = getMaxGamesForFormat(row.match_format)
  const aGames = row.a_games || 0
  const bGames = row.b_games || 0
  const totalGames = aGames + bGames

  // 檢查是否達到搶7條件：總局數 >= 最大局數-1 且分數接近
  return totalGames >= (maxGames - 1) && Math.abs(aGames - bGames) <= 1
}

// 找到搶7局的局數
const getTiebreakGameNumber = (row) => {
  if (!isTiebreakSituation(row)) return null

  const maxGames = getMaxGamesForFormat(row.match_format)
  const aGames = row.a_games || 0
  const bGames = row.b_games || 0
  const totalGames = aGames + bGames

  // 搶7局是最後一局
  return Math.min(totalGames, maxGames)
}

// 獲取搶7局的詳細分數
const getTiebreakScore = (row) => {
  const tiebreakGameNum = getTiebreakGameNumber(row)
  if (!tiebreakGameNum) return null

  const aScore = row[`game${tiebreakGameNum}_a_score`] || 0
  const bScore = row[`game${tiebreakGameNum}_b_score`] || 0

  // 如果沒有詳細分數數據，返回null
  if (aScore === 0 && bScore === 0) return null

  return { aScore, bScore, gameNumber: tiebreakGameNum }
}

// ===== 輔助函數 =====
const getMatchTypeDisplay = value => matchTypeOptions.find(opt => opt.value === value)?.label || value
const getMatchFormatDisplay = value => matchFormatOptions.find(opt => opt.value === value)?.label || value

// 高亮球員名字
const renderPlayerNameWithHighlight = playerName => {
  if (!playerName) return '-'

  if (!searchedPlayerNames.value || searchedPlayerNames.value.length === 0) {
    return playerName
  }

  const matchedSearchTerm = searchedPlayerNames.value.find(searchName =>
    playerName.toLowerCase().includes(searchName.toLowerCase())
  )

  if (matchedSearchTerm) {
    const escapeRegExp = string => string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const regex = new RegExp(`(${escapeRegExp(matchedSearchTerm)})`, 'gi')
    const highlightedHTML = playerName.replace(regex, '<mark class="search-highlight">$1</mark>')

    return h('span', {
      innerHTML: highlightedHTML
    })
  }

  return playerName
}

// ===== 增強的表格欄位定義（採用game-score-display方式）=====
const enhancedTableColumns = computed(() => [
  {
    title: '比賽日期',
    key: 'match_date',
    sorter: 'default',
    width: 110,
    render: row => (row.match_date ? format(new Date(row.match_date), 'yyyy-MM-dd') : '-')
  },
  {
    title: 'A隊比分',
    key: 'a_score',
    width: 120,
    minWidth: 100,
    align: 'center',
    render: row => {
      const isWinner = row.side_a_outcome === 'win'
      const tiebreakData = getTiebreakScore(row)
      const showTiebreakOnA = tiebreakData && !isWinner

      return h('div', {
        class: ['enhanced-team-score']
      }, [
        h('span', {
          class: ['score-team-a', isWinner ? 'winner' : '']
        }, [
          String(row.a_games || 0),
          showTiebreakOnA && h('span', { class: 'tiebreak-superscript' }, [
            h('sup', {}, String(tiebreakData.aScore))
          ])
        ])
      ])
    }
  },
  {
    title: 'A隊成員',
    key: 'team_a_players',
    width: 200,
    ellipsis: { tooltip: true },
    render: row => {
      const players = []

      if (row.player1) {
        players.push(
          h('div', { class: 'enhanced-player-item' }, [
            h('div', { class: 'position-label-fixed team-a-position' }, '後排'),
            h('span', { class: 'player-name-enhanced' }, renderPlayerNameWithHighlight(row.player1.name))
          ])
        )
      }

      if (row.player2) {
        players.push(
          h('div', { class: 'enhanced-player-item' }, [
            h('div', { class: 'position-label-fixed team-a-position' }, '前排'),
            h('span', { class: 'player-name-enhanced' }, renderPlayerNameWithHighlight(row.player2.name))
          ])
        )
      }

      return h('div', { class: 'enhanced-team-players' }, players)
    }
  },
  {
    title: 'VS',
    key: 'vs',
    width: 60,
    align: 'center',
    render: () => h('div', { class: 'enhanced-vs-separator' }, [
      h('div', { class: 'tennis-ball-mini' }, [
        h('div', { class: 'ball-core-mini' })
      ])
    ])
  },
  {
    title: 'B隊成員',
    key: 'team_b_players',
    width: 200,
    ellipsis: { tooltip: true },
    render: row => {
      const players = []

      if (row.player3) {
        players.push(
          h('div', { class: 'enhanced-player-item' }, [
            h('div', { class: 'position-label-fixed team-b-position' }, '後排'),
            h('span', { class: 'player-name-enhanced' }, renderPlayerNameWithHighlight(row.player3.name))
          ])
        )
      }

      if (row.player4) {
        players.push(
          h('div', { class: 'enhanced-player-item' }, [
            h('div', { class: 'position-label-fixed team-b-position' }, '前排'),
            h('span', { class: 'player-name-enhanced' }, renderPlayerNameWithHighlight(row.player4.name))
          ])
        )
      }

      return h('div', { class: 'enhanced-team-players' }, players)
    }
  },
  {
    title: 'B隊比分',
    key: 'b_score',
    width: 120,
    minWidth: 100,
    align: 'center',
    render: row => {
      const isWinner = row.side_a_outcome === 'loss' // B隊勝利
      const tiebreakData = getTiebreakScore(row)
      const showTiebreakOnB = tiebreakData && !isWinner

      return h('div', {
        class: ['enhanced-team-score']
      }, [
        h('span', {
          class: ['score-team-b', isWinner ? 'winner' : '']
        }, [
          String(row.b_games || 0),
          showTiebreakOnB && h('span', { class: 'tiebreak-superscript' }, [
            h('sup', {}, String(tiebreakData.bScore))
          ])
        ])
      ])
    }
  },
  {
    title: '類型',
    key: 'match_type',
    width: 80,
    render: row => h('span', { class: 'match-info' }, getMatchTypeDisplay(row.match_type))
  },
  {
    title: '賽制',
    key: 'match_format',
    width: 80,
    render: row => h('span', { class: 'match-info' }, getMatchFormatDisplay(row.match_format))
  },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    align: 'center',
    fixed: 'right',
    render: row => {
      const buttons = []

      // 查看詳細數據按鈕
      buttons.push(
        h(NTooltip, {}, {
          trigger: () => h(NButton, {
            size: 'small',
            type: 'info',
            ghost: true,
            onClick: () => viewMatchDetail(row.id)
          }, {
            icon: () => h(NIcon, { component: EyeIcon, size: 16 })
          }),
          default: () => '查看詳細'
        })
      )

      // 編輯按鈕 - 只有幹部以上可見
      if (hasManagementAccess.value) {
        buttons.push(
          h(NTooltip, {}, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'primary',
              ghost: true,
              onClick: () => editMatchRecord(row.id)
            }, {
              icon: () => h(NIcon, { component: EditIcon, size: 16 })
            }),
            default: () => '編輯'
          })
        )

        // 刪除按鈕 - 只有幹部以上可見
        buttons.push(
          h(NTooltip, {}, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error',
              ghost: true,
              onClick: () => confirmDeleteMatch(row)
            }, {
              icon: () => h(NIcon, { component: DeleteIcon, size: 16 })
            }),
            default: () => '刪除'
          })
        )
      }

      return h(NSpace, { justify: 'center', size: 8 }, () => buttons)
    }
  }
])

// 計算屬性
const activeFilters = computed(() => {
  const filters = []

  if (searchForm.player_ids?.length > 0) {
    const playerNames = searchForm.player_ids
      .map(id => playerOptions.value.find(p => p.value === id)?.label || id)
      .join(', ')
    filters.push({ key: 'player_ids', label: `球員: ${playerNames}` })
  }

  if (searchForm.match_type) {
    const typeLabel = matchTypeOptions.find(t => t.value === searchForm.match_type)?.label
    filters.push({ key: 'match_type', label: `類型: ${typeLabel}` })
  }

  if (searchForm.match_format) {
    const formatLabel = matchFormatOptions.find(f => f.value === searchForm.match_format)?.label
    filters.push({ key: 'match_format', label: `賽制: ${formatLabel}` })
  }

  if (searchForm.win_loss) {
    const winLossLabel = winLossOptions.find(w => w.value === searchForm.win_loss)?.label
    filters.push({ key: 'win_loss', label: `結果: ${winLossLabel}` })
  }

  if (searchForm.dateRange?.length === 2) {
    const [start, end] = searchForm.dateRange
    const startDate = new Date(start).toLocaleDateString()
    const endDate = new Date(end).toLocaleDateString()
    filters.push({ key: 'dateRange', label: `日期: ${startDate} ~ ${endDate}` })
  }

  return filters
})

const searchedPlayerNames = computed(() => {
  if (!searchForm.player_ids || searchForm.player_ids.length === 0) {
    return []
  }
  return searchForm.player_ids
    .map(id => {
      const player = playerOptions.value.find(p => p.value === id)
      return player ? player.label : ''
    })
    .filter(name => name)
})

const activeFiltersCount = computed(() => activeFilters.value.length)

// 分頁配置
const paginationConfig = computed(() => ({
  page: currentPage.value,
  pageSize: pageSize.value,
  itemCount: totalResults.value,
  showSizePicker: true,
  pageSizes: [10, 15, 20, 50],
  showQuickJumper: true,
  prefix: ({ itemCount }) => `共 ${itemCount} 項`,
  onUpdatePage: page => {
    handlePageChange(page)
  },
  onUpdatePageSize: newPageSize => {
    pageSize.value = newPageSize
    currentPage.value = 1
    debounceSearch()
  }
}))

// ===== 方法 =====

// 執行搜尋
const performSearch = async () => {
  const hasSearchConditions =
    (searchForm.player_ids && searchForm.player_ids.length > 0) ||
    searchForm.match_type ||
    searchForm.match_format ||
    searchForm.win_loss ||
    (searchForm.dateRange && searchForm.dateRange.length === 2) ||
    searchForm.min_score_diff !== null ||
    searchForm.max_score_diff !== null

  if (!hasSearchConditions) {
    displayRecords.value = allMatchRecords.value
    totalResults.value = allMatchRecords.value.length
    searchExecuted.value = false
    return
  }

  try {
    const params = buildSearchParams()
    const response = await apiClient.get('/match-records', { params })

    let recordsData = []
    let paginationData = null

    if (response.data?.match_records) {
      recordsData = response.data.match_records
      paginationData = response.data.pagination
    } else if (Array.isArray(response.data)) {
      recordsData = response.data
    }

    displayRecords.value = recordsData
    totalResults.value = paginationData?.total || recordsData.length
    searchExecuted.value = true
  } catch (error) {
    console.error('搜尋失敗:', error)
    fetchError.value = error.response?.data?.message || '搜尋失敗'
  }
}

// 防抖搜尋
const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  searching.value = true
  searchTimeout = setTimeout(async () => {
    if (!isResetting.value) {
      await performSearch()
    }
    searching.value = false
  }, SEARCH_DEBOUNCE_DELAY)
}

const toggleSearchPanel = () => {
  searchPanelVisible.value = !searchPanelVisible.value
}

const handlePlayerSearch = async query => {
  if (!query || query.length < 2) {
    await loadPlayers()
    return
  }

  playersLoading.value = true
  try {
    const response = await apiClient.get(`/members?search=${encodeURIComponent(query)}&limit=20`)

    let membersData = response.data
    if (response.data?.members) {
      membersData = response.data.members
    } else if (response.data?.data) {
      membersData = response.data.data
    }

    if (!Array.isArray(membersData)) {
      membersData = []
    }

    const searchResults = membersData.map(member => ({
      label: member.name,
      value: member.id
    }))

    const existingIds = new Set(playerOptions.value.map(p => p.value))
    const newOptions = searchResults.filter(p => !existingIds.has(p.value))
    playerOptions.value = [...playerOptions.value, ...newOptions]
  } catch (error) {
    console.error('搜尋球員失敗:', error)
  } finally {
    playersLoading.value = false
  }
}

const buildSearchParams = () => {
  const params = {
    page: currentPage.value,
    per_page: pageSize.value
  }

  if (searchForm.player_ids?.length > 0) {
    params.player_id = searchForm.player_ids[0]
  }

  if (searchForm.match_type) {
    params.match_type = searchForm.match_type
  }

  if (searchForm.match_format) {
    params.match_format = searchForm.match_format
  }

  if (searchForm.dateRange?.length === 2) {
    params.start_date = new Date(searchForm.dateRange[0]).toISOString().split('T')[0]
    params.end_date = new Date(searchForm.dateRange[1]).toISOString().split('T')[0]
  }

  Object.keys(params).forEach(key => {
    if (params[key] === null || params[key] === undefined || params[key] === '') {
      delete params[key]
    }
  })

  return params
}

const handleResetSearch = async () => {
  isResetting.value = true

  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }

  Object.keys(searchForm).forEach(key => {
    if (Array.isArray(searchForm[key])) {
      searchForm[key] = []
    } else {
      searchForm[key] = null
    }
  })

  await nextTick()
  isResetting.value = false

  searchExecuted.value = false
  currentPage.value = 1
  fetchError.value = null

  displayRecords.value = allMatchRecords.value
  totalResults.value = allMatchRecords.value.length
}

const removeFilter = async filterKey => {
  isResetting.value = true

  switch (filterKey) {
    case 'player_ids':
      searchForm.player_ids = []
      break
    case 'match_type':
      searchForm.match_type = null
      break
    case 'match_format':
      searchForm.match_format = null
      break
    case 'win_loss':
      searchForm.win_loss = null
      break
    case 'dateRange':
      searchForm.dateRange = null
      break
    case 'score_diff':
      searchForm.min_score_diff = null
      searchForm.max_score_diff = null
      break
  }

  await nextTick()
  isResetting.value = false
}

const handlePageChange = page => {
  currentPage.value = page
  debounceSearch()
}

const fetchMatchRecords = async () => {
  loading.value = true
  fetchError.value = null

  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      sort_by: 'match_date',
      sort_order: 'desc'
    }

    const response = await apiClient.get('/match-records', { params })

    let recordsData = []
    let paginationData = null

    if (response.data?.match_records) {
      recordsData = response.data.match_records
      paginationData = response.data.pagination
    } else if (Array.isArray(response.data)) {
      recordsData = response.data
    }

    allMatchRecords.value = recordsData
    displayRecords.value = recordsData
    totalResults.value = paginationData?.total || recordsData.length
  } catch (err) {
    console.error('載入比賽記錄失敗:', err)
    fetchError.value = err.response?.data?.message || '無法載入比賽記錄'
  } finally {
    loading.value = false
  }
}

const handleRefreshData = () => {
  fetchMatchRecords()
}

const goToRecordMatchPage = () => {
  router.push({ name: 'RecordMatch' })
}

const viewMatchDetail = recordId => {
  router.push({ name: 'ViewMatch', params: { id: recordId } })
}

const editMatchRecord = recordId => {
  router.push({ name: 'EditMatch', params: { id: recordId } })
}

const confirmDeleteMatch = record => {
  dialog.error({
    title: '確認刪除比賽記錄',
    content: `您確定要刪除這場比賽記錄嗎？`,
    positiveText: '確認刪除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await apiClient.delete(`/match-records/${record.id}`)
        message.success(`比賽記錄已成功刪除`)
        await handleRefreshData()
      } catch (err) {
        console.error('刪除失敗:', err)
        message.error(err.response?.data?.message || '刪除失敗')
      }
    }
  })
}

const loadPlayers = async () => {
  try {
    const response = await apiClient.get('/members?all=true&sort_by=name&sort_order=asc')

    let membersData = response.data
    if (response.data?.members) {
      membersData = response.data.members
    } else if (response.data?.data) {
      membersData = response.data.data
    }

    if (!Array.isArray(membersData)) {
      membersData = []
    }

    playerOptions.value = membersData.map(member => ({
      label: member.name,
      value: member.id
    }))
  } catch (error) {
    console.error('載入球員列表失敗:', error)
  }
}

// 監聽搜尋條件變化
watch(
  () => [
    searchForm.player_ids,
    searchForm.match_type,
    searchForm.match_format,
    searchForm.win_loss,
    searchForm.dateRange,
    searchForm.min_score_diff,
    searchForm.max_score_diff
  ],
  (newValues, oldValues) => {
    if (!oldValues || isResetting.value) {
      return
    }

    const hasChanged = newValues.some((newVal, index) => {
      const oldVal = oldValues[index]
      if (Array.isArray(newVal) && Array.isArray(oldVal)) {
        return JSON.stringify(newVal) !== JSON.stringify(oldVal)
      }
      return newVal !== oldVal
    })

    if (hasChanged) {
      currentPage.value = 1
      debounceSearch()
    }
  },
  { deep: true }
)

// 監聽球員選擇變更
watch(
  () => searchForm.player_ids,
  newIds => {
    if (!newIds || newIds.length === 0) {
      searchForm.win_loss = null
    }
  }
)

// 生命週期
onMounted(() => {
  fetchMatchRecords()
  loadPlayers()
})

onUnmounted(() => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>

<style scoped>
/* ===========================================
   完整的比賽管理頁面樣式 - Nintendo風格
   =========================================== */

.match-management-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
  font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* ===========================================
   1. 標題 + 統計卡片區域
   =========================================== */

.page-header {
  position: relative;
}

.header-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2.5rem;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 1px 0 rgba(255, 255, 255, 0.5) inset;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.title-section {
  flex: 1;
}

.page-title {
  font-size: 2.75rem;
  font-weight: 800;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #e60012 0%, #ff6b6b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #64748b;
  margin: 0;
  font-weight: 500;
}

/* 統計卡片樣式 */
.stats-cards {
  display: flex;
  gap: 1.5rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  min-width: 120px;
  position: relative;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.matches-stat .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.win-rate-stat .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.actions-stat .stat-icon {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #8b4513;
}

.stat-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a202c;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.stat-loading {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  opacity: 0.6;
}

.action-buttons {
  display: flex;
  align-items: center;
}

.quick-add-btn {
  border-radius: 12px;
  padding: 0.5rem 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #e60012 0%, #ff6b6b 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
  font-size: 0.875rem;
}

.quick-add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(230, 0, 18, 0.4);
}

/* ===========================================
   2. 搜尋區域
   =========================================== */

.search-section {
  position: relative;
}

.search-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.search-toggle-btn {
  border-radius: 16px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.search-actions {
  display: flex;
  gap: 1rem;
}

.refresh-btn {
  border-radius: 16px;
  padding: 0.75rem;
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(148, 163, 184, 0.2);
  transform: translateY(-1px);
}

.search-panel {
  background: rgba(248, 250, 252, 0.5);
  border-radius: 12px;
  padding: 2rem;
  margin-top: 1rem;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.search-panel-actions {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(226, 232, 240, 0.6);
}

.reset-btn {
  border-radius: 12px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  transition: all 0.3s ease;
}

.reset-btn:hover {
  background: rgba(148, 163, 184, 0.2);
  transform: translateY(-1px);
}

/* 活躍篩選條件 */
.active-filters {
  background: rgba(241, 245, 249, 0.8);
  border-radius: 12px;
  padding: 1rem;
  margin-top: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
}

.filters-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-label {
  font-weight: 600;
  color: #475569;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* ===========================================
   3. 主要內容區域
   =========================================== */

.main-content-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.error-alert {
  margin: 1.5rem;
  border-radius: 12px;
}

.search-stats {
  margin: 0 1.5rem;
}

.stats-alert {
  border-radius: 12px;
}

.filter-info {
  color: #6b7280;
  font-size: 0.875rem;
}

.table-container {
  flex: 1;
  padding: 1.5rem;
  overflow-x: auto;
  padding-bottom: 8px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.table-title {
  font-weight: 600;
  color: #374151;
  font-size: 1.125rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.table-info {
  display: flex;
  gap: 0.5rem;
}

/* ===========================================
   4. Game Score Display 樣式
   =========================================== */

/* 增強的團隊比分樣式 */
:deep(.enhanced-team-score) {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  min-height: 60px;
}

/* 分數樣式 - 採用game-score-display的設計 */
:deep(.score-team-a) {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  min-width: 1.2em;
  text-align: center;
  transition: all 0.3s ease;
}

:deep(.score-team-b) {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  min-width: 1.2em;
  text-align: center;
  transition: all 0.3s ease;
}

/* 獲勝方樣式 */
:deep(.score-team-a.winner) {
  color: #059669;
  text-shadow: 0 0 10px rgba(5, 150, 105, 0.3);
  transform: scale(1.1);
  animation: winner-glow 2s ease-in-out infinite;
}

:deep(.score-team-b.winner) {
  color: #059669;
  text-shadow: 0 0 10px rgba(5, 150, 105, 0.3);
  transform: scale(1.1);
  animation: winner-glow 2s ease-in-out infinite;
}

@keyframes winner-glow {
  0%, 100% {
    text-shadow: 0 0 10px rgba(5, 150, 105, 0.3);
  }
  50% {
    text-shadow: 0 0 20px rgba(5, 150, 105, 0.6);
  }
}

/* 搶7上標樣式 - 採用game-score-display的設計 */
:deep(.tiebreak-superscript) {
  margin-left: -0.5rem;
}

:deep(.tiebreak-superscript sup) {
  font-size: 0.6em;
  color: #f59e0b;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* ===========================================
   5. Position Label Fixed 樣式
   =========================================== */

/* 球員項目樣式 */
:deep(.enhanced-player-item) {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  padding: 4px 0;
}

:deep(.enhanced-player-item:last-child) {
  margin-bottom: 0;
}

:deep(.enhanced-team-players) {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  padding: 4px 0;
}

/* 位置標籤樣式 - 採用position-label-fixed的設計 */
:deep(.position-label-fixed) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 1.25rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
  line-height: 1;
  padding: 0.25rem 0.5rem;
  transition: all 0.3s ease;
}

:deep(.position-label-fixed.team-a-position) {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}


:deep(.position-label-fixed.team-b-position) {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

:deep(.position-label-fixed:hover) {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

/* 球員名稱樣式 */
:deep(.player-name-enhanced) {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

/* ===========================================
   6. VS分隔符 - 迷你網球
   =========================================== */

:deep(.enhanced-vs-separator) {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  padding: 0 8px;
}

:deep(.tennis-ball-mini) {
  width: 24px;
  height: 24px;
  background: radial-gradient(circle at 30% 30%, #ffffff, #f0f0f0);
  border-radius: 50%;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  animation: bounce-mini 2s ease-in-out infinite;
}

:deep(.tennis-ball-mini::before,
.tennis-ball-mini::after ){
  content: '';
  position: absolute;
  background: #fff;
  border-radius: 50%;
}

:deep(.tennis-ball-mini::before) {
  width: 2px;
  height: 12px;
  top: 6px;
  left: 11px;
  border-radius: 1px;
}

:deep(.tennis-ball-mini::after) {
  width: 12px;
  height: 2px;
  top: 11px;
  left: 6px;
  border-radius: 1px;
}

@keyframes bounce-mini {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

/* 比賽信息 */
.match-info {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
  text-align: center;
}

/* ===========================================
   7. 表格深度樣式
   =========================================== */

:deep(.enhanced-match-table .n-data-table) {
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
}

:deep(.enhanced-match-table .n-data-table-thead) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

:deep(.enhanced-match-table .n-data-table-th) {
  font-weight: 700;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  background: transparent;
  font-size: 0.875rem;
  padding: 12px 8px !important;
  text-align: center;
}

:deep(.enhanced-match-table .n-data-table-td) {
  transition: background-color 0.2s ease;
  padding: 12px 8px !important;
  vertical-align: middle;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

:deep(.enhanced-match-table .n-data-table-tr:hover) {
  background: linear-gradient(135deg, rgba(230, 0, 18, 0.02) 0%, rgba(255, 107, 107, 0.02) 100%);
}

:deep(.enhanced-match-table .n-data-table-tr:hover .enhanced-team-score) {
  transform: scale(1.03);
}

/* 搜尋高亮增強 */
:deep(.search-highlight) {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #92400e;
  font-weight: 600;
  padding: 2px 4px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* ===========================================
   8. 空狀態和載入動畫
   =========================================== */

.empty-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.empty-state {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* ===========================================
   9. 滾動條美化
   =========================================== */

.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: linear-gradient(90deg, #cbd5e1, #94a3b8);
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(90deg, #94a3b8, #64748b);
}

/* ===========================================
   10. 響應式設計
   =========================================== */

@media (max-width: 1200px) {
  .enhanced-match-table {
    min-width: 950px;
  }

  .enhanced-team-score {
    min-height: 55px;
    padding: 8px 6px;
  }

  .score-team-a,
  .score-team-b {
    font-size: 2.2rem;
  }

  .player-name-enhanced {
    font-size: 0.8rem;
  }

  .position-label-fixed {
    min-width: 2.2rem;
    height: 1.1rem;
    font-size: 0.7rem;
  }
}

@media (max-width: 968px) {
  .enhanced-match-table {
    min-width: 850px;
  }

  .enhanced-team-score {
    min-height: 50px;
    padding: 6px 5px;
  }

  .score-team-a,
  .score-team-b {
    font-size: 2rem;
  }

  .player-name-enhanced {
    font-size: 0.75rem;
  }

  .position-label-fixed {
    min-width: 2rem;
    height: 1rem;
    font-size: 0.65rem;
    padding: 0.2rem 0.4rem;
  }
}

@media (max-width: 768px) {
  .match-management-page {
    padding: 1.5rem;
    gap: 1.5rem;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
    padding: 2rem;
  }

  .page-title {
    font-size: 2.25rem;
  }

  .stats-cards {
    width: 100%;
    justify-content: space-between;
  }

  .stat-card {
    flex: 1;
    min-width: 100px;
    padding: 1rem;
  }

  .search-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .search-panel {
    padding: 1.5rem;
  }

  .filters-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .table-container {
    padding: 1rem;
    margin: 0 -0.5rem;
  }

  .enhanced-match-table {
    min-width: 750px;
    margin: 0;
    border-radius: 8px;
  }

  .score-team-a,
  .score-team-b {
    font-size: 1.8rem;
  }

  .player-name-enhanced {
    font-size: 0.7rem;
  }

  .position-label-fixed {
    min-width: 1.8rem;
    height: 0.9rem;
    font-size: 0.6rem;
  }

  .tennis-ball-mini {
    width: 20px;
    height: 20px;
  }
}

@media (max-width: 480px) {
  .match-management-page {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.875rem;
  }

  .stats-cards {
    flex-direction: column;
    gap: 1rem;
  }

  .stat-card {
    min-width: auto;
  }

  .search-panel {
    padding: 1rem;
  }

  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .enhanced-match-table {
    min-width: 680px;
  }

  .enhanced-team-score {
    min-height: 45px;
    padding: 6px 4px;
  }

  .score-team-a,
  .score-team-b {
    font-size: 1.6rem;
  }

  .position-label-fixed {
    min-width: 1.6rem;
    height: 0.8rem;
    font-size: 0.55rem;
    padding: 0.15rem 0.3rem;
  }

  .tennis-ball-mini {
    width: 16px;
    height: 16px;
  }
}

/* ===========================================
   11. Nintendo風格動畫效果
   =========================================== */

/* 卡片hover效果 */
.stat-card:hover {
  animation: nintendo-bounce 0.6s ease;
}

@keyframes nintendo-bounce {
  0%, 100% {
    transform: translateY(-2px);
  }
  50% {
    transform: translateY(-6px);
  }
}

/* 按鈕點擊效果 */
.quick-add-btn:active,
.search-toggle-btn:active,
.refresh-btn:active {
  transform: scale(0.95);
}

/* 表格行動畫 */
:deep(.enhanced-match-table .n-data-table-tr) {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.enhanced-match-table .n-data-table-tr:nth-child(even)) {
  background: rgba(248, 250, 252, 0.3);
}

/* 載入動畫增強 */
.stat-loading .n-spin {
  animation: spin-nintendo 1s linear infinite;
}

@keyframes spin-nintendo {
  0% {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.1);
  }
  100% {
    transform: rotate(360deg) scale(1);
  }
}
</style>