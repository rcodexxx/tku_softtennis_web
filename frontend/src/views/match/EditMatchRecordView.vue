<template>
  <div class="record-match-page container-fluid mt-4 mb-5 px-md-4">
    <!-- 載入狀態 -->
    <n-spin :show="loading" style="width: 100%">
      <n-card :bordered="false" class="form-card">
        <!-- 頁面標題 -->
        <div class="page-header mb-4">
          <n-button quaternary circle style="margin-right: 1rem" @click="goBack">
            <template #icon>
              <n-icon :component="ArrowLeftIcon" />
            </template>
          </n-button>
          <h1 class="page-title">編輯比賽記錄 #{{ recordId }}</h1>
        </div>

        <!-- 表單內容 -->
        <n-form
          ref="formRef"
          :model="matchForm"
          :rules="formRules"
          label-placement="top"
          @submit.prevent="handleUpdateMatch"
        >
          <!-- 比賽基本資訊 -->
          <n-divider style="margin-top: 2rem; margin-bottom: 2rem">
            <n-text style="font-size: 14px; color: #666">比賽基本資訊</n-text>
          </n-divider>
          <n-grid :x-gap="20" :y-gap="20" cols="1 s:3" responsive="screen" align-items="start">
            <n-form-item-gi label="比賽日期" path="match_date">
              <n-date-picker
                v-model:value="matchForm.match_date_ts"
                type="date"
                placeholder="選擇比賽日期"
                style="width: 100%"
                size="large"
              />
            </n-form-item-gi>
            <n-form-item-gi label="比賽類型" path="match_type">
              <n-select v-model:value="matchForm.match_type" :options="matchTypeOptions" size="large" />
            </n-form-item-gi>
            <n-form-item-gi label="賽制" path="match_format">
              <n-select v-model:value="matchForm.match_format" :options="matchFormatOptions" size="large" />
            </n-form-item-gi>
          </n-grid>

          <!-- 球員選擇區域 - 使用組件 -->
          <n-divider style="margin-top: 2rem; margin-bottom: 2rem">
            <n-text style="font-size: 14px; color: #666">球員設定</n-text>
          </n-divider>

          <MatchPlayerSelector ref="playerSelectorRef" v-model="matchForm" />

          <!-- 可折疊的詳細設定區塊 -->
          <n-divider style="margin-top: 2rem; margin-bottom: 1rem">
            <n-button text style="color: #666; font-size: 14px" @click="showAdvancedSettings = !showAdvancedSettings">
              <template #icon>
                <n-icon :component="showAdvancedSettings ? ChevronUpIcon : ChevronDownIcon" />
              </template>
              詳細設定
            </n-button>
          </n-divider>

          <!-- 可折疊內容 -->
          <n-collapse-transition :show="showAdvancedSettings">
            <div class="advanced-settings-container">
              <!-- 場地資訊 -->
              <div class="settings-section">
                <n-grid :x-gap="16" :y-gap="16" cols="1 s:3" responsive="screen" class="mt-3">
                  <n-form-item-gi label="場地材質" path="court_surface">
                    <n-select
                      v-model:value="matchForm.court_surface"
                      :options="courtSurfaceOptions"
                      placeholder="選擇場地材質"
                      clearable
                      size="medium"
                    />
                  </n-form-item-gi>

                  <n-form-item-gi label="場地環境" path="court_environment">
                    <n-select
                      v-model:value="matchForm.court_environment"
                      :options="courtEnvironmentOptions"
                      placeholder="選擇場地環境"
                      clearable
                      size="medium"
                    />
                  </n-form-item-gi>

                  <n-form-item-gi label="比賽時段" path="time_slot">
                    <n-select
                      v-model:value="matchForm.time_slot"
                      :options="timeSlotOptions"
                      placeholder="選擇比賽時段"
                      clearable
                      size="medium"
                    />
                  </n-form-item-gi>
                </n-grid>
              </div>

              <!-- 比賽詳細資訊 -->
              <div class="settings-section">
                <n-grid :x-gap="16" :y-gap="16" cols="1 s:2" responsive="screen" class="mt-3">
                  <!-- 移除總得分，只保留時間和YouTube連結 -->
                  <n-form-item-gi label="比賽時長 (分鐘)" path="duration_minutes">
                    <n-input-number
                      v-model:value="matchForm.duration_minutes"
                      placeholder="分鐘"
                      :min="10"
                      :max="180"
                      clearable
                      size="medium"
                      style="width: 100%"
                    />
                  </n-form-item-gi>

                  <n-form-item-gi label="YouTube 網址" path="youtube_url">
                    <n-input
                      v-model:value="matchForm.youtube_url"
                      placeholder="https://www.youtube.com/watch?v=..."
                      clearable
                      size="medium"
                    />
                  </n-form-item-gi>
                </n-grid>

                <!-- 詳細比分記錄 -->
                <div class="detailed-score-section">
                  <n-divider style="margin: 1.5rem 0 1rem 0">
                    <div class="score-section-header">
                      <span class="score-title">詳細比分記錄</span>
                    </div>
                  </n-divider>

                  <div class="score-toggle-container">
                    <n-button
                      text
                      type="primary"
                      class="toggle-detailed-btn"
                      size="medium"
                      @click="enableDetailedScoring = !enableDetailedScoring"
                    >
                      <template #icon>
                        <n-icon>
                          <CheckboxOutline v-if="!enableDetailedScoring" />
                          <CheckboxSharp v-else />
                        </n-icon>
                      </template>
                      {{ enableDetailedScoring ? '已啟用詳細記錄' : '啟用詳細記錄' }}
                    </n-button>
                  </div>

                  <!-- 詳細比分內容 -->
                  <n-collapse-transition :show="enableDetailedScoring">
                    <div class="detailed-score-content">
                      <!-- 先發球選擇和顯示模式選擇 -->
                      <div class="control-panel">
                        <div class="serve-selector">
                          <n-form-item label="先發球方" :show-feedback="false" size="small">
                            <n-radio-group v-model:value="matchForm.first_serve_side" size="small">
                              <n-space>
                                <n-radio value="side_a">A方先發</n-radio>
                                <n-radio value="side_b">B方先發</n-radio>
                              </n-space>
                            </n-radio-group>
                          </n-form-item>
                        </div>

                        <div class="display-mode-selector">
                          <n-form-item label="顯示模式" :show-feedback="false" size="small">
                            <n-radio-group v-model:value="scoreDisplayMode" size="small">
                              <n-space>
                                <n-radio value="table">表格模式</n-radio>
                                <n-radio value="cards">卡片模式</n-radio>
                              </n-space>
                            </n-radio-group>
                          </n-form-item>
                        </div>
                      </div>

                      <!-- 表格模式 -->
                      <div v-if="scoreDisplayMode === 'table'" class="score-table-mode">
                        <n-table :bordered="false" :single-line="false" size="small" class="score-table">
                          <thead>
                            <tr>
                              <th style="text-align: center; width: 20%">局數</th>
                              <th style="text-align: center; width: 20%">A方得分</th>
                              <th style="text-align: center; width: 20%">B方得分</th>
                              <th style="text-align: center; width: 25%">狀態</th>
                              <th style="text-align: center; width: 15%">操作</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              v-for="gameNum in maxGames"
                              :key="gameNum"
                              :class="{
                                'completed-row': isGameCompleted(gameNum),
                                'disabled-row': isGameDisabled(gameNum),
                                'invalid-row': getScoreInputStatus(gameNum)?.type === 'error',
                                'tiebreak-row': isTiebreakGame(gameNum)
                              }"
                            >
                              <td style="text-align: center">
                                <!-- 局數標題含 Tiebreak 標識 -->
                                <div class="game-number-cell">
                                  <strong>{{ getGameTitle(gameNum) }}</strong>
                                  <div v-if="isTiebreakGame(gameNum)" class="tiebreak-badge">
                                    <n-tag type="warning" size="small" round>決勝局</n-tag>
                                  </div>
                                </div>
                              </td>
                              <!-- A方得分含動態發球顯示 -->
                              <td style="text-align: center">
                                <div class="score-input-container">
                                  <!-- 網球icon顯示在輸入框前 -->
                                  <span
                                    v-if="isATeamServing(gameNum)"
                                    class="serve-icon table-serve-icon"
                                    title="A方發球"
                                    >🎾</span
                                  >
                                  <n-input-number
                                    v-model:value="matchForm[`game${gameNum}_a_score`]"
                                    :min="0"
                                    :max="50"
                                    :disabled="isGameDisabled(gameNum)"
                                    :status="getScoreInputStatus(gameNum)?.type"
                                    size="small"
                                    style="width: 100%; max-width: 80px"
                                    @update:value="updateGameStatistics"
                                  />
                                </div>
                              </td>
                              <!-- B方得分含動態發球顯示 -->
                              <td style="text-align: center">
                                <div class="score-input-container">
                                  <!-- 網球icon顯示在輸入框前 -->
                                  <span
                                    v-if="isBTeamServing(gameNum)"
                                    class="serve-icon table-serve-icon"
                                    title="B方發球"
                                    >🎾</span
                                  >
                                  <n-input-number
                                    v-model:value="matchForm[`game${gameNum}_b_score`]"
                                    :min="0"
                                    :max="50"
                                    :disabled="isGameDisabled(gameNum)"
                                    :status="getScoreInputStatus(gameNum)?.type"
                                    size="small"
                                    style="width: 100%; max-width: 80px"
                                    @update:value="updateGameStatistics"
                                  />
                                </div>
                              </td>
                              <td style="text-align: center">
                                <!-- 詳細狀態顯示 -->
                                <div class="game-status-display">
                                  <n-tag
                                    v-if="isGameCompleted(gameNum)"
                                    :type="getGameResultType(gameNum)"
                                    size="small"
                                    round
                                  >
                                    {{ getGameResult(gameNum) }}
                                  </n-tag>
                                  <n-tag
                                    v-else-if="getScoreInputStatus(gameNum)"
                                    :type="getScoreInputStatus(gameNum).type"
                                    size="small"
                                    round
                                  >
                                    {{ getScoreInputStatus(gameNum).message }}
                                  </n-tag>
                                  <span v-else-if="isGameDisabled(gameNum)" style="color: #ccc">
                                    <n-icon><LockClosedOutline /></n-icon> 已鎖定
                                  </span>
                                  <span v-else style="color: #ccc">{{
                                    isTiebreakGame(gameNum) ? '未開始 (Tiebreak)' : '未開始'
                                  }}</span>
                                </div>
                              </td>
                              <td style="text-align: center">
                                <!-- 重置按鈕 -->
                                <n-button
                                  v-if="
                                    (matchForm[`game${gameNum}_a_score`] > 0 ||
                                      matchForm[`game${gameNum}_b_score`] > 0) &&
                                    !isGameDisabled(gameNum)
                                  "
                                  size="tiny"
                                  type="warning"
                                  ghost
                                  style="padding: 2px 8px"
                                  @click="resetGameScore(gameNum)"
                                >
                                  重置
                                </n-button>
                              </td>
                            </tr>
                          </tbody>
                        </n-table>
                      </div>

                      <!-- 卡片模式 -->
                      <div v-else class="score-cards-mode">
                        <n-grid :x-gap="12" :y-gap="12" :cols="getCardsPerRow">
                          <n-grid-item v-for="gameNum in maxGames" :key="gameNum">
                            <n-card
                              size="small"
                              class="game-score-card"
                              :class="{
                                'completed-card': isGameCompleted(gameNum),
                                'disabled-card': isGameDisabled(gameNum),
                                'invalid-card': getScoreInputStatus(gameNum)?.type === 'error',
                                'deuce-card': getGameStatus(gameNum)?.status === 'deuce',
                                'advantage-card': getGameStatus(gameNum)?.status === 'advantage',
                                'tiebreak-card': isTiebreakGame(gameNum)
                              }"
                            >
                              <template #header>
                                <div class="card-game-header">
                                  <!-- 卡片標題含 Tiebreak 標識 -->
                                  <div class="card-title-section">
                                    <span>{{ getGameTitle(gameNum) }}</span>
                                    <n-tag v-if="isTiebreakGame(gameNum)" type="warning" size="tiny" round>
                                      決勝局
                                    </n-tag>
                                  </div>
                                  <div class="card-status">
                                    <n-tag
                                      v-if="isGameCompleted(gameNum)"
                                      :type="getGameResultType(gameNum)"
                                      size="small"
                                      round
                                    >
                                      {{ getGameResult(gameNum) }}
                                    </n-tag>
                                    <n-tag
                                      v-else-if="getScoreInputStatus(gameNum)"
                                      :type="getScoreInputStatus(gameNum).type"
                                      size="small"
                                      round
                                    >
                                      {{ getScoreInputStatus(gameNum).message }}
                                    </n-tag>
                                    <n-icon v-else-if="isGameDisabled(gameNum)" size="16" style="color: #ccc">
                                      <LockClosedOutline />
                                    </n-icon>
                                  </div>
                                </div>
                              </template>

                              <n-space vertical :size="8">
                                <!-- A方輸入含動態發球顯示 -->
                                <n-form-item :show-feedback="false" size="small">
                                  <template #label>
                                    <div class="team-label">
                                      <!-- 卡片模式：網球icon顯示在標籤前 -->
                                      <span
                                        v-if="isATeamServing(gameNum)"
                                        class="serve-icon card-serve-icon"
                                        title="A方發球"
                                        >🎾</span
                                      >
                                      <span>A方</span>
                                    </div>
                                  </template>
                                  <n-input-number
                                    v-model:value="matchForm[`game${gameNum}_a_score`]"
                                    :min="0"
                                    :max="50"
                                    :disabled="isGameDisabled(gameNum)"
                                    :status="getScoreInputStatus(gameNum)?.type"
                                    size="small"
                                    style="width: 100%"
                                    @update:value="updateGameStatistics"
                                  />
                                </n-form-item>

                                <!-- B方輸入含動態發球顯示 -->
                                <n-form-item :show-feedback="false" size="small">
                                  <template #label>
                                    <div class="team-label">
                                      <!-- 卡片模式：網球icon顯示在標籤前 -->
                                      <span
                                        v-if="isBTeamServing(gameNum)"
                                        class="serve-icon card-serve-icon"
                                        title="B方發球"
                                        >🎾</span
                                      >
                                      <span>B方</span>
                                    </div>
                                  </template>
                                  <n-input-number
                                    v-model:value="matchForm[`game${gameNum}_b_score`]"
                                    :min="0"
                                    :max="50"
                                    :disabled="isGameDisabled(gameNum)"
                                    :status="getScoreInputStatus(gameNum)?.type"
                                    size="small"
                                    style="width: 100%"
                                    @update:value="updateGameStatistics"
                                  />
                                </n-form-item>

                                <!-- 卡片操作區 -->
                                <div
                                  v-if="
                                    (matchForm[`game${gameNum}_a_score`] > 0 ||
                                      matchForm[`game${gameNum}_b_score`] > 0) &&
                                    !isGameDisabled(gameNum)
                                  "
                                  class="card-actions"
                                >
                                  <n-button
                                    size="tiny"
                                    type="warning"
                                    ghost
                                    style="width: 100%"
                                    @click="resetGameScore(gameNum)"
                                  >
                                    重置該局
                                  </n-button>
                                </div>
                              </n-space>
                            </n-card>
                          </n-grid-item>
                        </n-grid>
                      </div>

                      <!-- 即時統計 -->
                      <div class="real-time-statistics">
                        <n-divider style="margin: 1rem 0 0.5rem 0">
                          <n-text style="font-size: 14px; color: #666">即時統計</n-text>
                        </n-divider>
                        <n-grid :x-gap="12" :cols="6" class="stats-summary">
                          <n-statistic
                            label="A方獲勝"
                            :value="detailedStats.aWins"
                            :value-style="{ color: detailedStats.aWins >= gamesToWin ? '#52c41a' : '#1890ff' }"
                            class="stat-item"
                          />
                          <n-statistic
                            label="B方獲勝"
                            :value="detailedStats.bWins"
                            :value-style="{ color: detailedStats.bWins >= gamesToWin ? '#fa8c16' : '#1890ff' }"
                            class="stat-item"
                          />
                          <n-statistic label="已完成局數" :value="detailedStats.completedGames" class="stat-item" />
                          <!-- 進行中局數 -->
                          <n-statistic
                            label="進行中局數"
                            :value="detailedStats.inProgressGames"
                            :value-style="{ color: detailedStats.inProgressGames > 0 ? '#faad14' : '#1890ff' }"
                            class="stat-item"
                          />
                          <n-statistic label="總得分" :value="detailedStats.totalPoints" class="stat-item" />
                          <n-statistic
                            :label="
                              matchForm.first_serve_side === 'side_a'
                                ? 'A方先發'
                                : matchForm.first_serve_side === 'side_b'
                                  ? 'B方先發'
                                  : '先發球方'
                            "
                            :value="
                              matchForm.first_serve_side === 'side_a'
                                ? '🏓 A'
                                : matchForm.first_serve_side === 'side_b'
                                  ? '🏓 B'
                                  : '?'
                            "
                            class="stat-item serve-stat"
                          />
                        </n-grid>
                      </div>
                    </div>
                  </n-collapse-transition>
                </div>
              </div>
            </div>
          </n-collapse-transition>

          <!-- 操作按鈕 -->
          <n-divider style="margin-top: 2rem; margin-bottom: 2rem" />
          <n-space justify="space-between" style="width: 100%">
            <n-button size="large" @click="goBack">
              <template #icon>
                <n-icon :component="ArrowLeftIcon" />
              </template>
              返回
            </n-button>
            <n-space>
              <n-button
                type="primary"
                size="large"
                :loading="submitting"
                :disabled="!canSubmit"
                @click="handleUpdateMatch"
              >
                <template #icon>
                  <n-icon :component="SaveIcon" />
                </template>
                更新比賽記錄
              </n-button>
            </n-space>
          </n-space>
        </n-form>
      </n-card>
    </n-spin>
  </div>
