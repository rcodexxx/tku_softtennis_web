<template>
  <div class="home-leaderboard-page">
    <div class="leaderboard-content-wrapper">
      <!-- 頁面標題 -->
      <div class="leaderboard-header mb-4">
        <h1 class="page-title">🏆 淡江軟網排行榜</h1>
        <div class="leaderboard-description">
          <!--          <n-text depth="3" style="font-size: 16px"> 基於 TrueSkill 評分系統的球員實力排名 </n-text>-->
        </div>
      </div>

      <n-spin :show="loading" size="large">
        <template #description>載入排行榜中...</template>

        <!-- 錯誤提示 -->
        <div v-if="!loading && error" class="mt-4">
          <n-alert title="載入失敗" type="error" show-icon>
            {{ error }}
          </n-alert>
        </div>

        <!-- 排行榜統計摘要 -->
        <div v-if="!loading && !error && displayMembers.length > 0" class="stats-summary mb-4 desktop-only">
          <n-card size="small" class="stats-card">
            <div class="stats-row">
              <div class="stat-item">
                <n-statistic label="活躍球員" :value="displayMembers.length" />
              </div>
              <div class="stat-item">
                <n-statistic label="總比賽場次" :value="totalMatches" />
              </div>
              <div class="stat-item">
                <n-statistic label="平均比賽" :value="averageMatches" />
              </div>
            </div>
          </n-card>
        </div>

        <!-- 空狀態 -->
        <div v-if="!loading && !error">
          <n-empty v-if="displayMembers.length === 0" description="目前尚無排行榜資料" class="py-5" size="huge" />

          <!-- 排行榜列表 -->
          <div v-if="displayMembers.length > 0" class="home-leaderboard-list">
            <!-- 在你現有的模板中，替換手機版前三名的部分 -->

            <!-- F1頒獎台風格 (桌面版) - 保持不變 -->
            <div class="f1-podium-desktop desktop-only mb-4">
              <div class="podium-container">
                <!-- 第二名 (左邊) -->
                <div v-if="topThree[1]" class="podium-position position-2">
                  <div class="podium-card rank-2">
                    <div class="rank-icon">
                      <n-icon :component="getRankIconComponent(2)" :size="35" :color="getRankIconColor(2)" />
                    </div>
                    <div class="player-info">
                      <div class="player-name">{{ getPlayerDisplayName(topThree[1]) }}</div>
                      <div v-if="topThree[1].organization_name" class="player-org">
                        {{ topThree[1].organization_name }}
                      </div>
                      <div class="experience-badge">
                        <span class="experience-icon">{{
                          getExperienceIcon(safeGet(topThree[1], 'experience_level'))
                        }}</span>
                        <!--                        <span class="experience-text">{{ safeGet(topThree[1], 'experience_level', '新手') }}</span>-->
                      </div>
                    </div>
                    <div class="score-display">
                      <div class="score-number">
                        {{ formatDisplayScore(safeGet(topThree[1], 'official_rank_score', 0)) }}
                      </div>
                    </div>
                    <div v-if="getWinRate(topThree[1])" class="match-count">{{ getWinRate(topThree[1]) }} %</div>
                  </div>
                  <div class="podium-base podium-base-2"></div>
                </div>

                <!-- 第一名 (中間，最高) -->
                <div v-if="topThree[0]" class="podium-position position-1">
                  <div class="podium-card rank-1">
                    <div class="crown-icon">👑</div>
                    <div class="rank-icon">
                      <n-icon :component="getRankIconComponent(1)" :size="45" :color="getRankIconColor(1)" />
                    </div>
                    <div class="player-info">
                      <div class="player-name">{{ getPlayerDisplayName(topThree[0]) }}</div>
                      <div v-if="topThree[0].organization_name" class="player-org">
                        {{ topThree[0].organization_name }}
                      </div>
                      <div class="experience-badge">
                        <span class="experience-icon">{{
                          getExperienceIcon(safeGet(topThree[0], 'experience_level', '新手'))
                        }}</span>
                        <!--                        <span class="experience-text">{{ safeGet(topThree[0], 'experience_level', '新手') }}</span>-->
                      </div>
                    </div>
                    <div class="score-display">
                      <div class="score-number">
                        {{ formatDisplayScore(safeGet(topThree[0], 'official_rank_score', 0)) }}
                      </div>
                    </div>
                    <div v-if="getWinRate(topThree[0])" class="match-count">{{ getWinRate(topThree[0]) }} %</div>
                  </div>
                  <div class="podium-base podium-base-1"></div>
                </div>

                <!-- 第三名 (右邊) -->
                <div v-if="topThree[2]" class="podium-position position-3">
                  <div class="podium-card rank-3">
                    <div class="rank-icon">
                      <n-icon :component="getRankIconComponent(3)" :size="35" :color="getRankIconColor(3)" />
                    </div>
                    <div class="player-info">
                      <div class="player-name">{{ getPlayerDisplayName(topThree[2]) }}</div>
                      <div v-if="topThree[2].organization_name" class="player-org">
                        {{ topThree[2].organization_name }}
                      </div>
                      <div class="experience-badge">
                        <span class="experience-icon">{{
                          getExperienceIcon(safeGet(topThree[2], 'experience_level', '新手'))
                        }}</span>
                        <!--                        <span class="experience-text">{{ safeGet(topThree[2], 'experience_level', '新手') }}</span>-->
                      </div>
                    </div>
                    <div class="score-display">
                      <div class="score-number">
                        {{ formatDisplayScore(safeGet(topThree[2], 'official_rank_score', 0)) }}
                      </div>
                    </div>
                    <div v-if="getWinRate(topThree[2])" class="match-count">{{ getWinRate(topThree[2]) }} %</div>
                  </div>
                  <div class="podium-base podium-base-3"></div>
                </div>
              </div>
            </div>

            <!-- 手機版統一格式的前三名 -->
            <div class="mobile-unified-top-three mobile-only mb-4">
              <div
                v-for="member in topThree"
                :key="member.id"
                class="mobile-enhanced-rank-card"
                :class="getMobileRankClass(member.rank)"
              >
                <div class="mobile-rank-header">
                  <div class="rank-number-mobile" :class="getRankClass(member.rank)">
                    <n-icon
                      :component="getRankIconComponent(member.rank)"
                      :size="24"
                      :color="getRankIconColor(member.rank)"
                    />
                  </div>
                  <div class="player-info-mobile">
                    <div class="player-name-mobile">{{ getPlayerDisplayName(member) }}</div>
                    <div v-if="member.organization_name" class="player-org-mobile">
                      {{ member.organization_name }}
                    </div>
                  </div>
                  <div class="experience-mobile">
                    {{ getExperienceIcon(safeGet(member, 'experience_level', '新手')) }}
                  </div>
                </div>

                <div class="mobile-rank-stats">
                  <div class="stat-item">
                    <div class="stat-value" :style="{ color: getScoreColor(member.rank) }">
                      {{ formatDisplayScore(safeGet(member, 'official_rank_score', 0)) }}
                    </div>
                    <div class="stat-label">分數</div>
                  </div>

                  <div class="stat-item">
                    <div class="stat-value" :style="{ color: getWinRateColor(getWinRate(member)) }">
                      {{ getWinRate(member) }}%
                    </div>
                    <div class="stat-label">勝率</div>
                  </div>

                  <div class="stat-item">
                    <div class="stat-value">{{ getMatchCount(member) }}</div>
                    <div class="stat-label">比賽</div>
                  </div>
                </div>

                <!--                <div class="mobile-rank-details">-->
                <!--                  <span class="win-loss-record">{{ getWins(member) }}勝 {{ getLosses(member) }}敗</span>-->
                <!--                  <span class="experience-level">{{ safeGet(member, 'experience_level', '新手') }}</span>-->
                <!--                </div>-->
              </div>
            </div>

            <!-- 其他排名 -->
            <div v-if="otherRanks.length > 0" class="other-ranks">
              <!-- 桌面版增強列表 -->
              <n-list class="enhanced-ranking-list desktop-only">
                <n-list-item v-for="member in otherRanks" :key="member.id">
                  <div class="enhanced-rank-item">
                    <!-- 排名區域 -->
                    <div class="rank-section">
                      <div class="rank-number" :class="getRankClass(member.rank)">
                        {{ member.rank }}
                      </div>
                    </div>

                    <!-- 球員信息區域 -->
                    <div class="player-section">
                      <div class="player-name">{{ getPlayerDisplayName(member) }}</div>
                      <div class="player-details">
                        <span v-if="member.organization_name" class="org-name">
                          {{ member.organization_name }}
                        </span>
                        <span class="experience-badge">
                          <span class="experience-icon">{{
                            getExperienceIcon(safeGet(member, 'experience_level', '新手'))
                          }}</span>
                          <!--                          <span class="experience-text">{{ safeGet(member, 'experience_level', '新手') }}</span>-->
                        </span>
                      </div>
                    </div>

                    <!-- 分數區域 -->
                    <div class="score-section">
                      <div class="score-main" :style="{ color: getScoreColor(member.rank) }">
                        {{ formatDisplayScore(safeGet(member, 'official_rank_score', 0)) }}
                      </div>
                      <div class="score-label">分數</div>
                    </div>

                    <!-- 勝率區域 -->
                    <div class="winrate-section">
                      <div class="winrate-main" :style="{ color: getWinRateColor(getWinRate(member)) }">
                        {{ getWinRate(member) }}%
                      </div>
                      <div class="winrate-details">{{ getWins(member) }}勝{{ getLosses(member) }}敗</div>
                    </div>

                    <!-- 比賽信息區域 -->
                    <div class="match-section">
                      <div class="match-count">{{ getMatchCount(member) }}</div>
                      <div class="match-label">場比賽</div>
                    </div>
                  </div>
                </n-list-item>
              </n-list>

              <!-- 手機版增強卡片 (第4名以後) -->
              <div class="enhanced-mobile-rank-list mobile-only">
                <div v-for="member in otherRanks" :key="member.id" class="mobile-enhanced-rank-card">
                  <div class="mobile-rank-header">
                    <div class="rank-number-mobile" :class="getRankClass(member.rank)">
                      {{ member.rank }}
                    </div>
                    <div class="player-info-mobile">
                      <div class="player-name-mobile">{{ getPlayerDisplayName(member) }}</div>
                      <div v-if="member.organization_name" class="player-org-mobile">
                        {{ member.organization_name }}
                      </div>
                    </div>
                    <div class="experience-mobile">
                      {{ getExperienceIcon(safeGet(member, 'experience_level', '新手')) }}
                    </div>
                  </div>

                  <div class="mobile-rank-stats">
                    <div class="stat-item">
                      <div class="stat-value" :style="{ color: getScoreColor(member.rank) }">
                        {{ formatDisplayScore(safeGet(member, 'official_rank_score', 0)) }}
                      </div>
                      <div class="stat-label">分數</div>
                    </div>

                    <div class="stat-item">
                      <div class="stat-value" :style="{ color: getWinRateColor(getWinRate(member)) }">
                        {{ getWinRate(member) }}%
                      </div>
                      <div class="stat-label">勝率</div>
                    </div>

                    <div class="stat-item">
                      <div class="stat-value">{{ getMatchCount(member) }}</div>
                      <div class="stat-label">比賽</div>
                    </div>
                  </div>

                  <!--                  <div class="mobile-rank-details">-->
                  <!--                    <span class="win-loss-record">{{ getWins(member) }}勝 {{ getLosses(member) }}敗</span>-->
                  <!--                    <span class="experience-level">{{ safeGet(member, 'experience_level', '新手') }}</span>-->
                  <!--                  </div>-->
                </div>
              </div>
            </div>

            <!-- 如果沒有有比賽記錄的球員，顯示提示信息 -->
            <div
              v-if="!loading && !error && leaderboardData.length > 0 && activePlayersData.length === 0"
              class="no-matches-info"
            >
              <n-card class="info-card">
                <div class="info-content">
                  <n-icon :component="InfoIcon" size="24" color="#f59e0b" />
                  <div class="info-text">
                    <h3>暫無比賽記錄</h3>
                    <p>系統中共有 {{ leaderboardData.length }} 名球員，但尚無球員有比賽記錄。</p>
                    <p>開始比賽後，排行榜將顯示球員排名。</p>
                  </div>
                </div>
              </n-card>
            </div>
          </div>
        </div>
      </n-spin>
    </div>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import apiClient from '@/services/apiClient.js'
  import { NAlert, NCard, NEmpty, NIcon, NList, NListItem, NSpin, NStatistic } from 'naive-ui'
  import { Medal as Rank3Icon, ShieldSharp as Rank2Icon, TrophySharp as Rank1Icon } from '@vicons/ionicons5'
  import { InformationCircleIcon as InfoIcon } from '@heroicons/vue/24/outline'

  const router = useRouter()

  // 響應式數據
  const leaderboardData = ref([])
  const loading = ref(true)
  const error = ref(null)

  // === 安全訪問和格式化函數 ===
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

  // 獲取球員顯示名稱
  const getPlayerDisplayName = member => {
    return safeGet(member, 'display_name') || safeGet(member, 'name', '未知球員')
  }

  // 獲取經驗等級圖標
  const getExperienceIcon = experienceLevel => {
    const iconMap = {
      新手: '🌱', // 新芽
      初級: '🌿', // 葉子
      中級: '🌳', // 樹
      高級: '💫', // 閃爍星
      資深: '⭐' // 星星
    }
    return iconMap[experienceLevel] || '🌱'
  }

  // 格式化顯示分數 x100
  const formatDisplayScore = score => {
    if (typeof score !== 'number' || isNaN(score)) return '0'
    return Math.round(score * 100).toString()
  }

  // 輔助函數
  const getMatchCount = member => {
    return safeGet(member, 'total_matches', 0)
  }

  const getWins = member => {
    return safeGet(member, 'wins', 0)
  }

  const getLosses = member => {
    return safeGet(member, 'losses', 0)
  }

  const getWinRate = member => {
    return safeGet(member, 'win_rate', 0)
  }

  // === 計算屬性 ===

  const totalMatches = computed(() => {
    return displayMembers.value.reduce((sum, member) => sum + getMatchCount(member), 0)
  })

  const averageMatches = computed(() => {
    if (displayMembers.value.length === 0) return 0
    return Math.round(totalMatches.value / displayMembers.value.length)
  })

  // 只顯示有比賽記錄的球員
  const activePlayersData = computed(() => {
    const MIN_MATCHES = 5

    const filtered = leaderboardData.value.filter(member => {
      const matchCount = getMatchCount(member)
      return matchCount >= MIN_MATCHES // 只顯示達到最少比賽場次的球員
    })

    return filtered.map((member, index) => ({
      ...member,
      rank: index + 1 // 重新計算排名，確保排名連續
    }))
  })

  // 顯示的球員（前50名）
  const displayMembers = computed(() => {
    return activePlayersData.value.slice(0, 50)
  })

  // 前三名
  const topThree = computed(() => {
    return displayMembers.value.slice(0, 3)
  })

  // 其他排名（第4-50名）
  const otherRanks = computed(() => {
    return displayMembers.value.slice(3)
  })

  // === 獲取排行榜數據 ===
  const fetchLeaderboard = async () => {
    loading.value = true
    error.value = null

    try {
      console.log('🏆 獲取排行榜數據...')

      const response = await apiClient.get('/leaderboard', {
        params: {
          per_page: 500,
          include_guests: true
        }
      })

      const data = response.data

      // 處理數據
      if (data && Array.isArray(data)) {
        // 過濾非訪客
        const membersOnly = data.filter(member => !safeGet(member, 'is_guest', false))
        console.log(`🔍 過濾後數量: ${membersOnly.length}`)

        leaderboardData.value = membersOnly.map((member, index) => {
          return {
            ...member,
            official_rank_score: member.conservative_score,
            experience_level: safeGet(member, 'experience_level', ''),
            organization_name: member.organization?.short_name || member.organization?.name || '',

            total_matches: member.total_matches ?? 0,
            wins: member.wins ?? 0,
            losses: member.losses ?? 0,
            win_rate: member.win_rate ?? 0
          }
        })
      } else {
        throw new Error('無有效數據')
      }
    } catch (e) {
      console.error('❌ 排行榜獲取錯誤:', e)
      error.value = e.response?.data?.message || e.message || '載入排行榜時發生錯誤'
      leaderboardData.value = []
    } finally {
      loading.value = false
    }
  }

  // 其他輔助函數保持不變
  const getRankClass = rank => {
    if (rank <= 10) return 'rank-top-10'
    if (rank <= 20) return 'rank-top-20'
    if (rank <= 50) return 'rank-top-50'
    return ''
  }

  const getScoreColor = rank => {
    if (rank === 1) return '#B8860B'
    if (rank === 2) return '#696969'
    if (rank === 3) return '#8B4513'
    if (rank <= 10) return '#f59e0b'
    if (rank <= 20) return '#3b82f6'
    if (rank <= 50) return '#10b981'
    return '#1f2937'
  }

  const getWinRateColor = winRate => {
    if (winRate >= 80) return '#22c55e'
    if (winRate >= 70) return '#84cc16'
    if (winRate >= 60) return '#f59e0b'
    if (winRate >= 50) return '#ef4444'
    if (winRate > 0) return '#6b7280'
    return '#9ca3af'
  }

  const getMobileRankClass = rank => {
    if (rank === 1) return 'mobile-rank-1'
    if (rank === 2) return 'mobile-rank-2'
    if (rank === 3) return 'mobile-rank-3'
    return ''
  }

  function getRankIconComponent(rank) {
    if (rank === 1) return Rank1Icon
    if (rank === 2) return Rank2Icon
    if (rank === 3) return Rank3Icon
    return null
  }

  function getRankIconColor(rank) {
    if (rank === 1) return '#FFD700'
    if (rank === 2) return '#C0C0C0'
    if (rank === 3) return '#CD7F32'
    return undefined
  }

  // 生命週期
  onMounted(fetchLeaderboard)
