<template>
  <div class="match-score-display-container" :class="{ 'readonly-mode': readOnly }">
    <!-- 基本比分顯示 -->
    <n-card title="比賽分數" size="small" :bordered="false">
      <div class="simplified-score-container">
        <!-- 隊伍A控制 -->
        <div class="team-score-control">
          <div class="team-label-simple">{{ teamAName }}</div>
          <div class="score-buttons" v-if="!readOnly">
            <n-button
              :disabled="!allowScoreAdjustment || modelValue.a_games <= 0"
              circle
              size="small"
              type="error"
              ghost
              @click="adjustScore('a_games', -1)"
            >
              <n-icon :component="MinusIcon" />
            </n-button>
            <n-button
              :disabled="!allowScoreAdjustment || modelValue.a_games >= scoreInputMax"
              circle
              size="small"
              type="primary"
              ghost
              @click="adjustScore('a_games', 1)"
            >
              <n-icon :component="AddIcon" />
            </n-button>
          </div>
        </div>

        <!-- 分數顯示 -->
        <div class="enhanced-score-display">
          <div
            class="score-display-enhanced"
            :class="{ clickable: !readOnly }"
            :title="scoreTooltipText"
            @click="readOnly ? null : showScoreDetails"
          >
            <span class="score-team-a" :class="{ winner: isTeamAWinner }">
              {{ modelValue.a_games || 0 }}
              <span v-if="tiebreakScoreDisplay?.showOnA" class="tiebreak-superscript">
                <sup>{{ tiebreakScoreDisplay.loserScore }}</sup>
              </span>
            </span>
            <span class="score-separator">:</span>
            <span class="score-team-b" :class="{ winner: isTeamBWinner }">
              {{ modelValue.b_games || 0 }}
              <span v-if="tiebreakScoreDisplay?.showOnB" class="tiebreak-superscript">
                <sup>{{ tiebreakScoreDisplay.loserScore }}</sup>
              </span>
            </span>
          </div>
        </div>

        <!-- 隊伍B控制 -->
        <div class="team-score-control">
          <div class="team-label-simple">{{ teamBName }}</div>
          <div class="score-buttons" v-if="!readOnly">
            <n-button
              :disabled="!allowScoreAdjustment || modelValue.b_games <= 0"
              circle
              size="small"
              type="error"
              ghost
              @click="adjustScore('b_games', -1)"
            >
              <n-icon :component="MinusIcon" />
            </n-button>
            <n-button
              :disabled="!allowScoreAdjustment || modelValue.b_games >= scoreInputMax"
              circle
              size="small"
              type="primary"
              ghost
              @click="adjustScore('b_games', 1)"
            >
              <n-icon :component="AddIcon" />
            </n-button>
          </div>
        </div>
      </div>
    </n-card>

    <!-- 詳細設定區塊 -->
    <n-divider style="margin-top: 2rem; margin-bottom: 1rem">
      <n-button
        text
        style="color: #666; font-size: 14px"
        :disabled="mode === 'view'"
        @click="toggleAdvancedSettings"
      >
        <template #icon>
          <n-icon :component="showAdvancedSettings ? ChevronDownIcon : ChevronUpIcon" />
        </template>
        {{ readOnly ? '詳細資訊' : '詳細設定' }}
      </n-button>
    </n-divider>

    <!-- 詳細設定內容 -->
    <div v-show="shouldShowAdvancedSettings" class="advanced-settings-container">
      <div class="detailed-score-section">
        <!-- 控制面板 -->
        <div class="control-panel">
          <div class="serve-selector-buttons">
            <n-form-item label="先發球方" :show-feedback="false" size="small">
              <div class="serve-button-group">
                <n-button
                  :type="modelValue.first_serve_side === 'side_a' ? 'primary' : 'default'"
                  :ghost="modelValue.first_serve_side !== 'side_a'"
                  size="large"
                  class="serve-button"
                  :disabled="readOnly"
                  @click="readOnly ? null : setFirstServe('side_a')"
                >
                  <template #icon>
                    <span class="serve-icon">🎾</span>
                  </template>
                  A方先發
                </n-button>
                <n-button
                  :type="modelValue.first_serve_side === 'side_b' ? 'primary' : 'default'"
                  :ghost="modelValue.first_serve_side !== 'side_b'"
                  size="large"
                  class="serve-button"
                  :disabled="readOnly"
                  @click="readOnly ? null : setFirstServe('side_b')"
                >
                  <template #icon>
                    <span class="serve-icon">🎾</span>
                  </template>
                  B方先發
                </n-button>
              </div>
            </n-form-item>
          </div>
        </div>

        <!-- 紀錄模式 - 直接顯示 -->
        <div class="record-mode">
          <!-- 桌面版：網格佈局 -->
          <div class="desktop-grid">
            <n-grid :x-gap="12" :y-gap="12" :cols="getRecordCardsPerRow">
              <n-grid-item v-for="gameNum in maxGames" :key="gameNum">
                <n-card
                  size="small"
                  class="game-score-card"
                  :class="{
                    'completed-card': isGameCompleted(gameNum),
                    'disabled-card': isGameDisabled(gameNum) || readOnly,
                    'invalid-card': getScoreInputStatus(gameNum)?.type === 'error',
                    'tiebreak-card': isTiebreakGame(gameNum),
                    'winner-a-card': isGameCompleted(gameNum) && getGameWinner(gameNum) === 'A',
                    'winner-b-card': isGameCompleted(gameNum) && getGameWinner(gameNum) === 'B',
                    'readonly-card': readOnly
                  }"
                >
                  <template #header>
                    <div class="card-game-header">
                      <div class="card-title-section">
                        <span>{{ getGameTitle(gameNum) }}</span>
                        <n-tag v-if="isTiebreakGame(gameNum)" type="warning" size="small" round>
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
                      </div>
                    </div>
                  </template>

                  <n-space vertical :size="8">
                    <!-- A方輸入 -->
                    <n-form-item :show-feedback="false" size="small">
                      <template #label>
                        <div class="team-label">
                          <span
                            v-if="isATeamServing(gameNum)"
                            class="serve-icon card-serve-icon"
                            title="A方發球"
                          >🎾</span>
                          <span>A方</span>
                        </div>
                      </template>
                      <n-input-number
                        v-model:value="modelValue[`game${gameNum}_a_score`]"
                        :min="0"
                        :max="getMaxScoreForGame(gameNum, 'a')"
                        :disabled="isGameDisabled(gameNum) || readOnly"
                        :readonly="readOnly"
                        :status="getScoreInputStatus(gameNum)?.type"
                        size="small"
                        style="width: 100%"
                        @update:value="readOnly ? null : updateGameStatistics"
                      />
                    </n-form-item>

                    <!-- B方輸入 -->
                    <n-form-item :show-feedback="false" size="small">
                      <template #label>
                        <div class="team-label">
                          <span
                            v-if="isBTeamServing(gameNum)"
                            class="serve-icon card-serve-icon"
                            title="B方發球"
                          >🎾</span>
                          <span>B方</span>
                        </div>
                      </template>
                      <n-input-number
                        v-model:value="modelValue[`game${gameNum}_b_score`]"
                        :min="0"
                        :max="getMaxScoreForGame(gameNum, 'b')"
                        :disabled="isGameDisabled(gameNum) || readOnly"
                        :readonly="readOnly"
                        :status="getScoreInputStatus(gameNum)?.type"
                        size="small"
                        style="width: 100%"
                        @update:value="readOnly ? null : updateGameStatistics"
                      />
                    </n-form-item>
                  </n-space>
                </n-card>
              </n-grid-item>
            </n-grid>
          </div>

          <!-- 移動版：垂直排列 + 可摺疊 -->
          <div class="mobile-vertical">
            <div v-for="gameNum in maxGames" :key="gameNum" class="mobile-game-item">
              <div
                class="mobile-game-header"
                :class="{
                  'completed-header': isGameCompleted(gameNum),
                  'tiebreak-header': isTiebreakGame(gameNum),
                  'winner-a-header': isGameCompleted(gameNum) && getGameWinner(gameNum) === 'A',
                  'winner-b-header': isGameCompleted(gameNum) && getGameWinner(gameNum) === 'B'
                }"
                @click="toggleMobileGame(gameNum)"
              >
                <div class="mobile-game-title">
                  <span class="game-number">{{ getGameTitle(gameNum) }}</span>
                  <div class="header-tags">
                    <n-tag v-if="isTiebreakGame(gameNum)" type="warning" size="small" round>
                      決勝局
                    </n-tag>
                    <n-tag
                      v-if="isGameCompleted(gameNum)"
                      :type="getGameResultType(gameNum)"
                      size="small"
                      round
                    >
                      {{ getGameResult(gameNum) }}
                    </n-tag>
                  </div>
                </div>
                <div class="header-right">
                  <span v-if="hasGameScore(gameNum)" class="quick-score">
                    {{ modelValue[`game${gameNum}_a_score`] || 0 }}:{{ modelValue[`game${gameNum}_b_score`] || 0 }}
                  </span>
                  <n-icon
                    :component="collapsedGames.includes(gameNum) ? ChevronDownIcon : ChevronUpIcon"
                    class="collapse-icon"
                  />
                </div>
              </div>

              <div v-if="!collapsedGames.includes(gameNum)" class="mobile-game-content">
                <n-card
                  size="small"
                  class="mobile-card"
                  :class="{
                    'completed-card': isGameCompleted(gameNum),
                    'disabled-card': isGameDisabled(gameNum) || readOnly,
                    'invalid-card': getScoreInputStatus(gameNum)?.type === 'error',
                    'tiebreak-card': isTiebreakGame(gameNum),
                    'winner-a-card': isGameCompleted(gameNum) && getGameWinner(gameNum) === 'A',
                    'winner-b-card': isGameCompleted(gameNum) && getGameWinner(gameNum) === 'B',
                    'readonly-card': readOnly
                  }"
                >
                  <n-space vertical :size="8">
                    <n-form-item :show-feedback="false" size="small">
                      <template #label>
                        <div class="team-label">
                          <span
                            v-if="isATeamServing(gameNum)"
                            class="serve-icon card-serve-icon"
                            title="A方發球"
                          >🎾</span>
                          <span>A方</span>
                        </div>
                      </template>
                      <n-input-number
                        v-model:value="modelValue[`game${gameNum}_a_score`]"
                        :min="0"
                        :max="getMaxScoreForGame(gameNum, 'a')"
                        :disabled="isGameDisabled(gameNum) || readOnly"
                        :readonly="readOnly"
                        :status="getScoreInputStatus(gameNum)?.type"
                        size="small"
                        style="width: 100%"
                        @update:value="readOnly ? null : updateGameStatistics"
                      />
                    </n-form-item>

                    <n-form-item :show-feedback="false" size="small">
                      <template #label>
                        <div class="team-label">
                          <span
                            v-if="isBTeamServing(gameNum)"
                            class="serve-icon card-serve-icon"
                            title="B方發球"
                          >🎾</span>
                          <span>B方</span>
                        </div>
                      </template>
                      <n-input-number
                        v-model:value="modelValue[`game${gameNum}_b_score`]"
                        :min="0"
                        :max="getMaxScoreForGame(gameNum, 'b')"
                        :disabled="isGameDisabled(gameNum) || readOnly"
                        :readonly="readOnly"
                        :status="getScoreInputStatus(gameNum)?.type"
                        size="small"
                        style="width: 100%"
                        @update:value="readOnly ? null : updateGameStatistics"
                      />
                    </n-form-item>
                  </n-space>
                </n-card>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 詳細比分彈窗 -->
    <n-modal
      v-model:show="showScoreModal"
      preset="card"
      title="詳細比分"
      style="width: 90%; max-width: 600px"
      :mask-closable="true"
    >
      <div class="score-modal-content">
        <div v-if="hasDetailedScoreDataModal" class="detailed-scores-grid">
          <div
            v-for="gameNum in maxGames"
            :key="gameNum"
            class="score-game-card"
            :class="{
              'tiebreak-card': isTiebreakGame(gameNum),
              'completed-card': isGameCompleted(gameNum),
              'winner-a-card': getGameWinner(gameNum) === 'A',
              'winner-b-card': getGameWinner(gameNum) === 'B'
            }"
          >
            <div class="game-header">
              <span class="game-title">第{{ gameNum }}局</span>
              <span v-if="isTiebreakGame(gameNum)" class="tiebreak-badge"> 決勝局 </span>
            </div>

            <div class="game-score-display">
              <template v-if="hasGameScore(gameNum)">
                <span class="team-score team-a">{{ getGameScore(gameNum).aScore }}</span>
                <span class="score-sep">:</span>
                <span class="team-score team-b">{{ getGameScore(gameNum).bScore }}</span>
              </template>
              <span v-else class="no-score">未進行</span>
            </div>

            <div v-if="isGameCompleted(gameNum)" class="game-result" :class="{ 'result-a': getGameWinner(gameNum) === 'A', 'result-b': getGameWinner(gameNum) === 'B' }">
              {{ getGameWinner(gameNum) === 'A' ? 'A方獲勝' : 'B方獲勝' }}
            </div>

            <div v-else-if="hasGameScore(gameNum)" class="game-status">進行中</div>
          </div>
        </div>

        <div v-else class="no-detailed-data">
          <div class="empty-icon">📊</div>
          <h3>暫無詳細比分</h3>
          <p>此比賽未記錄詳細的局比分數據</p>
        </div>
      </div>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showScoreModal = false">關閉</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick, onMounted } from 'vue'