</template>

<script setup>
// 1. 引入 (Imports) - 修改這一行
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue' // 添加 reactive
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import apiClient from '@/services/apiClient'
import MatchPlayerSelector from '@/components/MatchPlayerSelector.vue'

// 引入圖標
import {
  ArrowBackOutline as ArrowLeftIcon,
  ChevronDownOutline as ChevronDownIcon,
  ChevronUpOutline as ChevronUpIcon,
  RefreshOutline as RefreshIcon,
  SaveOutline as SaveIcon,
  CheckboxOutline,
  CheckboxSharp,
  LockClosedOutline
} from '@vicons/ionicons5'

// 2. 實例化 hooks
const router = useRouter()
const route = useRoute()
const message = useMessage()

// 3. 狀態管理 (State)
const loading = ref(true)
const submitting = ref(false)
const showAdvancedSettings = ref(false)
const formRef = ref(null)
const recordId = ref(route.params.id)
const playerSelectorRef = ref(null)
const enableDetailedScoring = ref(true)
const scoreDisplayMode = ref('table')
const isLoadingData = ref(false)

// 4. 表單數據 (Form Data) - 🔥 改為 reactive
const matchForm = reactive({
  match_date_ts: null,
  match_date: '',
  match_type: 'doubles',
  match_format: 'games_9',
  player1_id: null,
  player2_id: null,
  player3_id: null,
  player4_id: null,
  a_games: 0,
  b_games: 0,
  match_notes: '',
  court_surface: null,
  court_environment: null,
  time_slot: null,
  total_points: null,
  duration_minutes: null,
  youtube_url: '',
  first_serve_side: null,

  // 🔥 初始化所有局比分
  game1_a_score: 0,
  game1_b_score: 0,
  game2_a_score: 0,
  game2_b_score: 0,
  game3_a_score: 0,
  game3_b_score: 0,
  game4_a_score: 0,
  game4_b_score: 0,
  game5_a_score: 0,
  game5_b_score: 0,
  game6_a_score: 0,
  game6_b_score: 0,
  game7_a_score: 0,
  game7_b_score: 0,
  game8_a_score: 0,
  game8_b_score: 0,
  game9_a_score: 0,
  game9_b_score: 0
})