</script>

<style scoped>
  .home-leaderboard-page {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 2rem 1rem;
  }

  .leaderboard-content-wrapper {
    max-width: 1000px;
    margin: 0 auto;
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  }

  .page-title {
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
  }

  .leaderboard-description {
    text-align: center;
    margin-bottom: 2rem;
    color: #6b7280;
  }

  /* 統計摘要 */
  .stats-summary {
    margin-bottom: 2rem;
  }

  .stats-card {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  }

  .stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 2rem;
    text-align: center;
  }

  /* F1頒獎台風格 (桌面版) */
  .f1-podium-desktop {
    perspective: 1000px;
    margin-bottom: 2rem;
  }

  .podium-container {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 0;
    padding: 2rem 0;
    position: relative;
    max-width: 780px;
    margin: 0 auto;
  }

  .podium-position {
    position: relative;
    width: 260px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  /* 2-1-3 排列 */
  .position-1 {
    order: 2;
  }

  .position-2 {
    order: 1;
  }

  .position-3 {
    order: 3;
  }

  .podium-card {
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 2px solid transparent;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    width: 100%;
    z-index: 2;
    margin-bottom: 8px;
  }

  .rank-1 {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    border: 3px solid #ffd700;
    box-shadow: 0 12px 40px rgba(255, 215, 0, 0.3);
  }

  .rank-2 {
    background: linear-gradient(135deg, #c0c0c0, #e5e5e5);
    border: 3px solid #c0c0c0;
    box-shadow: 0 10px 30px rgba(192, 192, 192, 0.3);
  }

  .rank-3 {
    background: linear-gradient(135deg, #cd7f32, #daa447);
    border: 3px solid #cd7f32;
    box-shadow: 0 8px 25px rgba(205, 127, 50, 0.3);
  }

  /* 頒獎台台階 - 更深的顏色 */
  .podium-base {
    width: 100%;
    border-radius: 8px 8px 0 0;
    position: relative;
    z-index: 1;
    background: linear-gradient(135deg, #94a3b8, #64748b);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
  }

  .podium-base-1 {
    height: 120px;
  }

  .podium-base-2 {
    height: 100px;
  }

  .podium-base-3 {
    height: 80px;
  }

  .crown-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    animation: bounce 2s infinite;
  }

  @keyframes bounce {
    0%,
    20%,
    50%,
    80%,
    100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-10px);
    }
    60% {
      transform: translateY(-5px);
    }
  }

  .podium-card:hover {
    transform: translateY(-4px);
  }

  .rank-icon {
    margin-bottom: 1rem;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .rank-icon .n-icon {
    background: white;
    border-radius: 50%;
    padding: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .player-info {
    margin-bottom: 1rem;
  }

  .player-name {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.25rem;
  }

  .player-org {
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 0.5rem;
  }

  .experience-badge {
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .experience-icon {
    font-size: 1.5rem;
  }

  .experience-text {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
  }

  .experience-icon-small {
    font-size: 1rem;
  }

  .experience-text-small {
    font-size: 0.75rem;
    color: #64748b;
  }

  .experience-mobile {
    font-size: 1.25rem;
    text-align: center;
  }

  .score-display {
    margin-bottom: 0.75rem;
  }

  .score-number {
    font-size: 2rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1;
  }

  .score-label {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
  }

  .score-display {
    margin-bottom: 0.75rem;
  }

  .score-number {
    font-size: 2rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1;
  }

  .match-count {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
  }

  /* 手機版簡潔卡片 */
  .mobile-top-three,
  .mobile-rank-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .mobile-rank-card {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
    width: 100%;
  }

  /* 前三名手機版卡片顏色 */
  .mobile-top-three .mobile-rank-card:nth-child(1) {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    border: 2px solid #ffd700;
  }

  .mobile-top-three .mobile-rank-card:nth-child(2) {
    background: linear-gradient(135deg, #c0c0c0, #e5e5e5);
    border: 2px solid #c0c0c0;
  }

  .mobile-top-three .mobile-rank-card:nth-child(3) {
    background: linear-gradient(135deg, #cd7f32, #daa447);
    border: 2px solid #cd7f32;
  }

  /* 第四名之後白色背景 */
  .mobile-rank-list .mobile-rank-card {
    background: white;
  }

  .mobile-rank-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .mobile-rank-content {
    display: grid;
    grid-template-columns: 50px 1fr auto auto;
    gap: 1rem;
    align-items: center;
    padding: 1rem 1.5rem;
  }

  .rank-icon-mobile {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .rank-icon-mobile .n-icon {
    background: white;
    border-radius: 50%;
    padding: 6px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .rank-number-mobile {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.125rem;
    font-weight: 600;
    color: #64748b;
    background: white;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    margin: 0 auto;
  }

  .player-name-mobile {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .score-mobile {
    font-size: 1rem;
    font-weight: 700;
    color: #1e293b;
    text-align: center;
    min-width: 60px;
  }

  .experience-mobile {
    font-size: 1.25rem;
    text-align: center;
  }

  /* 其他排名 */
  .other-ranks {
    margin-bottom: 2rem;
  }

  .section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
    text-align: center;
  }

  .ranking-list {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  }

  .rank-item {
    display: grid;
    grid-template-columns: 60px 1fr auto;
    gap: 1rem;
    align-items: center;
    padding: 1rem 1.5rem;
    background: white;
    border-bottom: 1px solid #f1f5f9;
    transition: all 0.2s ease;
  }

  .rank-item:hover {
    background: #f8fafc;
  }

  .rank-item:last-child {
    border-bottom: none;
  }

  .rank-number {
    font-size: 1.125rem;
    font-weight: 600;
    color: #64748b;
    text-align: center;
  }

  .player-section {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .player-section .player-name {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
  }

  .player-details {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .org-name {
    font-size: 0.875rem;
    color: #64748b;
  }

  .score-section {
    text-align: right;
  }

  .score-main {
    font-size: 1.125rem;
    font-weight: 700;
    color: #1e293b;
  }

  .match-info {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
  }

  /* 查看更多提示 */
  .view-more-hint {
    margin-top: 2rem;
  }

  .hint-card {
    background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
    border: none;
  }

  .hint-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    text-align: center;
    color: #4338ca;
    font-weight: 500;
  }

  /* 響應式設計 */
  .desktop-only {
    display: block;
  }

  .mobile-only {
    display: none;
  }

  @media (max-width: 768px) {
    .desktop-only {
      display: none;
    }

    .mobile-only {
      display: block;
    }

    .home-leaderboard-page {
      padding: 1rem 0.5rem;
    }

    .leaderboard-content-wrapper {
      padding: 1.5rem;
    }

    .page-title {
      font-size: 2rem;
    }

    .hint-content {
      flex-direction: column;
      gap: 0.75rem;
    }

    .mobile-rank-content {
      grid-template-columns: 50px 1fr auto auto;
      gap: 0.75rem;
    }

    .score-mobile,
    .experience-mobile {
      font-size: 0.875rem;
    }
  }

  @media (max-width: 480px) {
    .mobile-rank-content {
      grid-template-columns: 45px 1fr auto auto;
      gap: 0.5rem;
      padding: 1rem;
    }

    .player-name-mobile {
      font-size: 0.9rem;
    }

    .score-mobile {
      font-size: 0.85rem;
    }

    .experience-mobile {
      font-size: 1.1rem;
    }
  }

  /* === 增強的第四名之後排名樣式 === */

  .section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .section-title .subtitle {
    font-size: 0.875rem;
    font-weight: 500;
    color: #64748b;
    background: #f1f5f9;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
  }

  /* 桌面版增強排名列表 */
  .enhanced-ranking-list {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  }

  .enhanced-rank-item {
    display: grid;
    grid-template-columns: 80px 2fr 120px 140px 100px;
    gap: 1rem;
    align-items: center;
    padding: 1.25rem 1.5rem;
    background: white;
    border-bottom: 1px solid #f1f5f9;
    transition: all 0.2s ease;
  }

  .enhanced-rank-item:hover {
    background: #f8fafc;
    transform: translateY(-1px);
  }

  .enhanced-rank-item:last-child {
    border-bottom: none;
  }

  /* 排名區域 */
  .rank-section {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .rank-number {
    font-size: 1.25rem;
    font-weight: 700;
    color: #64748b;
    text-align: center;
    min-width: 40px;
    padding: 0.5rem;
    border-radius: 8px;
    transition: all 0.2s ease;
  }

  /* 排名顏色 */
  .rank-number.rank-top-10 {
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: white;
  }

  .rank-number.rank-top-20 {
    background: linear-gradient(135deg, #60a5fa, #3b82f6);
    color: white;
  }

  .rank-number.rank-top-50 {
    background: linear-gradient(135deg, #34d399, #10b981);
    color: white;
  }

  /* 球員信息區域 */
  .player-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .player-section .player-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
  }

  .player-details {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .org-name {
    font-size: 0.875rem;
    color: #64748b;
    background: #f1f5f9;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
  }

  .experience-badge {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    background: #e0e7ff;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
  }

  .experience-icon {
    font-size: 0.875rem;
  }

  .experience-text {
    font-size: 0.8rem;
    font-weight: 500;
    color: #4338ca;
  }

  /* 分數區域 */
  .score-section {
    text-align: center;
  }

  .score-main {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
  }

  .score-label {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.25rem;
  }

  /* 勝率區域 */
  .winrate-section {
    text-align: center;
  }

  .winrate-main {
    font-size: 1.25rem;
    font-weight: 700;
  }

  .winrate-details {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.25rem;
  }

  /* 比賽信息區域 */
  .match-section {
    text-align: center;
  }

  .match-count {
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
  }

  .match-label {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.25rem;
  }

  /* 在你現有的 CSS 中，添加這些樣式並移除舊的手機版前三名樣式 */

  /* === 手機版統一格式的前三名 === */
  .mobile-unified-top-three {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  /* 手機版增強卡片 (統一格式) */
  .mobile-enhanced-rank-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #f1f5f9;
    transition: all 0.2s ease;
  }

  .mobile-enhanced-rank-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  /* 前三名的特殊背景顏色 */
  .mobile-enhanced-rank-card.mobile-rank-1 {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    border: 2px solid #ffd700;
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
  }

  .mobile-enhanced-rank-card.mobile-rank-2 {
    background: linear-gradient(135deg, #c0c0c0, #e5e5e5);
    border: 2px solid #c0c0c0;
    box-shadow: 0 4px 12px rgba(192, 192, 192, 0.3);
  }

  .mobile-enhanced-rank-card.mobile-rank-3 {
    background: linear-gradient(135deg, #cd7f32, #daa447);
    border: 2px solid #cd7f32;
    box-shadow: 0 4px 12px rgba(205, 127, 50, 0.3);
  }

  /* 手機版卡片頭部 */
  .mobile-rank-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.75rem;
  }

  .rank-number-mobile {
    font-size: 1.125rem;
    font-weight: 700;
    color: #64748b;
    min-width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.9);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }

  /* 前三名的排名號碼特殊樣式 */
  .mobile-rank-1 .rank-number-mobile,
  .mobile-rank-2 .rank-number-mobile,
  .mobile-rank-3 .rank-number-mobile {
    background: rgba(255, 255, 255, 0.95);
    color: #1e293b;
    font-weight: 800;
  }

  .player-info-mobile {
    flex: 1;
  }

  .player-name-mobile {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
  }

  /* 前三名的球員名稱特殊樣式 */
  .mobile-rank-1 .player-name-mobile,
  .mobile-rank-2 .player-name-mobile,
  .mobile-rank-3 .player-name-mobile {
    color: #1e293b;
    font-weight: 700;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  .player-org-mobile {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.25rem;
  }

  /* 前三名的組織名稱 */
  .mobile-rank-1 .player-org-mobile,
  .mobile-rank-2 .player-org-mobile,
  .mobile-rank-3 .player-org-mobile {
    color: #374151;
    font-weight: 500;
  }

  .experience-mobile {
    font-size: 1.25rem;
  }

  /* 手機版統計區域 */
  .mobile-rank-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 0.75rem;
    padding: 0.75rem;
    background: rgba(248, 250, 252, 0.8);
    border-radius: 8px;
  }

  /* 前三名的統計區域背景 */
  .mobile-rank-1 .mobile-rank-stats,
  .mobile-rank-2 .mobile-rank-stats,
  .mobile-rank-3 .mobile-rank-stats {
    background: rgba(255, 255, 255, 0.8);
  }

  .stat-item {
    text-align: center;
  }

  .stat-value {
    font-size: 1.125rem;
    font-weight: 700;
    color: #1e293b;
  }

  .stat-label {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.25rem;
  }

  /* 手機版詳細信息 */
  .mobile-rank-details {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(241, 245, 249, 0.8);
  }

  /* 前三名的詳細信息邊框 */
  .mobile-rank-1 .mobile-rank-details,
  .mobile-rank-2 .mobile-rank-details,
  .mobile-rank-3 .mobile-rank-details {
    border-top: 1px solid rgba(255, 255, 255, 0.6);
  }

  .win-loss-record {
    font-size: 0.875rem;
    color: #374151;
    font-weight: 500;
  }

  .experience-level {
    font-size: 0.8rem;
    color: #64748b;
    background: rgba(241, 245, 249, 0.8);
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
  }

  /* 前三名的經驗等級標籤 */
  .mobile-rank-1 .experience-level,
  .mobile-rank-2 .experience-level,
  .mobile-rank-3 .experience-level {
    background: rgba(255, 255, 255, 0.8);
    color: #374151;
  }

  /* === 響應式控制 === */

  /* 確保桌面版不顯示手機版組件 */
  @media (min-width: 769px) {
    .mobile-only {
      display: none !important;
    }
  }

  /* 手機版顯示控制 */
  @media (max-width: 768px) {
    .desktop-only {
      display: none !important;
    }

    .mobile-only {
      display: block;
    }

    .mobile-unified-top-three {
      display: flex;
    }

    .enhanced-mobile-rank-list {
      display: flex;
    }
  }

  /* === 統一的輔助樣式 === */

  /* 排名等級顏色 (手機版和桌面版共用) */
  .rank-top-10 {
    background: linear-gradient(135deg, #fbbf24, #f59e0b) !important;
    color: white !important;
  }

  .rank-top-20 {
    background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
    color: white !important;
  }

  .rank-top-50 {
    background: linear-gradient(135deg, #34d399, #10b981) !important;
    color: white !important;
  }

  /* === 無比賽記錄信息卡片 === */
  .no-matches-info {
    margin-top: 2rem;
  }

  .info-card {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border: 1px solid #f59e0b;
  }

  .info-content {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
  }

  .info-text h3 {
    margin: 0 0 0.5rem 0;
    color: #92400e;
    font-size: 1.125rem;
    font-weight: 600;
  }

  .info-text p {
    margin: 0 0 0.5rem 0;
    color: #78350f;
    line-height: 1.5;
  }

  .info-text p:last-child {
    margin-bottom: 0;
  }

  /* === 輔助函數對應的顏色類 === */

  /* 排名等級類別 */
  .rank-top-10 {
    background: linear-gradient(135deg, #fbbf24, #f59e0b) !important;
    color: white !important;
  }

  .rank-top-20 {
    background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
    color: white !important;
  }

  .rank-top-50 {
    background: linear-gradient(135deg, #34d399, #10b981) !important;
    color: white !important;
  }

  /* === 響應式調整 === */
  @media (max-width: 1024px) {
    .enhanced-rank-item {
      grid-template-columns: 60px 2fr 100px 120px 80px;
      gap: 0.75rem;
      padding: 1rem;
    }

    .score-main,
    .winrate-main {
      font-size: 1.25rem;
    }

    .match-count {
      font-size: 1rem;
    }
  }

  @media (max-width: 768px) {
    .desktop-only {
      display: none;
    }

    .mobile-only {
      display: block;
    }

    .section-title {
      font-size: 1.25rem;
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .section-title .subtitle {
      font-size: 0.8rem;
    }
  }
</style>