import { useMessage, NStatistic, NGrid, NDivider, NText } from 'naive-ui'

import {
  AddOutline as AddIcon,
  CheckmarkCircleOutline as CheckmarkCircleIcon,
  RemoveOutline as MinusIcon,
  InformationCircleOutline as InfoIcon,
  ChevronUpOutline as ChevronUpIcon,
  ChevronDownOutline as ChevronDownIcon,
  LockClosedOutline
} from '@vicons/ionicons5'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  teamAName: {
    type: String,
    default: '隊伍 A'
  },
  teamBName: {
    type: String,
    default: '隊伍 B'
  },
  allowScoreAdjustment: {
    type: Boolean,
    default: true
  },
  readOnly: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'add',
    validator: value => ['add', 'edit', 'view'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'score-changed', 'match-completed'])

const message = useMessage()
const showAdvancedSettings = ref(false)
const showScoreModal = ref(false)
const collapsedGames = ref([])

// 計算屬性
const maxGames = computed(() => {
  const format = props.modelValue.match_format
  const matchFormatConfig = {
    games_5: { maxGames: 5 },
    games_7: { maxGames: 7 },
    games_9: { maxGames: 9 }
  }
  return format ? matchFormatConfig[format]?.maxGames || 9 : 9
})

const scoreInputMax = computed(() => {
  const formatMap = {
    games_5: 3,
    games_7: 4,
    games_9: 5
  }
  return formatMap[props.modelValue.match_format] || 5
})