// 5. 選項數據 (Options Data) - 保持不變
const matchTypeOptions = [
  { label: '單打', value: 'singles' },
  { label: '雙打', value: 'doubles' }
]

const matchFormatOptions = [
  { label: '五局制', value: 'games_5' },
  { label: '七局制', value: 'games_7' },
  { label: '九局制', value: 'games_9' }
]

const courtSurfaceOptions = [
  { label: '硬地', value: 'hard_court' },
  { label: '紅土', value: 'clay_court' },
  { label: '草地', value: 'grass_court' },
  { label: '人工合成', value: 'synthetic' },
  { label: '地毯', value: 'carpet' }
]

const courtEnvironmentOptions = [
  { label: '室內', value: 'indoor' },
  { label: '室外', value: 'outdoor' }
]

const timeSlotOptions = [
  { label: '早上', value: 'morning' },
  { label: '下午', value: 'afternoon' },
  { label: '晚上', value: 'evening' }
]

// 賽制與最大局數的對應配置
const matchFormatConfig = {
  games_5: { maxGames: 5, display: '五局制' },
  games_7: { maxGames: 7, display: '七局制' },
  games_9: { maxGames: 9, display: '九局制' }
}

// 6. 輔助函數 (Helper Functions) - 🔥 移除所有 .value
const processGameScore = (score) => {
  if (score === null || score === undefined || score === '') {
    return 0
  }
  const numScore = Number(score)
  return isNaN(numScore) ? 0 : Math.max(0, numScore)
}

