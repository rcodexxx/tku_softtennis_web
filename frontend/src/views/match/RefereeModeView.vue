<!-- RefereeModeView.vue - 修正版本 -->
<template>
  <div class="referee-mode-container" :class="{ 'landscape-mode': isLandscape }">
    <!-- 橫屏提示 -->
    <div v-if="showOrientationHint" class="orientation-hint-overlay">
      <div class="hint-content">
        <div class="rotate-icon">📱➡️📱</div>
        <h3>請將裝置橫向放置</h3>
        <p>裁判模式專為橫屏設計，提供更好的計分體驗</p>
        <n-button type="primary" @click="showOrientationHint = false"> 我知道了</n-button>
      </div>
    </div>

    <!-- Phase 1: 比賽設定 -->
    <div v-if="currentPhase === 'setup'" class="referee-arena-setup">
      <div class="expanded-arena-container">
        <!-- 配置控制器 -->
        <div class="match-config-controller">
          <div class="config-icon">⚙️</div>
          <div class="config-text">{{ configStepText }}</div>
        </div>

        <!-- 設定流程 -->
        <div class="setup-flow-container">
          <!-- 比賽類型選擇 -->
          <div v-if="currentStep === 'type'" class="setup-step">
            <div class="step-title">選擇比賽類型</div>
            <div class="type-selection-cards">
              <div
                class="match-type-card"
                :class="{ active: matchForm.match_type === 'singles' }"
                @click="selectMatchType('singles')"
              >
                <div class="type-icon">🎾</div>
                <div class="type-text">單打</div>
              </div>

              <div
                class="match-type-card"
                :class="{ active: matchForm.match_type === 'doubles' }"
                @click="selectMatchType('doubles')"
              >
                <div class="type-icon">🎾🎾</div>
                <div class="type-text">雙打</div>
              </div>
            </div>

            <!-- 賽制選擇 -->
            <div class="format-selection">
              <div class="format-title">選擇賽制</div>
              <n-space>
                <n-button
                  v-for="format in matchFormatOptions"
                  :key="format.value"
                  :type="matchForm.match_format === format.value ? 'primary' : 'default'"
                  @click="matchForm.match_format = format.value"
                >
                  {{ format.label }}
                </n-button>
              </n-space>
            </div>
          </div>

          <!-- 球員選擇 -->
          <div v-if="currentStep === 'players'" class="setup-step">
            <div class="step-title">選擇參賽球員</div>
            <MatchPlayerSelector v-model="matchForm" class="referee-player-selector" />
          </div>

          <!-- 發球權選擇 -->
          <div v-if="currentStep === 'serve'" class="setup-step">
            <div class="step-title">選擇首局發球方</div>
            <div class="serve-selection">
              <div class="serve-option team-a" :class="{ selected: firstServe === 'a' }" @click="selectFirstServe('a')">
                <div class="serve-ball">
                  <div class="ball-core"></div>
                </div>
                <div class="serve-text">隊伍 A 先發球</div>
              </div>

              <div class="vs-divider">VS</div>

              <div class="serve-option team-b" :class="{ selected: firstServe === 'b' }" @click="selectFirstServe('b')">
                <div class="serve-ball">
                  <div class="ball-core"></div>
                </div>
                <div class="serve-text">隊伍 B 先發球</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 進度指示器 -->
        <div class="setup-progress-indicator">
          <div class="progress-step" :class="{ active: currentStep === 'type' }">類型</div>
          <div class="progress-step" :class="{ active: currentStep === 'players' }">球員</div>
          <div class="progress-step" :class="{ active: currentStep === 'serve' }">發球</div>
        </div>

        <!-- 導航按鈕 -->
        <div class="setup-navigation">
          <n-button v-if="currentStep !== 'type'" size="large" @click="previousStep"> 上一步</n-button>
          <n-button size="large" @click="goBack"> 返回</n-button>
          <n-button v-if="canProceed" type="primary" size="large" @click="nextStep">
            {{ currentStep === 'serve' ? '開始比賽' : '下一步' }}
          </n-button>
        </div>
      </div>
    </div>

    <!-- Phase 2: 實時計分 -->
    <div v-if="currentPhase === 'live'" class="referee-arena-live">
      <div class="live-arena-container">
        <div class="live-battle-container">
          <!-- 隊伍A區域 -->
          <div class="live-team-section team-a">
            <div
              class="team-card-live"
              :class="{
                'is-serving': servingSide === 'a',
                'is-winning': isTeamAWinning,
                celebrating: celebratingTeam === 'a'
              }"
            >
              <div class="team-players-live">
                <div class="team-name">隊伍 A</div>
                <div class="players-avatars">
                  <div v-for="player in teamAPlayers" :key="player.id" class="player-avatar-live">
                    <div class="player-name-tiny">{{ player.name }}</div>
                  </div>
                </div>
              </div>

              <div class="score-display-massive">{{ aGames }}</div>

              <div class="score-controls-live">
                <n-button class="score-btn-massive add-score" :disabled="matchFinished" @click="addScore('a')">
                  <div class="btn-content-live">
                    <div class="btn-icon">+</div>
                    <div class="btn-text">得分</div>
                  </div>
                </n-button>

                <n-button class="score-btn-massive undo-score" :disabled="!canUndo('a')" @click="undoLastScore('a')">
                  <div class="btn-content-live">
                    <div class="btn-icon">↶</div>
                    <div class="btn-text">撤銷</div>
                  </div>
                </n-button>
              </div>
            </div>
          </div>

          <!-- 中央戰況區 -->
          <div class="battle-center-zone">
            <div class="serving-indicator-live">
              <div
                class="tennis-ball-animated"
                :class="{ 'serve-a': servingSide === 'a', 'serve-b': servingSide === 'b' }"
              >
                <div class="ball-core"></div>
              </div>
              <div class="serve-text-live">{{ servingText }}</div>
            </div>

            <div class="match-status-live">
              <div class="status-display">
                <div class="current-score">{{ aGames }} - {{ bGames }}</div>
                <div class="match-format">{{ formatText }}</div>
              </div>
            </div>

            <div class="emergency-controls">
              <n-button class="emergency-btn pause" @click="pauseMatch"> ⏸️ 暫停</n-button>
            </div>
          </div>

          <!-- 隊伍B區域 -->
          <div class="live-team-section team-b">
            <div
              class="team-card-live"
              :class="{
                'is-serving': servingSide === 'b',
                'is-winning': isTeamBWinning,
                celebrating: celebratingTeam === 'b'
              }"
            >
              <div class="team-players-live">
                <div class="team-name">隊伍 B</div>
                <div class="players-avatars">
                  <div v-for="player in teamBPlayers" :key="player.id" class="player-avatar-live">
                    <div class="player-name-tiny">{{ player.name }}</div>
                  </div>
                </div>
              </div>

              <div class="score-display-massive">{{ bGames }}</div>

              <div class="score-controls-live">
                <n-button class="score-btn-massive add-score" :disabled="matchFinished" @click="addScore('b')">
                  <div class="btn-content-live">
                    <div class="btn-icon">+</div>
                    <div class="btn-text">得分</div>
                  </div>
                </n-button>

                <n-button class="score-btn-massive undo-score" :disabled="!canUndo('b')" @click="undoLastScore('b')">
                  <div class="btn-content-live">
                    <div class="btn-icon">↶</div>
                    <div class="btn-text">撤銷</div>
                  </div>
                </n-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Phase 3: 比賽結果 -->
    <div v-if="currentPhase === 'result'" class="referee-arena-result">
      <div class="victory-arena-container">
        <div class="celebration-arena">
          <div class="winner-showcase">
            <div class="victory-crown">👑</div>
            <div class="winner-team-name">{{ winnerTeamName }} 獲勝！</div>
            <div class="final-score">{{ aGames }} - {{ bGames }}</div>
            <div class="victory-text">恭喜獲勝！</div>
          </div>

          <div class="result-actions">
            <n-button type="primary" size="large" @click="saveAndExit"> 儲存比賽記錄</n-button>
            <n-button size="large" @click="startNewMatch"> 開始新比賽</n-button>
            <n-button size="large" @click="goBack"> 返回主頁</n-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 暫停對話框 -->
    <n-modal v-model:show="showPauseDialog" preset="dialog" title="比賽暫停">
      <p>比賽已暫停，您可以：</p>
      <template #action>
        <n-space>
          <n-button @click="resumeMatch">繼續比賽</n-button>
          <n-button type="warning" @click="endMatch">結束比賽</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import MatchPlayerSelector from '@/components/match/MatchPlayerSelector.vue'
  import apiClient from '@/services/apiClient'

  const router = useRouter()
  const message = useMessage()

  // 響應式狀態
  const isLandscape = ref(false)
  const showOrientationHint = ref(false)
  const currentPhase = ref('setup') // 'setup' | 'live' | 'result'
  const currentStep = ref('type') // 'type' | 'players' | 'serve'
  const showPauseDialog = ref(false)
  const celebratingTeam = ref(null)

  // 比賽設定
  const matchForm = ref({
    match_date_ts: new Date().getTime(),
    match_type: 'doubles',
    match_format: 'games_9',
    player1_id: null,
    player2_id: null,
    player3_id: null,
    player4_id: null,
    court_surface: 'hard_court',
    court_environment: 'outdoor',
    time_slot: 'evening'
  })

  const matchFormatOptions = [
    { label: '五局制', value: 'games_5' },
    { label: '七局制', value: 'games_7' },
    { label: '九局制', value: 'games_9' }
  ]

  // 比賽狀態
  const firstServe = ref('a')
  const servingSide = ref('a')
  const aGames = ref(0)
  const bGames = ref(0)
  const matchFinished = ref(false)
  const scoreHistory = ref([])
  const teamAPlayers = ref([])
  const teamBPlayers = ref([])

  // 計算屬性
  const configStepText = computed(() => {
    const stepTexts = {
      type: '設定比賽類型',
      players: '選擇參賽球員',
      serve: '選擇發球方'
    }
    return stepTexts[currentStep.value]
  })

  const canProceed = computed(() => {
    switch (currentStep.value) {
      case 'type':
        return matchForm.value.match_type && matchForm.value.match_format
      case 'players':
        return (
          matchForm.value.player1_id &&
          matchForm.value.player3_id &&
          (matchForm.value.match_type === 'singles' || (matchForm.value.player2_id && matchForm.value.player4_id))
        )
      case 'serve':
        return firstServe.value
      default:
        return false
    }
  })

  const gamesToWin = computed(() => {
    const formatMap = {
      games_5: 3,
      games_7: 4,
      games_9: 5
    }
    return formatMap[matchForm.value.match_format] || 5
  })

  const isTeamAWinning = computed(() => aGames.value > bGames.value)
  const isTeamBWinning = computed(() => bGames.value > aGames.value)

  const servingText = computed(() => {
    return servingSide.value === 'a' ? '隊伍 A 發球' : '隊伍 B 發球'
  })

  const formatText = computed(() => {
    const formatMap = {
      games_5: '五局制',
      games_7: '七局制',
      games_9: '九局制'
    }
    return formatMap[matchForm.value.match_format]
  })

  const winnerTeamName = computed(() => {
    if (aGames.value >= gamesToWin.value) return '隊伍 A'
    if (bGames.value >= gamesToWin.value) return '隊伍 B'
    return ''
  })

  // 方法
  const checkOrientation = () => {
    isLandscape.value = window.innerWidth > window.innerHeight
    if (!isLandscape.value && currentPhase.value !== 'setup') {
      showOrientationHint.value = true
    }
  }

  const checkDeviceSupport = () => {
    const isDesktop = window.innerWidth > 1024 && !('ontouchstart' in window)

    if (isDesktop) {
      message.warning('裁判模式僅支援手機和平板裝置')
      router.push({ name: 'Leaderboard' })
      return false
    }

    return true
  }

  const selectMatchType = type => {
    matchForm.value.match_type = type
    if (type === 'singles') {
      matchForm.value.player2_id = null
      matchForm.value.player4_id = null
    }
  }

  const selectFirstServe = team => {
    firstServe.value = team
    servingSide.value = team
  }

  const nextStep = () => {
    if (currentStep.value === 'type') {
      currentStep.value = 'players'
    } else if (currentStep.value === 'players') {
      loadTeamPlayers()
      currentStep.value = 'serve'
    } else if (currentStep.value === 'serve') {
      startMatch()
    }
  }

  const previousStep = () => {
    if (currentStep.value === 'players') {
      currentStep.value = 'type'
    } else if (currentStep.value === 'serve') {
      currentStep.value = 'players'
    }
  }

  const loadTeamPlayers = () => {
    // 模擬載入球員資料
    teamAPlayers.value = [
      { id: matchForm.value.player1_id, name: '球員1' },
      { id: matchForm.value.player2_id, name: '球員2' }
    ].filter(p => p.id)

    teamBPlayers.value = [
      { id: matchForm.value.player3_id, name: '球員3' },
      { id: matchForm.value.player4_id, name: '球員4' }
    ].filter(p => p.id)
  }

  const startMatch = () => {
    currentPhase.value = 'live'
    aGames.value = 0
    bGames.value = 0
    matchFinished.value = false
    scoreHistory.value = []
    servingSide.value = firstServe.value
  }

  const addScore = team => {
    if (matchFinished.value) return

    // 記錄分數歷史
    scoreHistory.value.push({
      team,
      aGames: aGames.value,
      bGames: bGames.value,
      servingSide: servingSide.value,
      timestamp: Date.now()
    })

    // 更新分數
    if (team === 'a') {
      aGames.value++
    } else {
      bGames.value++
    }

    // 觸發慶祝動畫
    triggerScoreCelebration(team)

    // 檢查比賽結束
    if (aGames.value >= gamesToWin.value || bGames.value >= gamesToWin.value) {
      finishMatch()
    } else {
      // 切換發球權
      switchServing()
    }
  }

  const undoLastScore = team => {
    const lastScore = scoreHistory.value.pop()
    if (lastScore) {
      aGames.value = lastScore.aGames
      bGames.value = lastScore.bGames
      servingSide.value = lastScore.servingSide
      matchFinished.value = false
    }
  }

  const canUndo = team => {
    return scoreHistory.value.length > 0
  }

  const triggerScoreCelebration = team => {
    celebratingTeam.value = team
    setTimeout(() => {
      celebratingTeam.value = null
    }, 1000)
  }

  const switchServing = () => {
    servingSide.value = servingSide.value === 'a' ? 'b' : 'a'
  }

  const finishMatch = () => {
    matchFinished.value = true

    setTimeout(() => {
      currentPhase.value = 'result'
    }, 2000)
  }

  const pauseMatch = () => {
    showPauseDialog.value = true
  }

  const resumeMatch = () => {
    showPauseDialog.value = false
  }

  const endMatch = () => {
    showPauseDialog.value = false
    finishMatch()
  }

  const saveAndExit = async () => {
    try {
      const matchDate = new Date(matchForm.value.match_date_ts)
      const matchData = {
        match_date: `${matchDate.getFullYear()}-${String(matchDate.getMonth() + 1).padStart(2, '0')}-${String(matchDate.getDate()).padStart(2, '0')}`,
        match_type: matchForm.value.match_type,
        match_format: matchForm.value.match_format,
        player1_id: matchForm.value.player1_id,
        player2_id: matchForm.value.player2_id,
        player3_id: matchForm.value.player3_id,
        player4_id: matchForm.value.player4_id,
        a_games: aGames.value,
        b_games: bGames.value,
        court_surface: matchForm.value.court_surface,
        court_environment: matchForm.value.court_environment,
        time_slot: matchForm.value.time_slot,
        first_serve_side: firstServe.value === 'a' ? 'side_a' : 'side_b',
        notes: '裁判模式記錄'
      }

      await apiClient.post('/match-records', matchData)
      message.success('比賽記錄已成功儲存！')

      setTimeout(() => {
        router.push({ name: 'Leaderboard' })
      }, 1500)
    } catch (error) {
      console.error('儲存比賽記錄失敗:', error)
      message.error(error.response?.data?.message || '儲存失敗，請稍後再試')
    }
  }

  const startNewMatch = () => {
    // 重置所有狀態
    currentPhase.value = 'setup'
    currentStep.value = 'type'
    matchForm.value = {
      match_date_ts: new Date().getTime(),
      match_type: 'doubles',
      match_format: 'games_9',
      player1_id: null,
      player2_id: null,
      player3_id: null,
      player4_id: null,
      court_surface: 'hard_court',
      court_environment: 'outdoor',
      time_slot: 'evening'
    }
    aGames.value = 0
    bGames.value = 0
    firstServe.value = 'a'
    servingSide.value = 'a'
    matchFinished.value = false
    scoreHistory.value = []
    teamAPlayers.value = []
    teamBPlayers.value = []
  }

  const goBack = () => {
    router.push({ name: 'Leaderboard' })
  }

  // 生命週期
  onMounted(() => {
    if (!checkDeviceSupport()) return

    checkOrientation()
    window.addEventListener('orientationchange', checkOrientation)
    window.addEventListener('resize', checkOrientation)
  })

  onUnmounted(() => {
    window.removeEventListener('orientationchange', checkOrientation)
    window.removeEventListener('resize', checkOrientation)
  })

  // 監聽器
  watch(isLandscape, newVal => {
    if (!newVal && currentPhase.value === 'live') {
      showOrientationHint.value = true
    }
  })
</script>

<style scoped>
  @import '@/assets/css/components/referee-mode.css';
</style>