const gamesToWin = computed(() => scoreInputMax.value)

const isTeamAWinner = computed(() => {
  const aGames = props.modelValue.a_games || 0
  const bGames = props.modelValue.b_games || 0
  return aGames >= gamesToWin.value && aGames > bGames
})

const isTeamBWinner = computed(() => {
  const aGames = props.modelValue.a_games || 0
  const bGames = props.modelValue.b_games || 0
  return bGames >= gamesToWin.value && bGames > aGames
})

const matchCompleted = computed(() => {
  return detailedStats.value.aWins >= gamesToWin.value || detailedStats.value.bWins >= gamesToWin.value
})

const getRecordCardsPerRow = computed(() => {
  return 5
})

const shouldShowAdvancedSettings = computed(() => {
  if (props.readOnly || props.mode === 'view') {
    return true
  }
  return showAdvancedSettings.value
})

// 檢測詳細比分數據
const hasDetailedScoreData = computed(() => {
  for (let i = 1; i <= maxGames.value; i++) {
    const aScore = props.modelValue[`game${i}_a_score`] || 0
    const bScore = props.modelValue[`game${i}_b_score`] || 0
    if (aScore > 0 || bScore > 0) {
      return true
    }
  }
  return false
})

const hasDetailedScoreDataModal = computed(() => hasDetailedScoreData.value)