const getTiebreakGames = () => {
  const format = matchForm.match_format
  if (format === 'games_5') return ['第5局']
  if (format === 'games_7') return ['第7局']
  if (format === 'games_9') return ['第9局']
  return []
}

const getGameServeTeam = gameNum => {
  if (!matchForm.first_serve_side) return null

  if (gameNum % 2 === 1) {
    return matchForm.first_serve_side
  } else {
    return matchForm.first_serve_side === 'side_a' ? 'side_b' : 'side_a'
  }
}

const isATeamServing = gameNum => {
  return getGameServeTeam(gameNum) === 'side_a'
}

const isBTeamServing = gameNum => {
  return getGameServeTeam(gameNum) === 'side_b'
}

const isTiebreakGame = gameNum => {
  const format = matchForm.match_format
  if (format === 'games_5' && gameNum === 5) return true
  if (format === 'games_7' && gameNum === 7) return true
  if (format === 'games_9' && gameNum === 9) return true
  return false
}

const isGameDisabled = gameNum => {
  return matchCompleted.value && !isGameCompleted(gameNum)
}

const isGameCompleted = gameNum => {
  const aScore = matchForm[`game${gameNum}_a_score`] || 0
  const bScore = matchForm[`game${gameNum}_b_score`] || 0

  if (aScore === 0 && bScore === 0) return false

  const validation = validateSoftTennisScore(aScore, bScore, gameNum)
  return validation.gameFinished
}

const getGameResult = gameNum => {
  const aScore = matchForm[`game${gameNum}_a_score`] || 0
  const bScore = matchForm[`game${gameNum}_b_score`] || 0

  const validation = validateSoftTennisScore(aScore, bScore, gameNum)

  if (validation.gameFinished && validation.winner) {
    return validation.winner === 'A' ? 'A勝' : 'B勝'
  }

  return '進行中'
}

const getGameStatus = gameNum => {
  const aScore = matchForm[`game${gameNum}_a_score`] || 0
  const bScore = matchForm[`game${gameNum}_b_score`] || 0

  if (aScore === 0 && bScore === 0) {
    const isTiebreak = isTiebreakGame(gameNum)
    return {
      status: 'not_started',
      message: isTiebreak ? '未開始 (Tiebreak)' : '未開始'
    }
  }

  const validation = validateSoftTennisScore(aScore, bScore, gameNum)

  if (!validation.isValid) {
    return { status: 'invalid', message: validation.message }
  }

  if (validation.gameFinished) {
    const winner = validation.winner === 'A' ? 'A方' : 'B方'
    const isTiebreak = isTiebreakGame(gameNum)
    return {
      status: 'finished',
      message: isTiebreak ? `${winner}獲勝 (Tiebreak)` : `${winner}獲勝`
    }
  }

  const minScore = Math.min(aScore, bScore)
  const maxScore = Math.max(aScore, bScore)
  const scoreDiff = Math.abs(aScore - bScore)
  const isTiebreak = isTiebreakGame(gameNum)

  if (isTiebreak) {
    if (minScore < 6) {
      if (maxScore === 6) {
        return { status: 'close', message: 'Tiebreak 接近勝負點' }
      }
      return { status: 'in_progress', message: 'Tiebreak 進行中' }
    } else {
      if (scoreDiff === 0) {
        return { status: 'deuce', message: `${minScore}:${minScore} Tiebreak平分` }
      } else if (scoreDiff === 1) {
        const leader = aScore > bScore ? 'A方' : 'B方'
        return { status: 'advantage', message: `${leader}Tiebreak領先` }
      }
    }
  } else {
    if (minScore < 3) {
      if (maxScore === 3) {
        return { status: 'close', message: '接近勝負點' }
      }
      return { status: 'in_progress', message: '進行中' }
    } else {
      if (scoreDiff === 0) {
        return { status: 'deuce', message: `${minScore}:${minScore} 平分` }
      } else if (scoreDiff === 1) {
        const leader = aScore > bScore ? 'A方' : 'B方'
        return { status: 'advantage', message: `${leader}領先` }
      }
    }
  }

  return { status: 'in_progress', message: '進行中' }
}

