<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="user-greeting">
          <h1 class="greeting-text">歡迎回來，{{ profileData?.display_name || '球員' }}！</h1>
          <p class="greeting-subtitle">準備好今天的練習了嗎？</p>
        </div>
        <div class="header-actions">
          <n-button type="primary" size="large" round @click="showEditProfile = true">
            <template #icon>
              <n-icon :component="SettingsIcon" />
            </template>
            編輯資料
          </n-button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <n-spin size="large" />
      <p>載入中...</p>
    </div>

    <!-- Error State -->
    <n-alert v-if="fetchError" title="載入錯誤" type="error" closable class="mb-4" @close="fetchError = null">
      {{ fetchError }}
    </n-alert>

    <!-- Main Dashboard Content -->
    <div v-if="!loading && !fetchError && profileData" class="dashboard-content">
      <!-- Stats Overview Cards -->
      <div class="stats-grid">
        <div class="stat-card ranking-card">
          <div class="stat-icon">🏆</div>
          <div class="stat-content">
            <h3>目前排名</h3>
            <div class="stat-value"># {{ playerStats.rank || '--' }}</div>
          </div>
        </div>

        <div class="stat-card matches-card">
          <div class="stat-icon">🎾</div>
          <div class="stat-content">
            <h3>總比賽場次</h3>
            <div class="stat-value">{{ playerStats.total_matches || 0 }}</div>
          </div>
        </div>

        <div class="stat-card winrate-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <h3>勝率</h3>
            <div class="stat-value">{{ formatWinRate(playerStats.win_rate) }}%</div>
            <div class="stat-change">{{ playerStats.wins || 0 }}勝 {{ playerStats.losses || 0 }}敗</div>
          </div>
        </div>

        <div class="stat-card score-card">
          <div class="stat-icon">⭐</div>
          <div class="stat-content">
            <h3>官方分數</h3>
            <div class="stat-value">{{ formatScore(playerStats.official_rank_score || 0, 2) }}</div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="main-grid">
        <!-- Left Column -->
        <div class="left-column">
          <!-- Player Profile Card -->
          <n-card title="球員檔案" class="profile-card">
            <div class="profile-content">
              <div class="avatar-section">
                <div class="player-avatar-container">
                          <BaseIdenticon :user="authStore.user" :size="80" />
                  <div v-if="!avatarLoaded" class="avatar-overlay">
                    <n-spin size="small" />
                  </div>
                </div>
                <div class="player-basic-info">
                  <h3 class="player-name">
                    {{ profileData.member_profile?.name || profileData.display_name || '未設定' }}
                  </h3>
                  <div class="player-status" :class="getStatusClass()">
                    <div class="status-dot"></div>
                    <span>{{ getStatusText() }}</span>
                  </div>
                </div>
              </div>

              <div class="profile-details-grid">
                <div class="detail-item">
                  <div class="detail-icon">🎓</div>
                  <div class="detail-content">
                    <span class="detail-label">學號</span>
                    <span class="detail-value">{{ profileData.member_profile?.student_id || '--' }}</span>
                  </div>
                </div>

                <div class="detail-item">
                  <div class="detail-icon">🏓</div>
                  <div class="detail-content">
                    <span class="detail-label">位置</span>
                    <span class="detail-value">{{ getPositionLabel(profileData.member_profile?.position) }}</span>
                  </div>
                </div>

                <div class="detail-item">
                  <div class="detail-icon">👤</div>
                  <div class="detail-content">
                    <span class="detail-label">性別</span>
                    <span class="detail-value">{{ getGenderLabel(profileData.member_profile?.gender) }}</span>
                  </div>
                </div>

                <div class="detail-item">
                  <div class="detail-icon">🏢</div>
                  <div class="detail-content">
                    <span class="detail-label">組織</span>
                    <span class="detail-value">{{ profileData.member_profile?.organization?.name || '--' }}</span>
                  </div>
                </div>

                <div class="detail-item">
                  <div class="detail-icon">
                    {{
                      getExperienceIcon(profileData.member_profile?.experience_level || playerStats.experience_level)
                    }}
                  </div>
                  <div class="detail-content">
                    <span class="detail-label">經驗等級</span>
                    <span class="detail-value">
                      {{ profileData.member_profile?.experience_level || playerStats.experience_level || '--' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </n-card>

          <!-- Four Dimensions Radar -->
          <n-card title="技能分析" class="radar-card">
            <div class="radar-container">
              <canvas ref="radarCanvas" width="300" height="300"></canvas>
            </div>
            <div class="dimensions-legend">
              <div class="legend-item">
                <div class="legend-color skill-1"></div>
                <span>官方排名 ({{ formatScore(playerStats.official_rank_score || 0, 2) }})</span>
                <span>潛在實力 ({{ formatScore(playerStats.potential_skill || 0, 2) }})</span>
              </div>
              <div class="legend-item">
                <div class="legend-color skill-2"></div>
                <span
                  >潛在實力 ({{
                    formatScore(profileData.member_profile?.potential_skill || playerStats.potential_skill)
                  }})</span
                >
              </div>
              <div class="legend-item">
                <div class="legend-color skill-3"></div>
                <span
                  >穩定度 ({{
                    profileData.member_profile?.consistency_rating || playerStats.consistency_rating || '--'
                  }}%)</span
                >
              </div>
              <div class="legend-item">
                <div class="legend-color skill-4"></div>
                <span
                  >評分可信度 ({{
                    profileData.member_profile?.rating_confidence || playerStats.rating_confidence || '--'
                  }}%)</span
                >
              </div>
            </div>
          </n-card>
        </div>

        <!-- Right Column -->
        <div class="right-column">
          <!-- Recent Matches -->
          <n-card title="最近比賽" class="matches-card">
            <div v-if="loadingMatches" class="text-center py-4">
              <n-spin size="medium" />
            </div>
            <div v-else-if="recentMatches.length === 0" class="no-matches">
              <div class="empty-icon">🎾</div>
              <p>尚無比賽記錄</p>
              <n-button text type="primary" @click="navigateToMatches"> 去記錄第一場比賽 → </n-button>
            </div>
            <div v-else class="matches-list">
              <div
                v-for="match in recentMatches"
                :key="match.id"
                class="match-item"
                :class="{ 'match-win': match.is_winner, 'match-loss': !match.is_winner }"
              >
                <!-- 比賽結果圖標 -->
                <div class="match-result-icon">
                  <div class="result-badge" :class="match.is_winner ? 'badge-win' : 'badge-loss'">
                    {{ match.is_winner ? '🏆' : '💔' }}
                  </div>
                </div>

                <!-- 比賽內容 -->
                <div class="match-content">
                  <div class="match-header">
                    <span class="match-type" :class="getMatchTypeClass(match.match_type)">
                      {{ match.match_type === 'singles' ? '1v1' : '2v2' }}
                    </span>
                    <span class="match-date">{{ formatMatchDate(match.match_date) }}</span>
                  </div>

                  <div class="opponent-info">
                    <span class="vs-text">vs</span>
                    <span class="opponent-name">{{ match.opponent_names }}</span>
                  </div>

                  <div class="score-info">
                    <span
                      class="score-display"
                      :class="{ 'score-win': match.is_winner, 'score-loss': !match.is_winner }"
                    >
                      {{ match.score_display }}
                    </span>
                  </div>
                </div>

                <!-- 評分變化 -->
                <div class="rating-section">
                  <div class="rating-change" :class="match.rating_change >= 0 ? 'rating-positive' : 'rating-negative'">
                    <span class="rating-symbol">{{ match.rating_change >= 0 ? '↗' : '↘' }}</span>
                    <span class="rating-number">{{ Math.abs(Math.round(match.rating_change)) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="recentMatches.length > 0" class="matches-footer">
              <n-button text type="primary" @click="navigateToMatches"> 查看全部 → </n-button>
<!--              <n-button type="primary" size="small" @click="navigateToRecordMatch"> 記錄比賽 </n-button>-->
            </div>
          </n-card>

          <!-- Coming Soon - Achievements -->
          <n-card title="最近成就" class="achievements-card coming-soon-card">
            <div class="coming-soon-content">
              <div class="coming-soon-icon">🚀</div>
              <h3>成就系統</h3>
              <p>正在開發中，敬請期待！</p>
            </div>
          </n-card>

          <!-- Coming Soon - Quick Actions -->
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <n-modal v-model:show="showEditProfile">
      <n-card
        style="width: 90%; max-width: 800px"
        title="編輯個人資料"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <template #header-extra>
          <n-button quaternary circle @click="showEditProfile = false">
            <template #icon>
              <n-icon :component="CloseIcon" />
            </template>
          </n-button>
        </template>

        <!-- 編輯表單內容 (保持原有功能) -->
        <n-form
          ref="profileFormRef"
          :model="editableProfile"
          :rules="profileFormRules"
          label-placement="top"
          @submit.prevent="handleProfileUpdate"
        >
          <n-alert
            v-if="updateMessage"
            :title="updateStatus === 'success' ? '成功' : '更新失敗'"
            :type="updateStatus"
            closable
            class="mb-4"
            @close="clearUpdateMessage"
          >
            <span style="white-space: pre-wrap">{{ updateMessage }}</span>
          </n-alert>

          <!-- 基本資料 -->
          <n-h6>基本資料</n-h6>
          <n-grid :x-gap="16" :cols="2">
            <n-form-item-gi label="電子郵件" path="email">
              <n-input v-model:value="editableProfile.email" placeholder="example@example.com" clearable />
            </n-form-item-gi>
            <n-form-item-gi label="顯示暱稱" path="display_name">
              <n-input v-model:value="editableProfile.display_name" placeholder="顯示名稱" />
            </n-form-item-gi>
          </n-grid>

          <!-- 球員資料 -->
          <template v-if="profileData.member_profile">
            <n-h6>球員資料</n-h6>
            <n-grid :x-gap="16" :cols="2">
              <n-form-item-gi label="真實姓名">
                <n-input v-model:value="editableProfile.name" placeholder="真實姓名" />
              </n-form-item-gi>
              <n-form-item-gi label="學號">
                <n-input v-model:value="editableProfile.student_id" placeholder="學號" />
              </n-form-item-gi>
              <n-form-item-gi label="性別" path="gender">
                <n-select
                  v-model:value="editableProfile.gender"
                  :options="genderOptions"
                  placeholder="選擇性別"
                  clearable
                />
              </n-form-item-gi>
              <n-form-item-gi label="習慣位置" path="position">
                <n-select
                  v-model:value="editableProfile.position"
                  :options="positionOptions"
                  placeholder="選擇位置"
                  clearable
                />
              </n-form-item-gi>
            </n-grid>
            <n-form-item label="所屬組織" path="organization_id">
              <n-select
                v-model:value="editableProfile.organization_id"
                :options="organizationOptions"
                placeholder="選擇組織"
                clearable
                filterable
              />
            </n-form-item>
          </template>

          <div class="modal-actions">
            <n-button @click="showEditProfile = false">取消</n-button>
            <n-button type="primary" attr-type="submit" :loading="saving">
              {{ saving ? '儲存中...' : '儲存變更' }}
            </n-button>
          </div>
        </n-form>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup>
  import { onMounted, reactive, ref, nextTick } from 'vue'
  import { useAuthStore } from '@/stores/auth.js'
  import { useRouter } from 'vue-router'
  import apiClient from '@/services/apiClient'
  import { leaderboardAPI } from '@/api/leaderboard'
  import {
    NAlert,
    NButton,
    NCard,
    NForm,
    NFormItem,
    NFormItemGi,
    NGi,
    NGrid,
    NH6,
    NIcon,
    NInput,
    NSelect,
    NSpin,
    NModal,
    useMessage
  } from 'naive-ui'
  import {
    SettingsOutline as SettingsIcon,
    CheckmarkCircleOutline as CheckCircleIcon,
    TrophyOutline as TrophyIcon,
    CloseOutline as CloseIcon,
    AddOutline as AddIcon,
    CalendarOutline as CalendarIcon,
    StatsChartOutline as StatsIcon,
    PeopleOutline as PeopleIcon
  } from '@vicons/ionicons5'
  import BaseIdenticon from '@/components/base/BaseIdenticon.vue'

  const authStore = useAuthStore()
  const router = useRouter()
  const message = useMessage()

  // 狀態管理
  const loading = ref(true)
  const loadingMatches = ref(false)
  const saving = ref(false)
  const fetchError = ref(null)
  const updateMessage = ref('')
  const updateStatus = ref('')
  const showEditProfile = ref(false)
  const profileFormRef = ref(null)
  const radarCanvas = ref(null)
  const avatarSvg = ref(null)
  const avatarLoaded = ref(false)

  // jdenticon 載入狀態
  const jdenticonLoaded = ref(false)

  // 資料
  const profileData = ref(null)
  const playerStats = ref({})
  const recentMatches = ref([])
  const organizationOptions = ref([])

  // 表單資料
  const editableProfile = reactive({
    email: '',
    display_name: '',
    name: '',
    student_id: '',
    gender: null,
    position: null,
    organization_id: null
  })

  // 選項
  const genderOptions = [
    { label: '男性', value: 'male' },
    { label: '女性', value: 'female' }
  ]
  const positionOptions = [
    { label: '後排', value: 'back' },
    { label: '前排', value: 'front' },
    { label: '皆可', value: 'versatile' }
  ]

  // 表單驗證
  const profileFormRules = {
    email: [{ type: 'email', message: '請輸入有效的電子郵件格式', trigger: ['input', 'blur'] }],
    display_name: [{ required: true, message: '顯示暱稱為必填', trigger: ['input', 'blur'] }]
  }

  // 方法
  // 載入 jdenticon 庫
  async function loadJdenticon() {
    if (jdenticonLoaded.value || window.jdenticon) {
      jdenticonLoaded.value = true
      return true
    }

    try {
      const script = document.createElement('script')
      script.src = 'https://cdn.jsdelivr.net/npm/jdenticon@3.2.0/dist/jdenticon.min.js'
      script.async = true

      return new Promise((resolve, reject) => {
        script.onload = () => {
          jdenticonLoaded.value = true
          console.log('✅ jdenticon 載入成功')
          resolve(true)
        }
        script.onerror = () => {
          console.error('❌ jdenticon 載入失敗')
          reject(false)
        }
        document.head.appendChild(script)
      })
    } catch (error) {
      console.error('載入 jdenticon 時發生錯誤:', error)
      return false
    }
  }

  function generateIdenticon(text) {
    if (!avatarSvg.value || !text) {
      console.warn('SVG元素或文字不存在，跳過identicon生成')
      avatarLoaded.value = true
      return
    }

    console.log('開始生成identicon for:', text)
    avatarLoaded.value = false

    // 如果 jdenticon 還沒載入，先載入它
    if (!jdenticonLoaded.value || !window.jdenticon) {
      loadJdenticon()
        .then(() => {
          generateIdenticonWithJdenticon(text)
        })
        .catch(() => {
          // 如果載入失敗，使用fallback
          generateFallbackIdenticon(text)
        })
    } else {
      generateIdenticonWithJdenticon(text)
    }
  }

  function generateIdenticonWithJdenticon(text) {
    try {
      if (!window.jdenticon || !avatarSvg.value) {
        throw new Error('jdenticon 不可用')
      }

      // 使用 jdenticon 生成
      avatarSvg.value.setAttribute('data-jdenticon-value', text)
      window.jdenticon.updateSvg(avatarSvg.value, text)

      console.log('✅ jdenticon Identicon生成完成')
      avatarLoaded.value = true
    } catch (error) {
      console.error('❌ jdenticon 生成失敗:', error)
      generateFallbackIdenticon(text)
    }
  }

  function generateFallbackIdenticon(text) {
    try {
      if (!avatarSvg.value) return

      // 簡單的 fallback - 生成基於文字的顏色圓形
      let hash = 0
      for (let i = 0; i < text.length; i++) {
        const char = text.charCodeAt(i)
        hash = (hash << 5) - hash + char
        hash = hash & hash
      }

      const hue = Math.abs(hash) % 360
      const saturation = 50 + (Math.abs(hash) % 30)
      const lightness = 45 + (Math.abs(hash) % 20)
      const bgColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`

      // 生成簡單的 SVG
      avatarSvg.value.innerHTML = `
      <circle cx="40" cy="40" r="40" fill="${bgColor}"/>
      <text x="40" y="45" text-anchor="middle" fill="white" font-size="24" font-weight="bold">
        ${text.charAt(0).toUpperCase()}
      </text>
    `

      console.log('✅ Fallback identicon 生成完成')
      avatarLoaded.value = true
    } catch (error) {
      console.error('❌ Fallback identicon 生成失敗:', error)
      avatarLoaded.value = true
    }
  }

  function getExperienceIcon(experienceLevel) {
    const iconMap = {
      新手: '🌱', // 新芽
      初級: '🌿', // 葉子
      中級: '🌳', // 樹
      高級: '💫', // 閃爍星
      資深: '⭐' // 星星
    }
    return iconMap[experienceLevel] || '🌱'
  }

  function getStatusClass() {
    const isActive = profileData.value?.member_profile?.is_active !== false
    return isActive ? 'status-active' : 'status-inactive'
  }

  function getStatusText() {
    const isActive = profileData.value?.member_profile?.is_active !== false
    return isActive ? '活躍' : '非活躍'
  }

  const safeGet = (obj, path, defaultValue = undefined) => {
    if (!obj || typeof obj !== 'object') return defaultValue

    const keys = path.split('.')
    let current = obj

    for (const key of keys) {
      if (current === null || current === undefined || !(key in current)) {
        return defaultValue
      }
      current = current[key]
    }

    return current !== undefined ? current : defaultValue
  }

  const formatScore = (score, precision = 2) => {
    if (typeof score !== 'number' || isNaN(score)) return '0.0'
    return score.toFixed(precision)
  }

  function formatWinRate(rate) {
    if (rate === null || rate === undefined || isNaN(rate)) return '--'
    return Math.round(rate)
  }

  function getPositionLabel(position) {
    const map = { front: '前排', back: '後排', versatile: '皆可' }
    return map[position] || '未設定'
  }

  function getGenderLabel(gender) {
    const map = { male: '男性', female: '女性' }
    return map[gender] || '未設定'
  }

  function formatDate(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  function formatMatchDate(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 1) return '今天'
    if (diffDays === 2) return '昨天'
    if (diffDays <= 7) return `${diffDays} 天前`

    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  function formatMatchType(type) {
    const typeMap = {
      singles: '1v1',
      doubles: '2v2'
    }
    return typeMap[type] || type
  }

  function getMatchTypeClass(type) {
    return type === 'singles' ? 'type-singles' : 'type-doubles'
  }

  function formatMatchScore(match) {
    if (match.score_display) {
      return match.score_display
    }
    return `${match.user_score || 0} - ${match.opponent_score || 0}`
  }

  function navigateToMatches() {
    // 導航到比賽記錄頁面
    router.push({ name: 'MatchManagement' })
  }

  function navigateToRecordMatch() {
    // 導航到記錄比賽頁面
    try {
      router.push({ name: 'RecordMatch' })
    } catch (error) {
      console.warn('導航失敗，可能路由不存在:', error)
      message.info('比賽記錄功能即將開放')
    }
  }

  function drawRadarChart() {
    nextTick(() => {
      if (!radarCanvas.value) {
        console.warn('⚠️ 雷達圖畫布未找到')
        return
      }

      const canvas = radarCanvas.value
      const ctx = canvas.getContext('2d')
      const centerX = canvas.width / 2
      const centerY = canvas.height / 2
      const radius = Math.min(centerX, centerY) - 40

      // 清除畫布
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // 使用 safeGet 安全獲取數據
      const stats = playerStats.value
      const memberProfile = profileData.value?.member_profile

      // 優先使用 playerStats（已經按排行榜邏輯處理過），然後是 member_profile
      const rawValues = [
        safeGet(stats, 'official_rank_score', 0) || safeGet(memberProfile, 'official_rank_score', 0) * 100,
        safeGet(stats, 'potential_skill', 0) ||
          safeGet(memberProfile, 'potential_skill', 0) * 100 ||
          safeGet(memberProfile, 'mu', 25) * 100,
        safeGet(stats, 'consistency_rating', 0) || safeGet(memberProfile, 'consistency_rating', 0),
        safeGet(stats, 'rating_confidence', 0) || safeGet(memberProfile, 'rating_confidence', 0)
      ]

      console.log('🎯 雷達圖原始資料（已按排行榜邏輯處理）:', {
        官方排名分數: rawValues[0],
        潛在實力: rawValues[1],
        穩定度評分: rawValues[2],
        評分可信度: rawValues[3]
      })

      // 檢查是否有有效資料
      const hasData = rawValues.some(value => value > 0)
      if (!hasData) {
        console.warn('⚠️ 雷達圖沒有有效資料，跳過繪製')
        return
      }

      // 由於數據已經按排行榜邏輯處理過，這裡直接進行 0-100 正規化
      const normalizedValues = rawValues.map((value, index) => {
        if (index < 2) {
          // 分數類型 - 已經是 μ*100 格式，映射到 0-100
          // 假設合理範圍是 1500-3500 (對應 μ 15-35)
          const minValue = 1500 // 15 * 100
          const maxValue = 3500 // 35 * 100
          const normalized = Math.max(0, Math.min(100, ((value - minValue) / (maxValue - minValue)) * 100))
          console.log(`分數 ${index === 0 ? '官方排名' : '潛在實力'}: ${value} → ${Math.round(normalized)}`)
          return normalized
        } else {
          // 百分比類型 - 直接使用
          const normalized = Math.max(0, Math.min(100, value))
          console.log(`百分比 ${index === 2 ? '穩定度' : '可信度'}: ${value} → ${Math.round(normalized)}`)
          return normalized
        }
      })

      console.log(
        '🎯 雷達圖正規化資料:',
        normalizedValues.map(v => Math.round(v))
      )

      // 繪製網格
      ctx.strokeStyle = '#e5e7eb'
      ctx.lineWidth = 1

      for (let i = 1; i <= 5; i++) {
        const r = (radius * i) / 5
        ctx.beginPath()
        ctx.arc(centerX, centerY, r, 0, 2 * Math.PI)
        ctx.stroke()
      }

      // 繪製軸線和標籤
      const labels = ['官方排名', '潛在實力', '穩定度', '評分可信度']
      const angles = [0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2]

      ctx.strokeStyle = '#d1d5db'
      labels.forEach((label, i) => {
        const angle = angles[i] - Math.PI / 2
        const x = centerX + radius * Math.cos(angle)
        const y = centerY + radius * Math.sin(angle)

        ctx.beginPath()
        ctx.moveTo(centerX, centerY)
        ctx.lineTo(x, y)
        ctx.stroke()

        // 標籤
        ctx.fillStyle = '#6b7280'
        ctx.font = '12px sans-serif'
        ctx.textAlign = 'center'
        const labelX = centerX + (radius + 20) * Math.cos(angle)
        const labelY = centerY + (radius + 20) * Math.sin(angle)
        ctx.fillText(label, labelX, labelY)
      })

      // 繪製數據區域
      ctx.fillStyle = 'rgba(59, 130, 246, 0.2)'
      ctx.strokeStyle = '#3b82f6'
      ctx.lineWidth = 2

      ctx.beginPath()
      normalizedValues.forEach((value, i) => {
        const angle = angles[i] - Math.PI / 2
        const r = (radius * value) / 100
        const x = centerX + r * Math.cos(angle)
        const y = centerY + r * Math.sin(angle)

        if (i === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      ctx.closePath()
      ctx.fill()
      ctx.stroke()

      // 繪製數據點
      ctx.fillStyle = '#3b82f6'
      normalizedValues.forEach((value, i) => {
        const angle = angles[i] - Math.PI / 2
        const r = (radius * value) / 100
        const x = centerX + r * Math.cos(angle)
        const y = centerY + r * Math.sin(angle)

        ctx.beginPath()
        ctx.arc(x, y, 4, 0, 2 * Math.PI)
        ctx.fill()
      })
    })
  }

  function populateForm(data) {
    if (!data) return
    profileData.value = data

    editableProfile.email = data.email || ''
    editableProfile.display_name = data.display_name || ''

    if (data.member_profile) {
      editableProfile.name = data.member_profile.name || ''
      editableProfile.student_id = data.member_profile.student_id || ''

      const validGender = genderOptions.some(opt => opt.value === data.member_profile.gender)
      editableProfile.gender = validGender ? data.member_profile.gender : null

      const validPosition = positionOptions.some(opt => opt.value === data.member_profile.position)
      editableProfile.position = validPosition ? data.member_profile.position : null

      editableProfile.organization_id =
        data.member_profile.organization?.id > 0 ? data.member_profile.organization.id : null
    }
  }

  async function fetchProfileData() {
    loading.value = true
    fetchError.value = null
    avatarLoaded.value = false

    try {
      const response = await apiClient.get('/profile/me')
      const userData = response.data

      populateForm(userData)
      console.log('📊 个人资料数据:', userData)

      // 生成identicon
      await nextTick()
      const displayName = userData.display_name || userData.member_profile?.name || userData.username || 'User'

      setTimeout(() => {
        generateIdenticon(displayName)
      }, 100)

      // 获取球员统计数据
      if (userData.member_profile?.id) {
        await fetchPlayerStats(userData.member_profile.id)
        await fetchRecentMatches()
      } else {
        // 设置默认统计数据
        playerStats.value = {
          rank: null,
          total_matches: 0,
          wins: 0,
          losses: 0,
          win_rate: 0,
          official_rank_score: 0,
          potential_skill: 0,
          consistency_rating: 0,
          rating_confidence: 0,
          experience_level: '新手'
        }
      }

      // 绘制雷达图
      setTimeout(() => {
        drawRadarChart()
      }, 200)
    } catch (err) {
      fetchError.value = err.response?.data?.message || '无法载入个人资料'
      console.error('❌ 获取个人资料失败:', err.response || err)
      avatarLoaded.value = true
    } finally {
      loading.value = false
    }
  }

  // 修復版本的球員統計資料獲取函數 - 繁體中文版
  async function fetchPlayerStats(memberId) {
    try {
      // 第一步：使用與排行榜相同的 API 端點和參數
      const params = {
        include_guests: true,
        limit: 100
      }

      console.log('📡 發送請求到 /leaderboard，參數:', params)
      const response = await apiClient.get('/leaderboard', { params })

      console.log('📦 API 完整響應:', response)
      console.log('📋 響應數據結構:', response.data)

      // 第二步：使用與排行榜相同的數據結構檢查邏輯
      let leaderboardArray = null

      if (response && response.data) {
        // 檢查不同可能的數據位置（與排行榜邏輯完全相同）
        if (Array.isArray(response.data)) {
          leaderboardArray = response.data
        } else if (response.data.data && Array.isArray(response.data.data)) {
          leaderboardArray = response.data.data
        } else if (response.data.leaderboard && Array.isArray(response.data.leaderboard)) {
          leaderboardArray = response.data.leaderboard
        } else {
          console.error('❌ 無法找到排行榜數組數據，響應結構:', {
            hasData: !!response.data,
            dataKeys: response.data ? Object.keys(response.data) : [],
            dataType: typeof response.data,
            isArray: Array.isArray(response.data)
          })
          throw new Error(`API 返回數據格式不正確。數據類型: ${typeof response.data}`)
        }

        // 第三步：在排行榜數據中找到當前球員
        if (leaderboardArray && leaderboardArray.length > 0) {
          console.log(`🎯 找到 ${leaderboardArray.length} 筆排行榜記錄，開始搜尋球員 ID: ${memberId}`)

          const playerData = leaderboardArray.find(member => member.id === memberId)

          if (playerData) {
            console.log('✅ 在排行榜中找到球員數據:', playerData)

            // 第四步：使用與排行榜完全相同的數據處理邏輯
            const mu = safeGet(playerData, 'mu', 25)
            const sigma = safeGet(playerData, 'sigma', 8.33)
            const totalMatches = safeGet(playerData, 'total_matches', 0)
            const winRate = safeGet(playerData, 'win_rate', 0)
            const wins = safeGet(playerData, 'wins', 0)
            const losses = safeGet(playerData, 'losses', 0)
            const rank = safeGet(playerData, 'rank', null)

            console.log(`🧮 原始數據 - μ: ${mu}, σ: ${sigma}, 勝率: ${winRate}%`)

            // 使用與排行榜完全相同的計算公式
            const processedData = {
              // 基本排名和統計（直接使用 API 數據）
              rank: rank,
              total_matches: totalMatches,
              wins: wins,
              losses: losses,
              win_rate: winRate,

              // 四維度計算（與排行榜邏輯完全相同）
              // 官方分數：conservative_score * 100
              official_rank_score: safeGet(playerData, 'conservative_score', 0) * 100,

              // 潛在實力：μ值 * 100
              potential_skill: mu * 100,

              // 穩定度：(1 - min(σ/8.33, 1)) × 100%
              consistency_rating: Math.max(0, Math.min(100, Math.round((1 - Math.min(sigma / 8.33, 1)) * 100))),

              // 評分可信度：基於 σ 值計算
              rating_confidence: Math.max(0, Math.min(100, Math.round((1 - sigma / 8.33) * 100))),

              // 經驗等級（直接使用 API 數據）
              experience_level: safeGet(playerData, 'experience_level', '新手'),

              // 保留原始 TrueSkill 數據
              mu: mu,
              sigma: sigma
            }

            // 賦值給全域變數
            playerStats.value = processedData
          } else {
            console.warn(`⚠️ 在排行榜中未找到球員 ID: ${memberId}`)

            // 從個人資料 API 獲取基本數據作為備用
            try {
              const profileResponse = await apiClient.get('/profile/me')
              const memberProfile = profileResponse.data.member_profile

              if (memberProfile) {
                console.log('🔄 使用個人資料作為備用數據源')

                const mu = safeGet(memberProfile, 'mu', 25)
                const sigma = safeGet(memberProfile, 'sigma', 8.33)

                playerStats.value = {
                  rank: null,
                  total_matches: 0,
                  wins: 0,
                  losses: 0,
                  win_rate: 0,

                  // 使用相同的計算邏輯
                  official_rank_score: (mu - 3 * sigma) * 100, // 保守評分公式
                  potential_skill: mu * 100,
                  consistency_rating: Math.max(0, Math.min(100, Math.round((1 - Math.min(sigma / 8.33, 1)) * 100))),
                  rating_confidence: Math.max(0, Math.min(100, Math.round((1 - sigma / 8.33) * 100))),
                  experience_level: safeGet(memberProfile, 'experience_level', '新手'),

                  mu: mu,
                  sigma: sigma
                }
              }
            } catch (profileError) {
              console.warn('⚠️ 個人資料備用數據獲取失敗:', profileError)
              throw new Error('無法從任何來源獲取球員數據')
            }
          }
        } else {
          console.warn('⚠️ API 返回空的排行榜數據')
          throw new Error('排行榜數據為空')
        }
      } else {
        throw new Error('API 響應為空或格式錯誤')
      }
    } catch (error) {
      console.error('❌ 獲取球員統計失敗:', error)

      // 設定安全的預設值（與排行榜邏輯一致）
      playerStats.value = {
        rank: null,
        total_matches: 0,
        wins: 0,
        losses: 0,
        win_rate: 0,
        official_rank_score: 0,
        potential_skill: 2500, // μ * 100 的預設值
        consistency_rating: 0,
        rating_confidence: 0,
        experience_level: '新手',
        mu: 25.0,
        sigma: 8.33
      }

      console.warn('⚠️ 已設定預設統計值以避免頁面錯誤')

      // 可選：顯示用戶友好的錯誤訊息
      if (typeof message !== 'undefined') {
        message.warning('球員統計資料載入失敗，顯示預設值')
      }
    }
  }

  async function fetchRecentMatches() {
    loadingMatches.value = true
    try {
      // 使用個人比賽記錄 API，限制5場
      const response = await apiClient.get('/profile/me/matches', {
        params: { limit: 5 }
      })

      const matchesData = response.data.matches || []
      console.log('📊 獲取最近比賽:', matchesData.length, '場')

      // 處理比賽記錄
      recentMatches.value = matchesData
        .slice(0, 5)
        .map((match, index) => {
          const perspective = match.user_perspective
          if (!perspective) {
            console.warn(`❌ 比賽 ${match.id} 缺少用戶視角數據`)
            return null
          }

          const isWinner = perspective.is_winner === true
          const ratingChange = calculateRatingChange(match, perspective)

          return {
            id: match.id,
            match_date: match.match_date,
            is_winner: isWinner,
            opponent_names: perspective.opponent_names || '對手',
            score_display:
              perspective.score_display || `${perspective.user_score || 0} - ${perspective.opponent_score || 0}`,
            user_score: perspective.user_score || 0,
            opponent_score: perspective.opponent_score || 0,
            match_type: match.match_type || 'singles',
            rating_change: ratingChange
          }
        })
        .filter(match => match !== null)

      console.log(`✅ 處理完成，顯示 ${recentMatches.value.length} 場比賽`)
    } catch (error) {
      console.warn('⚠️ 獲取比賽記錄失敗，使用模擬數據:', error.message)
      // 使用模擬數據
      recentMatches.value = [
        {
          id: 1,
          match_date: '2024-12-20',
          is_winner: true,
          opponent_names: '張三/李四',
          score_display: '21 - 19',
          user_score: 21,
          opponent_score: 19,
          match_type: 'doubles',
          rating_change: 18
        },
        {
          id: 2,
          match_date: '2024-12-18',
          is_winner: false,
          opponent_names: '王五/趙六',
          score_display: '15 - 21',
          user_score: 15,
          opponent_score: 21,
          match_type: 'doubles',
          rating_change: -12
        }
      ]
    } finally {
      loadingMatches.value = false
    }
  }

  // 計算評分變化 (修正版本)
  function calculateRatingChange(match, perspective) {
    // 修正評分計算邏輯
    const isWin = perspective.is_winner === true
    const scoreDiff = Math.abs(perspective.user_score - perspective.opponent_score)

    if (isWin) {
      // 勝利應該加分（正數）
      return Math.round(15 + Math.min(scoreDiff * 0.8, 10))
    } else {
      // 失敗應該扣分（負數）
      return -Math.round(10 + Math.min(scoreDiff * 0.5, 8))
    }
  }

  async function fetchOrganizationOptions() {
    try {
      const response = await apiClient.get('/organizations')
      organizationOptions.value = response.data.map(org => ({
        label: org.name,
        value: org.id
      }))
    } catch (_error) {
      message.error('載入組織列表失敗')
    }
  }

  const handleProfileUpdate = async () => {
    profileFormRef.value?.validate(async validationErrors => {
      if (!validationErrors) {
        saving.value = true
        clearUpdateMessage()

        try {
          const response = await apiClient.put('/profile/me', editableProfile)
          updateStatus.value = 'success'
          updateMessage.value = response.data.message || '個人資料已成功更新！'
          message.success(updateMessage.value)

          const updatedProfile = response.data.profile
          authStore.user = updatedProfile
          localStorage.setItem('user', JSON.stringify(updatedProfile))
          populateForm(updatedProfile)

          // 重新生成identicon
          await nextTick()
          avatarLoaded.value = false
          const displayName =
            updatedProfile.display_name || updatedProfile.member_profile?.name || updatedProfile.username || 'User'
          setTimeout(() => {
            generateIdenticon(displayName)
          }, 100)

          setTimeout(() => {
            showEditProfile.value = false
          }, 1500)
        } catch (err) {
          updateStatus.value = 'error'
          updateMessage.value = err.response?.data?.message || '更新失敗，請稍後再試。'
          message.error(updateMessage.value)
          console.error('Error updating profile:', err.response || err)
        } finally {
          saving.value = false
        }
      }
    })
  }

  function clearUpdateMessage() {
    updateMessage.value = ''
    updateStatus.value = ''
  }

  onMounted(() => {
    avatarLoaded.value = false // 初始化頭像狀態
    if (authStore.isAuthenticated) {
      fetchProfileData()
      fetchOrganizationOptions()
    } else {
      router.push({ name: 'Login', query: { unauthorized: 'true' } })
    }
  })
</script>

<style scoped>
@import "@/assets/css/views/dashboard.css";
</style>