// 動態計算每局比分的最大值
const getMaxScoreForGame = computed(() => {
  return (gameNum, side) => {
    // 如果是決勝局，使用決勝局規則
    if (isTiebreakGame(gameNum)) {
      return 50 // 決勝局無上限
    }

    const aScore = props.modelValue[`game${gameNum}_a_score`] || 0
    const bScore = props.modelValue[`game${gameNum}_b_score`] || 0

    // 當前方分數和對方分數
    const currentScore = side === 'a' ? aScore : bScore
    const opponentScore = side === 'a' ? bScore : aScore

    // 軟式網球規則：
    // 1. 如果對方分數 < 3，最高只能到 4 分
    // 2. 如果對方分數 >= 3，無上限（但設置合理上限）
    if (opponentScore < 3) {
      return 4
    } else {
      return 50 // 3:3 後無上限
    }
  }
})

const getServeLabel = computed(() => {
  if (!props.modelValue.first_serve_side) return '先發'
  return props.modelValue.first_serve_side === 'side_a' ? 'A先發' : 'B先發'
})

const getServeValue = computed(() => {
  if (!props.modelValue.first_serve_side) return '?'
  return props.modelValue.first_serve_side === 'side_a' ? '🏓 A' : '🏓 B'
})

const tiebreakScoreDisplay = computed(() => {
  const tiebreakGame = getTiebreakGameNumber()
  if (!tiebreakGame || !isGameCompleted(tiebreakGame)) {
    return null
  }

  const aScore = props.modelValue[`game${tiebreakGame}_a_score`] || 0
  const bScore = props.modelValue[`game${tiebreakGame}_b_score`] || 0

  const tiebreakWinner = aScore > bScore ? 'A' : 'B'
  const loserScore = tiebreakWinner === 'A' ? bScore : aScore

  return {
    aScore,
    bScore,
    loserScore,
    winner: tiebreakWinner,
    showOnA: tiebreakWinner === 'B',
    showOnB: tiebreakWinner === 'A'
  }
})

