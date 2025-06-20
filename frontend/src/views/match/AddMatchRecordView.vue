<template>
  <div class="record-match-page container-fluid mt-4 mb-5 px-md-4">
    <n-card :bordered="false" class="form-card">
      <!-- 頁面標題 -->
      <div class="page-header mb-4">
        <n-button quaternary circle style="margin-right: 1rem" @click="goBack">
          <template #icon>
            <n-icon :component="ArrowLeftIcon" />
          </template>
        </n-button>
        <h1 class="page-title">記錄新比賽</h1>
      </div>

      <!-- 表單內容 -->
      <n-form
        ref="formRef"
        :model="matchForm"
        :rules="formRules"
        label-placement="top"
        @submit.prevent="handleRecordMatch"
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

        <MatchPlayerSelector v-model="matchForm" />

        <!-- 可折疊的詳細設定區塊 -->
        <n-divider style="margin-top: 2rem; margin-bottom: 1rem">
          <n-button text style="color: #666; font-size: 14px" @click="showAdvancedSettings = !showAdvancedSettings">
            <template #icon>
              <n-icon :component="showAdvancedSettings ? ChevronUpIcon : ChevronDownIcon" />
            </template>
            詳細設定 (選填)
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
                    <!-- 🆕 先發球選擇和顯示模式選擇 -->
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
                            <!-- 🔧 移除標題欄的網球icon -->
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
                                  <n-tag type="warning" size="tiny" round>決勝局</n-tag>
                                </div>
                              </div>
                            </td>
                            <!-- 🆕 A方得分含動態發球顯示 -->
                            <td style="text-align: center">
                              <div class="score-input-container">
                                <!-- 🎾 網球icon顯示在輸入框前 -->
                                <span v-if="isATeamServing(gameNum)" class="serve-icon table-serve-icon" title="A方發球"
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
                            <!-- 🆕 B方得分含動態發球顯示 -->
                            <td style="text-align: center">
                              <div class="score-input-container">
                                <!-- 🎾 網球icon顯示在輸入框前 -->
                                <span v-if="isBTeamServing(gameNum)" class="serve-icon table-serve-icon" title="B方發球"
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
                                    size="tiny"
                                    round
                                  >
                                    {{ getGameResult(gameNum) }}
                                  </n-tag>
                                  <n-tag
                                    v-else-if="getScoreInputStatus(gameNum)"
                                    :type="getScoreInputStatus(gameNum).type"
                                    size="tiny"
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
                              <!-- 🆕 A方輸入含動態發球顯示 -->
                              <n-form-item :show-feedback="false" size="small">
                                <template #label>
                                  <div class="team-label">
                                    <!-- 🎾 卡片模式：網球icon顯示在標籤前 -->
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

                              <!-- 🆕 B方輸入含動態發球顯示 -->
                              <n-form-item :show-feedback="false" size="small">
                                <template #label>
                                  <div class="team-label">
                                    <!-- 🎾 卡片模式：網球icon顯示在標籤前 -->
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

                    <!-- 🆕 計分規則說明（更新版） -->
                    <!--<div class="scoring-rules-info">-->
                    <!--  <n-collapse>-->
                    <!--    <n-collapse-item title="軟網計分規則" name="rules">-->
                    <!--      <div class="rules-content">-->
                    <!--        <n-tabs type="segment" size="small">-->
                    <!--          <n-tab-pane name="regular" tab="一般局">-->
                    <!--            <n-ul>-->
                    <!--              <n-li><strong>基本規則：</strong>先達到4分且領先對手至少1分即獲勝該局</n-li>-->
                    <!--              <n-li><strong>平分規則：</strong>如果出現3:3平分，需要領先2分才能獲勝</n-li>-->
                    <!--              <n-li><strong>示例：</strong>4:1, 4:2, 4:3 → A方獲勝</n-li>-->
                    <!--              <n-li><strong>加時示例：</strong>3:3 → 5:3, 6:4, 7:5 → 領先方獲勝</n-li>-->
                    <!--            </n-ul>-->
                    <!--          </n-tab-pane>-->
                    <!--          <n-tab-pane name="tiebreak" tab="決勝局 (Tiebreak)">-->
                    <!--            <n-ul>-->
                    <!--              <n-li><strong>適用局數：</strong>{{ getTiebreakGames().join('、') }}</n-li>-->
                    <!--              <n-li><strong>基本規則：</strong>先達到7分且領先對手至少1分即獲勝該局</n-li>-->
                    <!--              <n-li><strong>平分規則：</strong>如果出現6:6平分，需要領先2分才能獲勝</n-li>-->
                    <!--              <n-li><strong>示例：</strong>7:1, 7:5, 7:6 → A方獲勝</n-li>-->
                    <!--              <n-li><strong>加時示例：</strong>6:6 → 8:6, 9:7, 10:8 → 領先方獲勝</n-li>-->
                    <!--            </n-ul>-->
                    <!--          </n-tab-pane>-->
                    <!--        </n-tabs>-->
                    <!--      </div>-->
                    <!--    </n-collapse-item>-->
                    <!--  </n-collapse>-->
                    <!--</div>-->

                    <!--        &lt;!&ndash; 🆕 發球輪換顯示說明 &ndash;&gt;-->
                    <!--<div v-if="matchForm.first_serve_side" class="serve-rotation-info">-->
                    <!--  <n-alert type="info" :show-icon="false" style="margin-top: 1rem">-->
                    <!--    <template #icon>-->
                    <!--      <span class="serve-icon">🎾</span>-->
                    <!--    </template>-->
                    <!--    <div class="serve-info-content">-->
                    <!--      <strong>發球輪換：</strong>-->
                    <!--      <span v-if="matchForm.first_serve_side === 'side_a'">-->
                    <!--        A方先發球 → 奇數局(1,3,5,7,9)A方發球，偶數局(2,4,6,8)B方發球-->
                    <!--      </span>-->
                    <!--      <span v-else>-->
                    <!--        B方先發球 → 奇數局(1,3,5,7,9)B方發球，偶數局(2,4,6,8)A方發球-->
                    <!--      </span>-->
                    <!--    </div>-->
                    <!--  </n-alert>-->
                    <!--</div>-->

                    <!-- 🔧 修改即時統計 -->
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
                        <!-- 🆕 進行中局數 -->
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
            <n-button size="large" @click="resetForm">
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              重置
            </n-button>
            <n-button
              type="primary"
              size="large"
              :loading="submitting"
              :disabled="!canSubmit"
              @click="handleRecordMatch"
            >
              <template #icon>
                <n-icon :component="SaveIcon" />
              </template>
              儲存比賽結果
            </n-button>
          </n-space>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
  // 1. 引入 (Imports)
  // 引入 Vue 核心功能：計算屬性、響應式數據、監聽器
  import { computed, ref, watch } from 'vue'
  // 引入 Vue Router 用於導航
  import { useRouter } from 'vue-router'
  // 引入 Naive UI 的消息提示組件
  import { useMessage } from 'naive-ui'
  // 引入自定義的 API 客戶端服務
  import apiClient from '@/services/apiClient'
  // 引入自定義的球員選擇器組件
  import MatchPlayerSelector from '@/components/MatchPlayerSelector.vue'

  // 引入 Naive UI 的圖標 (Icons)
  import {
    ArrowBackOutline as ArrowLeftIcon, // 返回箭頭
    ChevronDownOutline as ChevronDownIcon, // 向下箭頭
    ChevronUpOutline as ChevronUpIcon, // 向上箭頭
    RefreshOutline as RefreshIcon, // 刷新圖標
    SaveOutline as SaveIcon, // 保存圖標
    CheckboxOutline, // 空白複選框
    CheckboxSharp, // 實心複選框
    LockClosedOutline // 鎖定圖標
  } from '@vicons/ionicons5'

  // 2. 實例化 hooks
  // 獲取路由器實例，用於頁面跳轉
  const router = useRouter()
  // 獲取消息提示實例，用於顯示成功/失敗消息
  const message = useMessage()

  // 3. 狀態管理 (State)
  // 控制頁面或組件的載入狀態
  const loading = ref(false)
  // 控制表單提交的載入狀態，防止重複提交
  const submitting = ref(false)
  // 控制是否顯示進階設定區塊
  const showAdvancedSettings = ref(false)
  // 引用表單組件實例，用於觸發表單驗證
  const formRef = ref(null)
  // 是否啟用詳細比分記錄功能
  const enableDetailedScoring = ref(false)
  // 比分顯示模式：'table' 或其他 (如果未來有不同顯示方式)
  const scoreDisplayMode = ref('table')

  // 4. 表單數據 (Form Data)
  // 比賽記錄表單的響應式數據模型
  const matchForm = ref({
    match_date_ts: new Date().getTime(), // 比賽日期時間戳 (預設為當前時間)
    match_type: 'doubles', // 比賽類型：'singles' (單打) 或 'doubles' (雙打)
    match_format: 'games_9', // 賽制：'games_5' (五局), 'games_7' (七局), 'games_9' (九局)
    player1_id: null, // A方球員1 ID
    player2_id: null, // A方球員2 ID (僅雙打有)
    player3_id: null, // B方球員1 ID
    player4_id: null, // B方球員2 ID (僅雙打有)
    a_games: 0, // A方總贏得局數
    b_games: 0, // B方總贏得局數
    match_notes: '', // 比賽備註
    court_surface: 'hard_court', // 場地表面：'hard_court' (硬地), 'clay_court' (紅土), 'grass_court' (草地)
    court_environment: 'outdoor', // 場地環境：'indoor' (室內) 或 'outdoor' (室外)
    time_slot: 'evening', // 時間段：'morning' (早上), 'afternoon' (下午), 'evening' (晚上)
    total_points: null, // 總分 (可選)
    duration_minutes: null, // 比賽時長 (分鐘, 可選)
    youtube_url: '', // YouTube 連結 (可選)
    first_serve_side: null, // 第一局發球方 ('side_a' 或 'side_b')

    // 詳細局比分，用於記錄每一局的得分 (預設為0)
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

  // 5. 選項數據 (Options Data)
  // 比賽類型下拉選單選項
  const matchTypeOptions = [
    { label: '單打', value: 'singles' },
    { label: '雙打', value: 'doubles' }
  ]

  // 賽制下拉選單選項
  const matchFormatOptions = [
    { label: '五局制', value: 'games_5' },
    { label: '七局制', value: 'games_7' },
    { label: '九局制', value: 'games_9' }
  ]

  // 場地表面下拉選單選項
  const courtSurfaceOptions = [
    { label: '硬地', value: 'hard_court' },
    { label: '紅土', value: 'clay_court' },
    { label: '草地', value: 'grass_court' }
  ]

  // 場地環境下拉選單選項
  const courtEnvironmentOptions = [
    { label: '室內', value: 'indoor' },
    { label: '室外', value: 'outdoor' }
  ]

  // 時間段下拉選單選項
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

  // 6. 輔助函數 (Helper Functions) - 與分數/局數邏輯強相關
  /**
   * 根據當前賽制獲取 Tiebreak 局數列表。
   * @returns {string[]} Tiebreak 局數的文字描述陣列。
   */
  const getTiebreakGames = () => {
    const format = matchForm.value.match_format
    if (format === 'games_5') return ['第5局']
    if (format === 'games_7') return ['第7局']
    if (format === 'games_9') return ['第9局']
    return []
  }

  /**
   * 根據軟網規則判斷指定局數的發球方。
   * 軟網規則：奇數局與第一局發球方相同，偶數局則相反。
   * @param {number} gameNum - 局數。
   * @returns {string|null} 發球方 ('side_a' 或 'side_b')，如果未設定第一局發球方則返回 null。
   */
  const getGameServeTeam = gameNum => {
    if (!matchForm.value.first_serve_side) return null

    if (gameNum % 2 === 1) {
      // 奇數局 (1, 3, 5, 7, 9) 和第一局發球方相同
      return matchForm.value.first_serve_side
    } else {
      // 偶數局 (2, 4, 6, 8) 和第一局發球方相反
      return matchForm.value.first_serve_side === 'side_a' ? 'side_b' : 'side_a'
    }
  }

  /**
   * 檢查指定局數是否為 A 方發球。
   * @param {number} gameNum - 局數。
   * @returns {boolean} 如果是 A 方發球則為 true，否則為 false。
   */
  const isATeamServing = gameNum => {
    return getGameServeTeam(gameNum) === 'side_a'
  }

  /**
   * 檢查指定局數是否為 B 方發球。
   * @param {number} gameNum - 局數。
   * @returns {boolean} 如果是 B 方發球則為 true，否則為 false。
   */
  const isBTeamServing = gameNum => {
    return getGameServeTeam(gameNum) === 'side_b'
  }

  /**
   * 獲取指定局數的發球顯示文本。
   * @param {number} gameNum - 局數。
   * @returns {string} 發球方顯示文本 (例如 'A方發球' 或 'B方發球')。
   */
  const getServeDisplayText = gameNum => {
    const serveTeam = getGameServeTeam(gameNum)
    if (!serveTeam) return '未設定'
    return serveTeam === 'side_a' ? 'A方發球' : 'B方發球'
  }

  /**
   * 判斷指定局數是否為 Tiebreak 局。
   * @param {number} gameNum - 局數。
   * @returns {boolean} 如果是 Tiebreak 局則為 true，否則為 false。
   */
  const isTiebreakGame = gameNum => {
    const format = matchForm.value.match_format
    if (format === 'games_5' && gameNum === 5) return true
    if (format === 'games_7' && gameNum === 7) return true
    if (format === 'games_9' && gameNum === 9) return true
    return false
  }

  /**
   * 判斷分數輸入框是否應該被禁用。
   * 如果比賽已結束且該局未完成，或者該局已完成，則禁用。
   * @param {number} gameNum - 局數。
   * @returns {boolean} 如果應該禁用則為 true，否則為 false。
   */
  const isScoreInputDisabled = gameNum => {
    // 如果比賽已結束且該局未完成，則禁用
    if (matchCompleted.value && !isGameCompleted(gameNum)) return true
    // 如果該局已完成，則禁用 (除非用戶想修改，此處預設禁用)
    return isGameCompleted(gameNum)
  }

  /**
   * 判斷指定局數的比賽是否被禁用 (因為總比賽已結束)。
   * @param {number} gameNum - 局數。
   * @returns {boolean} 如果該局應禁用則為 true，否則為 false。
   */
  const isGameDisabled = gameNum => {
    // 如果比賽已結束且該局未完成，則禁用
    return matchCompleted.value && !isGameCompleted(gameNum)
  }

  /**
   * 根據軟網規則判斷該局是否完成。
   * @param {number} gameNum - 局數。
   * @returns {boolean} 如果該局已完成則為 true，否則為 false。
   */
  const isGameCompleted = gameNum => {
    const aScore = matchForm.value[`game${gameNum}_a_score`] || 0
    const bScore = matchForm.value[`game${gameNum}_b_score`] || 0

    if (aScore === 0 && bScore === 0) return false // 如果分數都是0，表示未開始或已重置，不算完成

    const validation = validateSoftTennisScore(aScore, bScore, gameNum)
    return validation.gameFinished
  }

  /**
   * 獲取指定局數的比賽結果 (A勝/B勝/進行中)。
   * @param {number} gameNum - 局數。
   * @returns {string} 局數結果。
   */
  const getGameResult = gameNum => {
    const aScore = matchForm.value[`game${gameNum}_a_score`] || 0
    const bScore = matchForm.value[`game${gameNum}_b_score`] || 0

    const validation = validateSoftTennisScore(aScore, bScore, gameNum)

    if (validation.gameFinished && validation.winner) {
      return validation.winner === 'A' ? 'A勝' : 'B勝'
    }

    return '進行中'
  }

  /**
   * 獲取指定局數的詳細狀態 (例如: 平分, 領先, 結束等)。
   * @param {number} gameNum - 局數。
   * @returns {object} 包含狀態類型和消息的物件。
   */
  const getGameStatus = gameNum => {
    const aScore = matchForm.value[`game${gameNum}_a_score`] || 0
    const bScore = matchForm.value[`game${gameNum}_b_score`] || 0

    // 如果雙方分數都是0，表示這局還沒開始
    if (aScore === 0 && bScore === 0) {
      const isTiebreak = isTiebreakGame(gameNum)
      return {
        status: 'not_started', // 未開始狀態
        message: isTiebreak ? '未開始 (Tiebreak)' : '未開始'
      }
    }

    // 驗證當前比分是否符合軟網規則
    const validation = validateSoftTennisScore(aScore, bScore, gameNum)

    // 如果分數無效，直接返回錯誤狀態
    if (!validation.isValid) {
      return { status: 'invalid', message: validation.message }
    }

    // 如果該局已完成
    if (validation.gameFinished) {
      const winner = validation.winner === 'A' ? 'A方' : 'B方'
      const isTiebreak = isTiebreakGame(gameNum)
      return {
        status: 'finished', // 完成狀態
        message: isTiebreak ? `${winner}獲勝 (Tiebreak)` : `${winner}獲勝`
      }
    }

    // 如果該局仍在進行中，分析其具體狀態
    const minScore = Math.min(aScore, bScore)
    const maxScore = Math.max(aScore, bScore)
    const scoreDiff = Math.abs(aScore - bScore)
    const isTiebreak = isTiebreakGame(gameNum)

    if (isTiebreak) {
      // Tiebreak 狀態分析
      if (minScore < 6) {
        if (maxScore === 6) {
          return { status: 'close', message: 'Tiebreak 接近勝負點' } // 接近結束
        }
        return { status: 'in_progress', message: 'Tiebreak 進行中' } // 進行中
      } else {
        // 6:6 或更高，進入 Tiebreak 加時 (需要領先兩分)
        if (scoreDiff === 0) {
          return { status: 'deuce', message: `${minScore}:${minScore} Tiebreak平分` } // 平分
        } else if (scoreDiff === 1) {
          const leader = aScore > bScore ? 'A方' : 'B方'
          return { status: 'advantage', message: `${leader}Tiebreak領先` } // 領先但未結束
        }
      }
    } else {
      // 一般局狀態分析
      if (minScore < 3) {
        if (maxScore === 3) {
          return { status: 'close', message: '接近勝負點' } // 接近結束
        }
        return { status: 'in_progress', message: '進行中' } // 進行中
      } else {
        // 3:3 或更高，進入加時 (需要領先兩分)
        if (scoreDiff === 0) {
          return { status: 'deuce', message: `${minScore}:${minScore} 平分` } // 平分
        } else if (scoreDiff === 1) {
          const leader = aScore > bScore ? 'A方' : 'B方'
          return { status: 'advantage', message: `${leader}領先` } // 領先但未結束
        }
      }
    }

    return { status: 'in_progress', message: '進行中' } // 預設為進行中
  }

  /**
   * 根據軟網規則驗證單局比分是否有效及是否已結束。
   * 軟網規則：一般局先到4分且領先1分獲勝，3:3後需領先2分。
   * Tiebreak 局先到7分且領先1分獲勝，6:6後需領先2分。
   * @param {number} aScore - A方得分。
   * @param {number} bScore - B方得分。
   * @param {number|null} gameNum - (可選) 局數，用於判斷是否為 Tiebreak 局。
   * @returns {object} 包含 isValid (是否有效), message (提示信息), gameFinished (是否結束), winner (勝方) 的物件。
   */
  const validateSoftTennisScore = (aScore, bScore, gameNum = null) => {
    // 基本分數不能為負數或過高
    if (aScore < 0 || bScore < 0) {
      return { isValid: false, message: '分數不能為負數' }
    }
    if (aScore > 50 || bScore > 50) {
      return { isValid: false, message: '分數過高，請檢查輸入' }
    }

    // 如果分數都是0，表示還沒開始，視為有效但未結束
    if (aScore === 0 && bScore === 0) {
      return { isValid: true, message: '', gameFinished: false, winner: null }
    }

    // 判斷是否為 Tiebreak 局
    const isTiebreak = gameNum && isTiebreakGame(gameNum)

    if (isTiebreak) {
      // 應用 Tiebreak 局的驗證規則
      return validateTiebreakScore(aScore, bScore)
    } else {
      // 應用一般局的驗證規則
      return validateRegularGameScore(aScore, bScore)
    }
  }

  /**
   * 驗證 Tiebreak 局的比分是否有效。
   * @param {number} aScore - A方得分。
   * @param {number} bScore - B方得分。
   * @returns {object} 驗證結果物件。
   */
  const validateTiebreakScore = (aScore, bScore) => {
    const minScore = Math.min(aScore, bScore)
    const maxScore = Math.max(aScore, bScore)
    const scoreDiff = Math.abs(aScore - bScore)

    // 情況1: 還沒到 6:6，先到 7 分且領先 1 分就贏
    if (minScore < 6) {
      if (maxScore >= 7 && scoreDiff >= 1) {
        const winner = aScore > bScore ? 'A' : 'B'
        return { isValid: true, message: '', gameFinished: true, winner }
      }
      // 檢查是否出現無效分數 (例如一方已到7分但未領先)
      if (maxScore >= 7 && scoreDiff < 1) {
        return { isValid: false, message: '分數已達到勝負點但未拉開差距，無效' }
      }
      return { isValid: true, message: '', gameFinished: false, winner: null }
    }

    // 情況2: 已經到 6:6 或更高，需要領先 2 分才能獲勝
    if (minScore >= 6) {
      if (scoreDiff >= 2) {
        const winner = aScore > bScore ? 'A' : 'B'
        return { isValid: true, message: '', gameFinished: true, winner }
      }
      // 6:6 之後，允許繼續比賽直到有一方領先 2 分
      return { isValid: true, message: '', gameFinished: false, winner: null }
    }

    return { isValid: true, message: '', gameFinished: false, winner: null }
  }

  /**
   * 驗證一般局的比分是否有效。
   * @param {number} aScore - A方得分。
   * @param {number} bScore - B方得分。
   * @returns {object} 驗證結果物件。
   */
  const validateRegularGameScore = (aScore, bScore) => {
    const minScore = Math.min(aScore, bScore)
    const maxScore = Math.max(aScore, bScore)
    const scoreDiff = Math.abs(aScore - bScore)

    // 情況1: 還沒到 3:3，先到 4 分且領先 1 分就贏
    if (minScore < 3) {
      if (maxScore >= 4 && scoreDiff >= 1) {
        const winner = aScore > bScore ? 'A' : 'B'
        return { isValid: true, message: '', gameFinished: true, winner }
      }
      // 檢查是否出現無效分數 (例如一方已到4分但未領先)
      if (maxScore >= 4 && scoreDiff < 1) {
        return { isValid: false, message: '分數已達到勝負點但未拉開差距，無效' }
      }
      return { isValid: true, message: '', gameFinished: false, winner: null }
    }

    // 情況2: 已經到 3:3 或更高，需要領先 2 分才能獲勝
    if (minScore >= 3) {
      if (scoreDiff >= 2) {
        const winner = aScore > bScore ? 'A' : 'B'
        return { isValid: true, message: '', gameFinished: true, winner }
      }
      return { isValid: true, message: '', gameFinished: false, winner: null }
    }

    return { isValid: true, message: '', gameFinished: false, winner: null }
  }

  /**
   * 驗證總比賽分數是否有效。
   * @param {number} aGames - A方贏得的總局數。
   * @param {number} bGames - B方贏得的總局數。
   * @param {string} format - 比賽格式 (例如 'games_5')。
   * @returns {object} 包含 isValid 和 message 的物件。
   */
  const validateMatchScore = (aGames, bGames, format) => {
    const gamesToWin = scoreInputMax.value // 獲取當前賽制下贏得比賽所需的局數

    // 1. 基本驗證：分數不能為負數
    if (aGames < 0 || bGames < 0) {
      return { isValid: false, message: '比賽分數不能為負數' }
    }

    // 2. 不能平局：總局數不能相同
    if (aGames === bGames) {
      return { isValid: false, message: '比賽分數不能相同，必須分出勝負' }
    }

    // 3. 必須有一方達到獲勝局數
    if (aGames < gamesToWin && bGames < gamesToWin) {
      return { isValid: false, message: `比賽尚未結束，需要有一方達到 ${gamesToWin} 局` }
    }

    // 4. 只能有一方達到獲勝局數 (不能雙方都超過或達到勝場數)
    if (aGames >= gamesToWin && bGames >= gamesToWin) {
      return { isValid: false, message: `無效分數：雙方都達到了獲勝局數 ${gamesToWin}` }
    }

    // 5. 達到獲勝局數的一方必須領先
    if (aGames >= gamesToWin && aGames <= bGames) {
      return { isValid: false, message: `無效分數：A方達到 ${gamesToWin} 局但未領先B方` }
    }

    if (bGames >= gamesToWin && bGames <= aGames) {
      return { isValid: false, message: `無效分數：B方達到 ${gamesToWin} 局但未領先A方` }
    }

    return { isValid: true, message: '' } // 驗證通過
  }

  /**
   * 在提交前驗證所有詳細比分是否有效。
   * 只有在啟用詳細比分記錄時才會執行此驗證。
   * @returns {object} 包含 isValid 和 message 的物件。
   */
  const validateDetailedScoresBeforeSubmit = () => {
    if (!enableDetailedScoring.value) return { isValid: true } // 如果未啟用詳細比分，則無需驗證

    for (let i = 1; i <= maxGames.value; i++) {
      const aScore = matchForm.value[`game${i}_a_score`] || 0
      const bScore = matchForm.value[`game${i}_b_score`] || 0

      // 只驗證有輸入分數的局
      if (aScore > 0 || bScore > 0) {
        const validation = validateSoftTennisScore(aScore, bScore, i)
        if (!validation.isValid) {
          const gameType = isTiebreakGame(i) ? 'Tiebreak局' : '局'
          return {
            isValid: false,
            message: `第${i}${gameType}分數無效: ${validation.message}` // 返回具體錯誤信息
          }
        }
      }
    }
    return { isValid: true } // 所有詳細比分都有效
  }

  /**
   * 重置指定局數的比分。
   * @param {number} gameNum - 要重置的局數。
   */
  const resetGameScore = gameNum => {
    matchForm.value[`game${gameNum}_a_score`] = 0
    matchForm.value[`game${gameNum}_b_score`] = 0
    updateGameStatistics() // 重置後更新總局數
    message.info(`第${gameNum}局比分已重置`)
  }

  /**
   * 根據詳細比分更新總局數 (a_games, b_games)。
   * 此方法也會檢查詳細比分的有效性並給出提示。
   */
  const updateGameStatistics = () => {
    if (enableDetailedScoring.value) {
      let aWins = 0
      let bWins = 0
      let hasInvalidScore = false
      let invalidMessage = ''

      for (let i = 1; i <= maxGames.value; i++) {
        const aScore = matchForm.value[`game${i}_a_score`] || 0
        const bScore = matchForm.value[`game${i}_b_score`] || 0

        // 只處理有輸入分數的局
        if (aScore > 0 || bScore > 0) {
          const validation = validateSoftTennisScore(aScore, bScore, i)

          if (!validation.isValid) {
            hasInvalidScore = true // 標記為存在無效分數
            const gameType = isTiebreakGame(i) ? 'Tiebreak局' : '局'
            invalidMessage = `第${i}${gameType}: ${validation.message}`
            break // 找到第一個無效分數就停止
          }

          if (validation.gameFinished && validation.winner) {
            // 如果該局已完成，計入勝場數
            if (validation.winner === 'A') {
              aWins++
            } else {
              bWins++
            }
          }
        }
      }

      // 如果有任何無效分數，顯示錯誤提示並返回
      if (hasInvalidScore) {
        message.error(invalidMessage, { duration: 5000 })
        return
      }

      // 更新表單中的總局數
      matchForm.value.a_games = aWins
      matchForm.value.b_games = bWins

      // 檢查比賽是否已結束，並給出提示
      if (matchCompleted.value && (aWins > 0 || bWins > 0)) {
        const winner = getMatchWinner()
        if (winner !== '未決定') {
          message.success(`比賽結束！${winner} 獲勝！`, { duration: 3000 })
        }
      }
    }
  }

  /**
   * 獲取單局的標題 (例如 '第1局' 或 '第5局 (Tiebreak)')。
   * @param {number} gameNum - 局數。
   * @returns {string} 局數標題。
   */
  const getGameTitle = gameNum => {
    return isTiebreakGame(gameNum) ? `第${gameNum}局 (Tiebreak)` : `第${gameNum}局`
  }

  /**
   * 檢查給定的一方是否是第一局的發球方。
   * @param {string} side - 'side_a' 或 'side_b'。
   * @returns {boolean} 如果是則為 true，否則為 false。
   */
  const isFirstServeTeam = side => {
    return matchForm.value.first_serve_side === side
  }

  /**
   * 獲取比賽的最終勝者。
   * @returns {string} 'A方', 'B方' 或 '未決定'。
   */
  const getMatchWinner = () => {
    if (detailedStats.value.aWins >= gamesToWin.value) return 'A方'
    if (detailedStats.value.bWins >= gamesToWin.value) return 'B方'
    return '未決定'
  }

  /**
   * 重置所有詳細局的比分和總比分。
   */
  const resetDetailedScores = () => {
    for (let i = 1; i <= maxGames.value; i++) {
      matchForm.value[`game${i}_a_score`] = 0
      matchForm.value[`game${i}_b_score`] = 0
    }
    matchForm.value.a_games = 0
    matchForm.value.b_games = 0
    message.info('詳細比分已重置')
  }

  /**
   * 重置整個表單到初始狀態。
   */
  const resetForm = () => {
    matchForm.value = {
      match_date_ts: new Date().getTime(),
      match_type: 'doubles',
      match_format: 'games_9',
      player1_id: null,
      player2_id: null,
      player3_id: null,
      player4_id: null,
      a_games: 0,
      b_games: 0,
      match_notes: '',
      court_surface: 'hard_court',
      court_environment: 'outdoor',
      time_slot: 'evening',
      total_points: null,
      duration_minutes: null,
      youtube_url: '',
      first_serve_side: null // 也要重置發球方
    }

    // 確保所有詳細分數都被重置
    for (let i = 1; i <= 9; i++) {
      matchForm.value[`game${i}_a_score`] = 0
      matchForm.value[`game${i}_b_score`] = 0
    }
    enableDetailedScoring.value = false // 重置詳細比分開關
    message.info('表單已重置')
  }

  /**
   * 導航回 'ManagementCenter' 頁面。
   */
  const goBack = () => {
    router.push({ name: 'ManagementCenter' })
  }

  // 7. 計算屬性 (Computed Properties)
  /**
   * 計算當前賽制下的最大局數。
   * 例如：五局制最多 5 局，九局制最多 9 局。
   */
  const maxGames = computed(() => {
    const format = matchForm.value.match_format
    return format ? matchFormatConfig[format]?.maxGames || 9 : 9 // 預設為 9 局
  })

  /**
   * 計算每行顯示的比分卡片數量 (用於佈局)。
   */
  const getCardsPerRow = computed(() => {
    if (maxGames.value <= 5) return 5
    if (maxGames.value <= 7) return 7
    return 9
  })

  /**
   * 計算詳細的比賽統計數據，包括勝場數、完成局數、總分數等。
   */
  const detailedStats = computed(() => {
    let aWins = 0 // A方贏得局數
    let bWins = 0 // B方贏得局數
    let completedGames = 0 // 已完成局數
    let totalPoints = 0 // 總分數
    let inProgressGames = 0 // 進行中局數

    for (let i = 1; i <= maxGames.value; i++) {
      const aScore = matchForm.value[`game${i}_a_score`] || 0
      const bScore = matchForm.value[`game${i}_b_score`] || 0

      // 只統計有輸入分數的局
      if (aScore > 0 || bScore > 0) {
        totalPoints += aScore + bScore // 累加總分

        const validation = validateSoftTennisScore(aScore, bScore, i)

        if (validation.gameFinished && validation.winner) {
          completedGames++ // 計數已完成的局
          if (validation.winner === 'A') {
            aWins++
          } else {
            bWins++
          }
        } else if (validation.isValid) {
          inProgressGames++ // 計數進行中的局 (有效但未完成)
        }
      }
    }

    return {
      aWins,
      bWins,
      completedGames,
      totalPoints,
      inProgressGames,
      totalActiveGames: completedGames + inProgressGames // 總活躍局數 (已完成 + 進行中)
    }
  })

  /**
   * 根據單局比分狀態返回對應的 UI 樣式類型。
   * 用於顯示比分輸入框的狀態提示 (例如 'success', 'error', 'warning' 等)。
   */
  const getGameResultType = gameNum => {
    const result = getGameResult(gameNum) // 獲取局結果 (A勝/B勝/進行中)
    const status = getGameStatus(gameNum) // 獲取局詳細狀態

    if (status.status === 'invalid') return 'error' // 無效分數顯示紅色
    if (result === 'A勝') return 'success' // A勝顯示綠色
    if (result === 'B勝') return 'warning' // B勝顯示黃色 (或可改為其他顏色)
    if (status.status === 'deuce') return 'info' // 平分顯示藍色
    if (status.status === 'advantage') return 'primary' // 領先顯示主色

    return 'default' // 預設狀態 (未開始或進行中)
  }

  /**
   * 獲取單局分數輸入框的驗證狀態和提示信息。
   * @param {number} gameNum - 局數。
   * @returns {object|null} 包含 type (類型) 和 message (信息) 的物件，如果沒有提示則為 null。
   */
  const getScoreInputStatus = gameNum => {
    const aScore = matchForm.value[`game${gameNum}_a_score`] || 0
    const bScore = matchForm.value[`game${gameNum}_b_score`] || 0

    if (aScore === 0 && bScore === 0) return null // 如果沒有分數，不顯示提示

    const validation = validateSoftTennisScore(aScore, bScore, gameNum)

    if (!validation.isValid) {
      return { type: 'error', message: validation.message } // 無效分數
    }

    const status = getGameStatus(gameNum)

    if (status.status === 'finished') {
      return { type: 'success', message: status.message } // 局已完成
    }

    if (status.status === 'deuce' || status.status === 'advantage') {
      return { type: 'warning', message: status.message } // 平分或領先 (接近結束)
    }

    if (status.status === 'close') {
      return { type: 'info', message: status.message } // 接近勝負點
    }

    return null // 其他情況不顯示提示
  }

  /**
   * 計算比賽是否已結束。
   */
  const matchCompleted = computed(() => {
    // 只要A方或B方達到獲勝所需局數，比賽就結束
    return detailedStats.value.aWins >= gamesToWin.value || detailedStats.value.bWins >= gamesToWin.value
  })

  /**
   * 計算當前賽制下贏得比賽所需的局數。
   * 例如：五局制需要贏 3 局，九局制需要贏 5 局。
   */
  const gamesToWin = computed(() => {
    const formatMap = {
      games_5: 3, // 5局3勝
      games_7: 4, // 7局4勝
      games_9: 5 // 9局5勝
    }
    return formatMap[matchForm.value.match_format] || 5 // 預設為 5
  })

  /**
   * 計算分數輸入的最大值 (用於前端驗證，防止輸入過大的數字)。
   * 這個值應該與實際的贏局分數掛鉤。
   */
  const scoreInputMax = computed(() => {
    const formatMap = {
      games_5: 3, // 五局制贏得比賽需要 3 局
      games_7: 4, // 七局制贏得比賽需要 4 局
      games_9: 5 // 九局制贏得比賽需要 5 局
    }
    return formatMap[matchForm.value.match_format] || 5
  })

  /**
   * 計算表單是否可以提交。
   * 檢查必填項和總比分驗證。
   */
  const canSubmit = computed(() => {
    const form = matchForm.value

    // 基本必填檢查：球員1和球員3必須選擇
    if (!form.player1_id || !form.player3_id) {
      return false
    }

    // 如果是雙打模式，球員2和球員4也必須選擇
    if (form.match_type === 'doubles' && (!form.player2_id || !form.player4_id)) {
      return false
    }

    // 使用新的總比分驗證邏輯來判斷是否可以提交
    const scoreValidation = validateMatchScore(form.a_games, form.b_games, form.match_format)

    return scoreValidation.isValid
  })

  /**
   * 計算比賽的總體狀態 (有效性、完成度、消息)。
   */
  const matchStatus = computed(() => {
    const validation = validateMatchScore(
      matchForm.value.a_games,
      matchForm.value.b_games,
      matchForm.value.match_format
    )

    return {
      isValid: validation.isValid, // 總比分是否有效
      message: validation.message, // 驗證消息
      // 比賽是否完成：總比分有效且沒有 'PENDING' 狀態 (這個 'PENDING' 可能是舊邏輯殘留，可根據實際後端處理調整)
      isComplete: validation.isValid && matchForm.value.side_a_outcome !== 'PENDING'
    }
  })

  // 8. 表單驗證規則 (Form Rules)
  // Naive UI 表單驗證規則定義
  const formRules = {
    match_date: [{ required: true, message: '請選擇比賽日期', trigger: 'change' }],
    match_type: [{ required: true, message: '請選擇比賽類型', trigger: 'change' }],
    match_format: [{ required: true, message: '請選擇賽制', trigger: 'change' }],
    player1_id: [{ required: true, message: '請選擇球員1', trigger: 'change' }],
    player3_id: [{ required: true, message: '請選擇球員3', trigger: 'change' }],
    // A方總局數的驗證規則
    a_games: [
      { required: true, message: '請輸入A方得分', trigger: 'blur' },
      { type: 'number', min: 0, message: '分數不能為負數', trigger: 'blur' },
      {
        // 自定義驗證器，使用 validateMatchScore 檢查總局數有效性
        validator: (rule, value, callback) => {
          const validation = validateMatchScore(value, matchForm.value.b_games, matchForm.value.match_format)
          if (!validation.isValid) {
            callback(new Error(validation.message)) // 驗證失敗則拋出錯誤
          } else {
            callback() // 驗證成功
          }
        },
        trigger: 'blur' // 失去焦點時觸發
      }
    ],
    // B方總局數的驗證規則 (與 A 方類似)
    b_games: [
      { required: true, message: '請輸入B方得分', trigger: 'blur' },
      { type: 'number', min: 0, message: '分數不能為負數', trigger: 'blur' },
      {
        validator: (rule, value, callback) => {
          const validation = validateMatchScore(matchForm.value.a_games, value, matchForm.value.match_format)
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

  // 9. 事件處理函數 (Event Handlers)
  /**
   * 處理比賽記錄的提交邏輯。
   * 包含前端表單驗證、數據組裝、API 請求和錯誤處理。
   */
  const handleRecordMatch = async () => {
    try {
      // 觸發 Naive UI 表單的基本驗證
      const valid = await formRef.value?.validate()
      if (!valid) {
        message.error('請修正表單中的錯誤。')
        return
      }
    } catch (e) {
      // 捕獲表單驗證本身可能拋出的錯誤
      message.error('請修正表單中的錯誤。')
      return
    }

    // 再次進行客戶端總比分預驗證 (確保在提交前最後檢查一次)
    const localValidation = validateMatchScore(
      matchForm.value.a_games,
      matchForm.value.b_games,
      matchForm.value.match_format
    )

    if (!localValidation.isValid) {
      message.error(localValidation.message)
      return
    }

    submitting.value = true // 設定提交狀態為 true

    try {
      // 格式化日期時間戳為 YYYY-MM-DD 格式
      const formatDate = timestamp => {
        if (!timestamp) return null
        const date = new Date(timestamp)
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      }

      // 組裝要發送到後端的 payload 數據
      const payload = {
        match_date: formatDate(matchForm.value.match_date_ts),
        match_type: matchForm.value.match_type,
        match_format: matchForm.value.match_format,
        player1_id: matchForm.value.player1_id,
        // 如果是雙打，才包含 player2_id
        player2_id: matchForm.value.match_type === 'doubles' ? matchForm.value.player2_id : null,
        player3_id: matchForm.value.player3_id,
        // 如果是雙打，才包含 player4_id
        player4_id: matchForm.value.match_type === 'doubles' ? matchForm.value.player4_id : null,
        a_games: matchForm.value.a_games,
        b_games: matchForm.value.b_games,
        match_notes: matchForm.value.match_notes || null, // 空字符串轉為 null
        court_surface: matchForm.value.court_surface || null,
        court_environment: matchForm.value.court_environment || null,
        time_slot: matchForm.value.time_slot || null,
        total_points: matchForm.value.total_points || null,
        duration_minutes: matchForm.value.duration_minutes || null,
        youtube_url: matchForm.value.youtube_url || null,
        first_serve_side: matchForm.value.first_serve_side || null // 第一局發球方
      }

      // 如果啟用詳細比分，則將每局分數加入 payload
      if (enableDetailedScoring.value) {
        // 在發送前再次驗證詳細比分 (雙重保險)
        const scoreValidation = validateDetailedScoresBeforeSubmit()
        if (!scoreValidation.isValid) {
          message.error(scoreValidation.message)
          return
        }
        for (let i = 1; i <= maxGames.value; i++) {
          payload[`game${i}_a_score`] = matchForm.value[`game${i}_a_score`] || 0
          payload[`game${i}_b_score`] = matchForm.value[`game${i}_b_score`] || 0
        }
      }

      console.log('發送新增請求:', payload)

      // 根據是否啟用詳細比分，選擇不同的 API 端點
      const endpoint = enableDetailedScoring.value ? '/match-records/detailed' : '/match-records'
      const response = await apiClient.post(endpoint, payload) // 發送 POST 請求
      console.log('新增響應:', response.data)

      message.success(response.data.message || '比賽結果已成功儲存！') // 顯示成功消息

      // 1.5 秒後跳轉到 Leaderboard 頁面
      setTimeout(() => {
        router.push({ name: 'Leaderboard' })
      }, 1500)
    } catch (err) {
      console.error('新增失敗詳細信息:', {
        error: err,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText
      })

      const errorData = err.response?.data

      // 處理來自後端的分數驗證錯誤
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
          duration: 8000, // 錯誤消息顯示更長時間
          closable: true // 允許用戶手動關閉
        })
        return
      }

      // 處理其他錯誤類型
      let errorMessage = '儲存失敗，請稍後再試。' // 預設錯誤消息

      if (errorData?.details) {
        // 如果後端返回詳細的驗證錯誤信息
        errorMessage = '輸入數據有誤：\n' + Object.values(errorData.details).flat().join('\n')
        message.error(errorMessage, { duration: 7000, closable: true })
      } else if (errorData?.message) {
        // 如果後端返回一般錯誤消息
        errorMessage = errorData.message
        message.error(errorMessage)
      } else {
        // 其他未知錯誤
        message.error(errorMessage)
      }
    } finally {
      submitting.value = false // 無論成功或失敗，結束提交狀態
    }
  }

  // 10. 監聽器 (Watchers)
  // 監聽總局數 (a_games, b_games) 和賽制 (match_format) 的變化
  watch(
    [() => matchForm.value.a_games, () => matchForm.value.b_games, () => matchForm.value.match_format],
    (newValues, oldValues) => {
      const [newAGames, newBGames, newFormat] = newValues
      const [oldAGames, oldBGames, oldFormat] = oldValues || []

      // 只有當相關值真正改變時才執行邏輯
      if (newAGames !== oldAGames || newBGames !== oldBGames || newFormat !== oldFormat) {
        // 在前端進行本地驗證，提供即時反饋
        const validation = validateMatchScore(newAGames, newBGames, newFormat)

        if (!validation.isValid && (newAGames > 0 || newBGames > 0)) {
          console.warn('分數驗證失敗:', validation.message)
          // 這裡可以選擇是否觸發表單錯誤提示，通常由 formRules 處理
        }

        // 根據總局數判斷比賽結果 (WIN/LOSS/PENDING)
        const gamesToWin = scoreInputMax.value
        if (newAGames >= gamesToWin && newAGames > newBGames) {
          matchForm.value.side_a_outcome = 'WIN'
        } else if (newBGames >= gamesToWin && newBGames > newAGames) {
          matchForm.value.side_a_outcome = 'LOSS'
        } else {
          matchForm.value.side_a_outcome = 'PENDING'
        }
      }
    },
    { deep: true } // 深度監聽 (如果內部對象有變化也會觸發)
  )

  // 監聽比賽類型 (match_type) 的變化
  watch(
    () => matchForm.value.match_type,
    newType => {
      // 如果切換到單打，清除雙打球員的選擇
      if (newType === 'singles') {
        matchForm.value.player2_id = null
        matchForm.value.player4_id = null
      }
    }
  )

  // 監聽賽制 (match_format) 的變化
  watch(
    () => matchForm.value.match_format,
    newFormat => {
      if (newFormat) {
        // 當賽制改變時，重置所有詳細局的比分
        for (let i = 1; i <= 9; i++) {
          matchForm.value[`game${i}_a_score`] = 0
          matchForm.value[`game${i}_b_score`] = 0
        }
        enableDetailedScoring.value = false // 同時關閉詳細比分開關
        message.info('賽制已變更，詳細比分已重置') // 提示用戶
      }
    }
  )
</script>

<style scoped>
  @import "@/assets/css/page/add-match-record-view.css";
</style>