// 驗證函數保持不變
const validateSoftTennisScore = (aScore, bScore, gameNum = null) => {
  if (aScore < 0 || bScore < 0) {
    return { isValid: false, message: '分數不能為負數' }
  }
  if (aScore > 50 || bScore > 50) {
    return { isValid: false, message: '分數過高，請檢查輸入' }
  }

  if (aScore === 0 && bScore === 0) {
    return { isValid: true, message: '', gameFinished: false, winner: null }
  }

  const isTiebreak = gameNum && isTiebreakGame(gameNum)

  if (isTiebreak) {
    return validateTiebreakScore(aScore, bScore)
  } else {
    return validateRegularGameScore(aScore, bScore)
  }
}

const validateTiebreakScore = (aScore, bScore) => {
  const minScore = Math.min(aScore, bScore)
  const maxScore = Math.max(aScore, bScore)
  const scoreDiff = Math.abs(aScore - bScore)

  if (minScore < 6) {
    if (maxScore >= 7 && scoreDiff >= 1) {
      const winner = aScore > bScore ? 'A' : 'B'
      return { isValid: true, message: '', gameFinished: true, winner }
    }
    if (maxScore >= 7 && scoreDiff < 1) {
      return { isValid: false, message: '分數已達到勝負點但未拉開差距，無效' }
    }
    return { isValid: true, message: '', gameFinished: false, winner: null }
  }

  if (minScore >= 6) {
    if (scoreDiff >= 2) {
      const winner = aScore > bScore ? 'A' : 'B'
      return { isValid: true, message: '', gameFinished: true, winner }
    }
    return { isValid: true, message: '', gameFinished: false, winner: null }
  }

  return { isValid: true, message: '', gameFinished: false, winner: null }
}

const validateRegularGameScore = (aScore, bScore) => {
  const minScore = Math.min(aScore, bScore)
  const maxScore = Math.max(aScore, bScore)
  const scoreDiff = Math.abs(aScore - bScore)

  if (minScore < 3) {
    if (maxScore >= 4 && scoreDiff >= 1) {
      const winner = aScore > bScore ? 'A' : 'B'
      return { isValid: true, message: '', gameFinished: true, winner }
    }
    if (maxScore >= 4 && scoreDiff < 1) {
      return { isValid: false, message: '分數已達到勝負點但未拉開差距，無效' }
    }
    return { isValid: true, message: '', gameFinished: false, winner: null }
  }

  if (minScore >= 3) {
    if (scoreDiff >= 2) {
      const winner = aScore > bScore ? 'A' : 'B'
      return { isValid: true, message: '', gameFinished: true, winner }
    }
    return { isValid: true, message: '', gameFinished: false, winner: null }
  }

  return { isValid: true, message: '', gameFinished: false, winner: null }
}

const validateMatchScore = (aGames, bGames, format) => {
  const gamesToWin = scoreInputMax.value

  if (aGames < 0 || bGames < 0) {
    return { isValid: false, message: '比賽分數不能為負數' }
  }

  if (aGames === bGames) {
    return { isValid: false, message: '比賽分數不能相同，必須分出勝負' }
  }

  if (aGames < gamesToWin && bGames < gamesToWin) {
    return { isValid: false, message: `比賽尚未結束，需要有一方達到 ${gamesToWin} 局` }
  }

  if (aGames >= gamesToWin && bGames >= gamesToWin) {
    return { isValid: false, message: `無效分數：雙方都達到了獲勝局數 ${gamesToWin}` }
  }

  if (aGames >= gamesToWin && aGames <= bGames) {
    return { isValid: false, message: `無效分數：A方達到 ${gamesToWin} 局但未領先B方` }
  }

  if (bGames >= gamesToWin && bGames <= aGames) {
    return { isValid: false, message: `無效分數：B方達到 ${gamesToWin} 局但未領先A方` }
  }

  return { isValid: true, message: '' }
}

const validateDetailedScoresBeforeSubmit = () => {
  if (!enableDetailedScoring.value) return { isValid: true }

  for (let i = 1; i <= maxGames.value; i++) {
    const aScore = matchForm[`game${i}_a_score`] || 0
    const bScore = matchForm[`game${i}_b_score`] || 0

    if (aScore > 0 || bScore > 0) {
      const validation = validateSoftTennisScore(aScore, bScore, i)
      if (!validation.isValid) {
        const gameType = isTiebreakGame(i) ? 'Tiebreak局' : '局'
        return {
          isValid: false,
          message: `第${i}${gameType}分數無效: ${validation.message}`
        }
      }
    }
  }
  return { isValid: true }
}

const resetGameScore = gameNum => {
  matchForm[`game${gameNum}_a_score`] = 0
  matchForm[`game${gameNum}_b_score`] = 0
  updateGameStatistics()
  message.info(`第${gameNum}局比分已重置`)
}

const updateGameStatistics = () => {
  // 🔥 如果正在加載數據，不執行統計更新
  if (!enableDetailedScoring.value || isLoadingData.value) return

  let aWins = 0
  let bWins = 0

  for (let i = 1; i <= maxGames.value; i++) {
    const aScore = matchForm[`game${i}_a_score`] || 0
    const bScore = matchForm[`game${i}_b_score`] || 0

    if (aScore > 0 || bScore > 0) {
      const validation = validateSoftTennisScore(aScore, bScore, i)

      if (validation.gameFinished && validation.winner) {
        if (validation.winner === 'A') {
          aWins++
        } else {
          bWins++
        }
      }
    }
  }

  // 只在數據不是從服務器加載時才更新
  matchForm.a_games = aWins
  matchForm.b_games = bWins
}