const scoreTooltipText = computed(() => {
  if (props.readOnly) {
    return '詳細比分資訊（只讀模式）'
  }
  if (!hasDetailedScoreData.value) {
    return '點擊查看詳細比分'
  }
  return '點擊查看詳細比分記錄'
})

// 詳細統計
const detailedStats = computed(() => {
  let aWins = 0
  let bWins = 0
  let completedGames = 0
  let totalPoints = 0
  let inProgressGames = 0

  for (let i = 1; i <= maxGames.value; i++) {
    const aScore = props.modelValue[`game${i}_a_score`] || 0
    const bScore = props.modelValue[`game${i}_b_score`] || 0

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

// 輔助函數
const getTiebreakGameNumber = () => {
  const format = props.modelValue.match_format
  if (format === 'games_5') return 5
  if (format === 'games_7') return 7
  if (format === 'games_9') return 9
  return null
}

const isTiebreakGame = (gameNum) => {
  const format = props.modelValue.match_format
  if (format === 'games_5' && gameNum === 5) return true
  if (format === 'games_7' && gameNum === 7) return true
  if (format === 'games_9' && gameNum === 9) return true
  return false
}

const getGameServeTeam = (gameNum) => {
  if (!props.modelValue.first_serve_side) return null

  if (gameNum % 2 === 1) {
    return props.modelValue.first_serve_side
  } else {
    return props.modelValue.first_serve_side === 'side_a' ? 'side_b' : 'side_a'
  }
}

const isATeamServing = (gameNum) => {
  return getGameServeTeam(gameNum) === 'side_a'
}

const isBTeamServing = (gameNum) => {
  return getGameServeTeam(gameNum) === 'side_b'
}

const isGameCompleted = (gameNum) => {
  const aScore = props.modelValue[`game${gameNum}_a_score`] || 0
  const bScore = props.modelValue[`game${gameNum}_b_score`] || 0

  if (aScore === 0 && bScore === 0) return false

  const validation = validateSoftTennisScore(aScore, bScore, gameNum)
  return validation.gameFinished
}

const isGameDisabled = (gameNum) => {
  return matchCompleted.value && !isGameCompleted(gameNum)
}

const getGameResult = (gameNum) => {
  const aScore = props.modelValue[`game${gameNum}_a_score`] || 0
  const bScore = props.modelValue[`game${gameNum}_b_score`] || 0

  const validation = validateSoftTennisScore(aScore, bScore, gameNum)

  if (validation.gameFinished && validation.winner) {
    return validation.winner === 'A' ? 'A勝' : 'B勝'
  }

  return '進行中'
}

const getGameWinner = (gameNum) => {
  if (!isGameCompleted(gameNum)) return null

  const aScore = props.modelValue[`game${gameNum}_a_score`] || 0
  const bScore = props.modelValue[`game${gameNum}_b_score`] || 0

  return aScore > bScore ? 'A' : 'B'
}

const hasGameScore = (gameNum) => {
  const aScore = props.modelValue[`game${gameNum}_a_score`] || 0
  const bScore = props.modelValue[`game${gameNum}_b_score`] || 0
  return aScore > 0 || bScore > 0
}

const getGameScore = (gameNum) => {
  const aScore = props.modelValue[`game${gameNum}_a_score`] || 0
  const bScore = props.modelValue[`game${gameNum}_b_score`] || 0
  return { aScore, bScore }
}

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

  if (maxScore >= 4 && minScore < 3) {
    const winner = aScore > bScore ? 'A' : 'B'
    return { isValid: true, message: '', gameFinished: true, winner }
  }

  if (maxScore < 4) {
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

const getGameResultType = (gameNum) => {
  const result = getGameResult(gameNum)

  if (result === 'A勝') return 'success'
  if (result === 'B勝') return 'warning'

  return 'default'
}

const getScoreInputStatus = (gameNum) => {
  const aScore = props.modelValue[`game${gameNum}_a_score`] || 0
  const bScore = props.modelValue[`game${gameNum}_b_score`] || 0

  if (aScore === 0 && bScore === 0) return null

  const validation = validateSoftTennisScore(aScore, bScore, gameNum)

  if (!validation.isValid) {
    return { type: 'error', message: validation.message }
  }

  if (validation.gameFinished) {
    return { type: 'success', message: getGameResult(gameNum) }
  }

  return null
}

const getGameTitle = (gameNum) => {
  return isTiebreakGame(gameNum) ? `Tiebreak` : `第${gameNum}局`
}

// 同步詳細比分到總比分
const syncDetailedScores = () => {
  let aWins = 0
  let bWins = 0

  for (let i = 1; i <= maxGames.value; i++) {
    const aScore = props.modelValue[`game${i}_a_score`] || 0
    const bScore = props.modelValue[`game${i}_b_score`] || 0

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

  // 只在分數不同時才更新，避免無限循環
  if (props.modelValue.a_games !== aWins || props.modelValue.b_games !== bWins) {
    const updatedValue = {
      ...props.modelValue,
      a_games: aWins,
      b_games: bWins
    }
    emit('update:modelValue', updatedValue)
  }
}

// 主要方法
const toggleAdvancedSettings = () => {
  if (props.readOnly) return

  showAdvancedSettings.value = !showAdvancedSettings.value
}

const setFirstServe = (side) => {
  if (props.readOnly) return

  const updatedValue = { ...props.modelValue, first_serve_side: side }
  emit('update:modelValue', updatedValue)
}

const toggleMobileGame = (gameNum) => {
  const index = collapsedGames.value.indexOf(gameNum)
  if (index > -1) {
    collapsedGames.value.splice(index, 1)
  } else {
    collapsedGames.value.push(gameNum)
  }
}

const adjustScore = (field, delta) => {
  if (props.readOnly || !props.allowScoreAdjustment) return

  const currentValue = props.modelValue[field] || 0
  const newValue = currentValue + delta

  if (newValue >= 0 && newValue <= scoreInputMax.value) {
    const updatedValue = { ...props.modelValue, [field]: newValue }
    emit('update:modelValue', updatedValue)
    emit('score-changed', { field, oldValue: currentValue, newValue, delta })

    if (hasDetailedScoreData.value && delta !== 0) {
      message.warning('手動調整總分可能與詳細比分不一致')
    }
  }
}

const updateGameStatistics = () => {
  if (props.readOnly) return

  let aWins = 0
  let bWins = 0
  let hasInvalidScore = false
  let invalidMessage = ''

  for (let i = 1; i <= maxGames.value; i++) {
    const aScore = props.modelValue[`game${i}_a_score`] || 0
    const bScore = props.modelValue[`game${i}_b_score`] || 0

    if (aScore > 0 || bScore > 0) {
      const validation = validateSoftTennisScore(aScore, bScore, i)

      if (!validation.isValid) {
        hasInvalidScore = true
        const gameType = isTiebreakGame(i) ? 'Tiebreak局' : '局'
        invalidMessage = `第${i}${gameType}: ${validation.message}`
        break
      }

      if (validation.gameFinished && validation.winner) {
        if (validation.winner === 'A') {
          aWins++
        } else {
          bWins++
        }
      }
    }
  }

  if (hasInvalidScore) {
    message.error(invalidMessage, { duration: 5000 })
    return
  }

  const updatedValue = {
    ...props.modelValue,
    a_games: aWins,
    b_games: bWins
  }

  emit('update:modelValue', updatedValue)

  if (matchCompleted.value && (aWins > 0 || bWins > 0)) {
    const winner = aWins >= gamesToWin.value ? props.teamAName : props.teamBName
    message.success(`${winner} 獲勝！`, { duration: 3000 })
    emit('match-completed', { winner })
  }
}

const showScoreDetails = () => {
  if (hasDetailedScoreData.value) {
    showScoreModal.value = true
  } else {
    if (!props.readOnly) {
      message.info('無詳細比分記錄')
    }
  }
}

// 監聽器
watch(
  () => props.modelValue.match_format,
  (newFormat) => {
    if (newFormat && !props.readOnly) {
      const updatedValue = { ...props.modelValue }

      for (let i = 1; i <= 9; i++) {
        updatedValue[`game${i}_a_score`] = 0
        updatedValue[`game${i}_b_score`] = 0
      }

      collapsedGames.value = []
      emit('update:modelValue', updatedValue)
      message.info('賽制已變更，比分已重置')
    }
  }
)

// 監聽 modelValue 變化並自動同步
watch(
  () => props.modelValue,
  () => {
    if (hasDetailedScoreData.value) {
      nextTick(() => {
        syncDetailedScores()
      })
    }
  },
  { deep: true, immediate: false }
)

// 模式初始化
watch(
  () => [props.readOnly, props.mode],
  ([newReadOnly, newMode]) => {
    if (newReadOnly || newMode === 'view') {
      showAdvancedSettings.value = true
    } else if (newMode === 'edit') {
      showAdvancedSettings.value = true
    } else if (newMode === 'add') {
      showAdvancedSettings.value = false
    }
  },
  { immediate: true, flush: 'post' }
)

defineExpose({
  resetComponentState: () => {
    showAdvancedSettings.value = false
    showScoreModal.value = false
    collapsedGames.value = []
  },
  resetScores: () => {
    if (props.readOnly) return

    const updatedValue = { ...props.modelValue }
    for (let i = 1; i <= maxGames.value; i++) {
      updatedValue[`game${i}_a_score`] = 0
      updatedValue[`game${i}_b_score`] = 0
    }
    updatedValue.a_games = 0
    updatedValue.b_games = 0
    emit('update:modelValue', updatedValue)

    showAdvancedSettings.value = false
    collapsedGames.value = []
    message.info('已重置')
  },
  syncDetailedScores
})
</script>

<style scoped>
@import "@/assets/css/components/match/match-score-display.css";

/* 只讀模式樣式 */
.match-score-display-container.readonly-mode {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1rem;
  border: 2px solid #e9ecef;
}

.readonly-mode .score-buttons {
  display: none;
}

.readonly-mode .score-display-enhanced {
  cursor: default !important;
}

.readonly-mode .score-display-enhanced.clickable {
  cursor: default !important;
}

.readonly-mode .serve-button[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

.readonly-mode .game-score-card.readonly-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
}

.readonly-mode .game-score-card.readonly-card :deep(.n-input-number.n-input-number--disabled) {
  background-color: #f8f9fa !important;
  border-color: #dee2e6 !important;
  cursor: default !important;
}

.readonly-mode .game-score-card.readonly-card :deep(.n-input__input-el[disabled]) {
  color: #495057 !important;
  background-color: #f8f9fa !important;
}

.readonly-mode .card-game-header {
  background: linear-gradient(135deg, #f1f3f5 0%, #e9ecef 100%);
  padding: 0.5rem;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.readonly-mode .real-time-statistics {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

.readonly-mode::before {
  content: '📖 比賽資料檢視模式';
  display: block;
  text-align: center;
  font-size: 0.875rem;
  color: #6c757d;
  background: #e9ecef;
  padding: 0.5rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-weight: 500;
}
</style>