const getGameTitle = gameNum => {
  return isTiebreakGame(gameNum) ? `第${gameNum}局 (Tiebreak)` : `第${gameNum}局`
}

const getMatchWinner = () => {
  if (detailedStats.value.aWins >= gamesToWin.value) return 'A方'
  if (detailedStats.value.bWins >= gamesToWin.value) return 'B方'
  return '未決定'
}

const resetDetailedScores = () => {
  for (let i = 1; i <= maxGames.value; i++) {
    matchForm[`game${i}_a_score`] = 0
    matchForm[`game${i}_b_score`] = 0
  }
  matchForm.a_games = 0
  matchForm.b_games = 0
  message.info('詳細比分已重置')
}

const goBack = () => {
  router.push({ name: 'MatchManagement' })
}

// 7. 計算屬性 (Computed Properties) - 🔥 修改相關計算屬性
const maxGames = computed(() => {
  const format = matchForm.match_format
  return format ? matchFormatConfig[format]?.maxGames || 9 : 9
})

const getCardsPerRow = computed(() => {
  if (maxGames.value <= 5) return 5
  if (maxGames.value <= 7) return 7
  return 9
})

const detailedStats = computed(() => {
  let aWins = 0
  let bWins = 0
  let completedGames = 0
  let totalPoints = 0
  let inProgressGames = 0

  for (let i = 1; i <= maxGames.value; i++) {
    const aScore = matchForm[`game${i}_a_score`] || 0
    const bScore = matchForm[`game${i}_b_score`] || 0

    if (aScore > 0 || bScore > 0) {
      totalPoints += aScore + bScore

      const validation = validateSoftTennisScore(aScore, bScore, i)

      if (validation.gameFinished && validation.winner) {
        completedGames++
        if (validation.winner === 'A') {
          aWins++
        } else {
          bWins++
        }
      } else if (validation.isValid) {
        inProgressGames++
      }
    }
  }

  return {
    aWins,
    bWins,
    completedGames,
    totalPoints,
    inProgressGames,
    totalActiveGames: completedGames + inProgressGames
  }
})

const getGameResultType = gameNum => {
  const result = getGameResult(gameNum)
  const status = getGameStatus(gameNum)

  if (status.status === 'invalid') return 'error'
  if (result === 'A勝') return 'success'
  if (result === 'B勝') return 'warning'
  if (status.status === 'deuce') return 'info'
  if (status.status === 'advantage') return 'primary'

  return 'default'
}

const getScoreInputStatus = gameNum => {
  const aScore = matchForm[`game${gameNum}_a_score`] || 0
  const bScore = matchForm[`game${gameNum}_b_score`] || 0

  if (aScore === 0 && bScore === 0) return null

  const validation = validateSoftTennisScore(aScore, bScore, gameNum)

  if (!validation.isValid) {
    return { type: 'error', message: validation.message }
  }

  const status = getGameStatus(gameNum)

  if (status.status === 'finished') {
    return { type: 'success', message: status.message }
  }

  if (status.status === 'deuce' || status.status === 'advantage') {
    return { type: 'warning', message: status.message }
  }

  if (status.status === 'close') {
    return { type: 'info', message: status.message }
  }

  return null
}

const matchCompleted = computed(() => {
  return detailedStats.value.aWins >= gamesToWin.value || detailedStats.value.bWins >= gamesToWin.value
})

const gamesToWin = computed(() => {
  const formatMap = {
    games_5: 3,
    games_7: 4,
    games_9: 5
  }
  return formatMap[matchForm.match_format] || 5
})

const scoreInputMax = computed(() => {
  const formatMap = {
    games_5: 3,
    games_7: 4,
    games_9: 5
  }
  return formatMap[matchForm.match_format] || 5
})

const canSubmit = computed(() => {
  if (!matchForm.player1_id || !matchForm.player3_id) {
    return false
  }

  if (matchForm.match_type === 'doubles' && (!matchForm.player2_id || !matchForm.player4_id)) {
    return false
  }

  const scoreValidation = validateMatchScore(matchForm.a_games, matchForm.b_games, matchForm.match_format)

  return scoreValidation.isValid
})

// 8. 表單驗證規則 (Form Rules) - 🔥 修改驗證規則中的引用
const formRules = {
  match_date: [{ required: true, message: '請選擇比賽日期', trigger: 'change' }],
  match_type: [{ required: true, message: '請選擇比賽類型', trigger: 'change' }],
  match_format: [{ required: true, message: '請選擇賽制', trigger: 'change' }],
  player1_id: [{ required: true, message: '請選擇球員1', trigger: 'change' }],
  player3_id: [{ required: true, message: '請選擇球員3', trigger: 'change' }],
  a_games: [
    { required: true, message: '請輸入A方得分', trigger: 'blur' },
    { type: 'number', min: 0, message: '分數不能為負數', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        const validation = validateMatchScore(value, matchForm.b_games, matchForm.match_format)
        if (!validation.isValid) {
          callback(new Error(validation.message))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  b_games: [
    { required: true, message: '請輸入B方得分', trigger: 'blur' },
    { type: 'number', min: 0, message: '分數不能為負數', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        const validation = validateMatchScore(matchForm.a_games, value, matchForm.match_format)
        if (!validation.isValid) {
          callback(new Error(validation.message))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 載入比賽記錄相關球員的方法 - 保持不變
const loadMatchPlayers = async playerIds => {
  try {
    const validPlayerIds = playerIds.filter(id => id !== null && id !== undefined)

    if (validPlayerIds.length === 0) {
      return
    }

    console.log('載入比賽相關球員:', validPlayerIds)

    const playerPromises = validPlayerIds.map(async playerId => {
      try {
        const response = await apiClient.get(`/members/${playerId}`)
        return response.data.member || response.data
      } catch (error) {
        console.warn(`無法載入球員 ${playerId}:`, error)
        return null
      }
    })

    const players = await Promise.all(playerPromises)
    const validPlayers = players.filter(player => player !== null)

    if (playerSelectorRef.value && validPlayers.length > 0) {
      await nextTick()
      if (typeof playerSelectorRef.value.addPlayersToList === 'function') {
        playerSelectorRef.value.addPlayersToList(validPlayers)
      }
    }
  } catch (error) {
    console.error('載入比賽球員失敗:', error)
  }
}

// 9. 事件處理函數 (Event Handlers) - 🔥 修改所有相關函數
const handleUpdateMatch = async () => {
  try {
    const valid = await formRef.value?.validate()
    if (!valid) {
      message.error('請修正表單中的錯誤。')
      return
    }
  } catch (e) {
    message.error('請修正表單中的錯誤。')
    return
  }

  const localValidation = validateMatchScore(
    matchForm.a_games,
    matchForm.b_games,
    matchForm.match_format
  )

  if (!localValidation.isValid) {
    message.error(localValidation.message)
    return
  }

  submitting.value = true

  try {
    const formatDate = timestamp => {
      if (!timestamp) return null
      const date = new Date(timestamp)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const payload = {
      match_date: formatDate(matchForm.match_date_ts) || matchForm.match_date,
      match_type: matchForm.match_type,
      match_format: matchForm.match_format,
      player1_id: matchForm.player1_id,
      player2_id: matchForm.match_type === 'doubles' ? matchForm.player2_id : null,
      player3_id: matchForm.player3_id,
      player4_id: matchForm.match_type === 'doubles' ? matchForm.player4_id : null,
      a_games: matchForm.a_games,
      b_games: matchForm.b_games,
      match_notes: matchForm.match_notes || null,
      court_surface: matchForm.court_surface || null,
      court_environment: matchForm.court_environment || null,
      time_slot: matchForm.time_slot || null,
      total_points: matchForm.total_points || null,
      duration_minutes: matchForm.duration_minutes || null,
      youtube_url: matchForm.youtube_url || null,
      first_serve_side: matchForm.first_serve_side || null
    }

    // 如果啟用詳細比分，則將每局分數加入 payload
    if (enableDetailedScoring.value) {
      const scoreValidation = validateDetailedScoresBeforeSubmit()
      if (!scoreValidation.isValid) {
        message.error(scoreValidation.message)
        return
      }
      for (let i = 1; i <= maxGames.value; i++) {
        payload[`game${i}_a_score`] = matchForm[`game${i}_a_score`] || 0
        payload[`game${i}_b_score`] = matchForm[`game${i}_b_score`] || 0
      }
    }

    console.log('發送更新請求:', payload)

    const endpoint = enableDetailedScoring.value ? `/match-records/${recordId.value}/detailed` : `/match-records/${recordId.value}`
    const response = await apiClient.put(endpoint, payload)
    console.log('更新響應:', response.data)

    message.success(response.data.message || '比賽記錄已成功更新！')

    setTimeout(() => {
      router.push({ name: 'MatchManagement' })
    }, 1500)
  } catch (err) {
    console.error('更新失敗詳細信息:', {
      error: err,
      response: err.response?.data,
      status: err.response?.status,
      statusText: err.response?.statusText
    })

    const errorData = err.response?.data

    if (errorData?.error === 'score_validation_error') {
      const scoreInfo = errorData.score_info
      let detailedMessage = errorData.message

      if (scoreInfo) {
        detailedMessage += `\n\n詳細信息：`
        detailedMessage += `\nA方得分：${scoreInfo.a_games}`
        detailedMessage += `\nB方得分：${scoreInfo.b_games}`
        detailedMessage += `\n比賽格式：${scoreInfo.match_format}`
        detailedMessage += `\n獲勝需要：${scoreInfo.games_to_win} 局`
      }

      message.error(detailedMessage, {
        duration: 8000,
        closable: true
      })
      return
    }

    let errorMessage = '更新失敗，請稍後再試。'

    if (errorData?.details) {
      errorMessage = '輸入數據有誤：\n' + Object.values(errorData.details).flat().join('\n')
      message.error(errorMessage, { duration: 7000, closable: true })
    } else if (errorData?.message) {
      errorMessage = errorData.message
      message.error(errorMessage)
    } else if (err.response?.status === 404) {
      errorMessage = '找不到要更新的比賽記錄'
      message.error(errorMessage)
    } else if (err.response?.status === 403) {
      errorMessage = '您沒有權限更新此比賽記錄'
      message.error(errorMessage)
    } else {
      message.error(errorMessage)
    }
  } finally {
    submitting.value = false
  }
}

const resetForm = async () => {
  try {
    await fetchMatchRecord()
    message.info('表單已重置為原始數據')
  } catch (error) {
    message.error('重置失敗，請重新載入頁面')
  }
}

const fetchMatchRecord = async () => {
  try {
    loading.value = true
    isLoadingData.value = true // 🔥 標記開始加載數據

    let response
    let record

    response = await apiClient.get(`/match-records/${recordId.value}/detailed`)
    record = response.data.record || response.data

    console.log('🔍 比賽數據', record)
    if (!record) {
      throw new Error('沒有收到比賽記錄數據')
    }

    // 處理日期
    let matchDate = null
    if (record.match_date) {
      try {
        matchDate = new Date(record.match_date).getTime()
        if (isNaN(matchDate)) {
          matchDate = null
        }
      } catch (e) {
        matchDate = null
      }
    }

    // 檢查是否有詳細比分 - 提前檢查
    const hasDetailedScoresFromRecord = Object.keys(record).some(key =>
      key.includes('game') && key.includes('score') && (record[key] || 0) > 0
    )
    const hasServeInfo = !!record.first_serve_side
    const hasDetailedScoresFlag = record.has_detailed_scores
    const shouldEnableDetailedScoring = hasDetailedScoresFromRecord || hasServeInfo || hasDetailedScoresFlag

    console.log('📊 詳細比分檢查結果:', {
      hasDetailedScoresFromRecord,
      hasServeInfo,
      hasDetailedScoresFlag,
      shouldEnableDetailedScoring
    })

    // 🔥 先設置詳細比分狀態，但不觸發統計更新
    if (shouldEnableDetailedScoring) {
      enableDetailedScoring.value = true
      showAdvancedSettings.value = true
    }

    // 🔥 一次性設置所有數據，包括來自服務器的 a_games 和 b_games
    Object.assign(matchForm, {
      match_date_ts: matchDate,
      match_date: record.match_date || '',
      match_type: record.match_type || 'doubles',
      match_format: record.match_format || 'games_9',
      player1_id: record.player1?.id || record.player1_id || null,
      player2_id: record.player2?.id || record.player2_id || null,
      player3_id: record.player3?.id || record.player3_id || null,
      player4_id: record.player4?.id || record.player4_id || null,

      // 🔥 保持服務器返回的總局數，不要立即重新計算
      a_games: record.a_games || 0,
      b_games: record.b_games || 0,

      match_notes: record.match_notes || '',
      court_surface: record.court_surface || null,
      court_environment: record.court_environment || null,
      time_slot: record.time_slot || null,
      total_points: record.total_points || null,
      duration_minutes: record.duration_minutes || null,
      youtube_url: record.youtube_url || '',
      first_serve_side: record.first_serve_side || null,

      // 🔥 局比分數據
      game1_a_score: processGameScore(record.game1_a_score),
      game1_b_score: processGameScore(record.game1_b_score),
      game2_a_score: processGameScore(record.game2_a_score),
      game2_b_score: processGameScore(record.game2_b_score),
      game3_a_score: processGameScore(record.game3_a_score),
      game3_b_score: processGameScore(record.game3_b_score),
      game4_a_score: processGameScore(record.game4_a_score),
      game4_b_score: processGameScore(record.game4_b_score),
      game5_a_score: processGameScore(record.game5_a_score),
      game5_b_score: processGameScore(record.game5_b_score),
      game6_a_score: processGameScore(record.game6_a_score),
      game6_b_score: processGameScore(record.game6_b_score),
      game7_a_score: processGameScore(record.game7_a_score),
      game7_b_score: processGameScore(record.game7_b_score),
      game8_a_score: processGameScore(record.game8_a_score),
      game8_b_score: processGameScore(record.game8_b_score),
      game9_a_score: processGameScore(record.game9_a_score),
      game9_b_score: processGameScore(record.game9_b_score)
    })

    // 🔥 等待 DOM 更新
    await nextTick()

    // 🔥 驗證數據是否正確加載
    console.log('✅ 數據加載完成驗證:')
    console.log('總局數:', { a_games: matchForm.a_games, b_games: matchForm.b_games })

    let foundDetailedScores = false
    for (let i = 1; i <= 9; i++) {
      const aScore = matchForm[`game${i}_a_score`]
      const bScore = matchForm[`game${i}_b_score`]
      if (aScore > 0 || bScore > 0) {
        console.log(`第${i}局: A=${aScore}, B=${bScore}`)
        foundDetailedScores = true
      }
    }

    if (foundDetailedScores) {
      console.log('✅ 詳細比分已正確加載')
    } else {
      console.log('ℹ️ 沒有詳細比分數據')
    }

    // 載入球員信息
    const playerIds = [
      matchForm.player1_id,
      matchForm.player2_id,
      matchForm.player3_id,
      matchForm.player4_id
    ].filter(id => id !== null && id !== undefined)

    if (playerIds.length > 0) {
      await loadMatchPlayers(playerIds)
    }

  } catch (error) {
    console.error('載入比賽記錄失敗:', error)
    const errorMsg = error.response?.data?.message || error.message || '載入比賽記錄失敗'
    message.error(`載入比賽記錄失敗: ${errorMsg}`)

    if (error.response?.status === 404) {
      message.error(`找不到 ID 為 ${recordId.value} 的比賽記錄`)
    }

    setTimeout(() => {
      router.push({ name: 'MatchManagement' })
    }, 2000)
  } finally {
    loading.value = false
    isLoadingData.value = false // 🔥 標記數據加載完成
  }
}


// 10. 監聽器 (Watchers) - 🔥 修改所有相關監聽器
watch(
  () => enableDetailedScoring.value,
  async (newValue, oldValue) => {
    // 🔥 只在用戶手動切換時才重新計算統計
    if (!isLoadingData.value && oldValue !== undefined) {
      console.log('用戶手動切換詳細記錄:', newValue)
      if (newValue) {
        await nextTick()
        updateGameStatistics()
      }
    }
  }
)

watch(
  [() => matchForm.a_games, () => matchForm.b_games, () => matchForm.match_format],
  (newValues, oldValues) => {
    const [newAGames, newBGames, newFormat] = newValues
    const [oldAGames, oldBGames, oldFormat] = oldValues || []

    if (newAGames !== oldAGames || newBGames !== oldBGames || newFormat !== oldFormat) {
      const validation = validateMatchScore(newAGames, newBGames, newFormat)

      const gamesToWin = scoreInputMax.value
      if (newAGames >= gamesToWin && newAGames > newBGames) {
        matchForm.side_a_outcome = 'WIN'
      } else if (newBGames >= gamesToWin && newBGames > newAGames) {
        matchForm.side_a_outcome = 'LOSS'
      } else {
        matchForm.side_a_outcome = 'PENDING'
      }
    }
  },
  { deep: true }
)

watch(
  () => matchForm.match_type,
  newType => {
    if (newType === 'singles') {
      matchForm.player2_id = null
      matchForm.player4_id = null
    }
  }
)

watch(
  () => matchForm.match_format,
  (newFormat, oldFormat) => {
    // 🔥 只在用戶手動變更賽制時才重置
    if (!isLoadingData.value && oldFormat !== undefined && newFormat !== oldFormat) {
      console.log('用戶手動變更賽制:', newFormat)
      for (let i = 1; i <= 9; i++) {
        matchForm[`game${i}_a_score`] = 0
        matchForm[`game${i}_b_score`] = 0
      }
      matchForm.a_games = 0
      matchForm.b_games = 0
      enableDetailedScoring.value = false
      message.info('賽制已變更，詳細比分已重置')
    }
  }
)

watch(
  [
    () => matchForm.player1_id,
    () => matchForm.player2_id,
    () => matchForm.player3_id,
    () => matchForm.player4_id
  ],
  async (newPlayerIds, oldPlayerIds) => {
    const newIds = newPlayerIds.filter((id, index) => id !== oldPlayerIds?.[index] && id !== null)

    if (newIds.length > 0) {
      await loadMatchPlayers(newIds)
    }
  },
  { deep: true }
)

// Lifecycle
onMounted(async () => {
  await fetchMatchRecord()
})
</script>

<style scoped>
  @import '@/assets/css/page/add-match-record-view.css';
</style>