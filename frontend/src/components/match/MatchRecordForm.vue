<template>
  <div class="match-record-form-page container-fluid mt-4 mb-5 px-md-4">
    <n-card :bordered="false" :class="['form-card', { 'readonly-mode': isReadonly }]">
      <!-- 頁面標題 -->
      <div class="page-header mb-4">
        <n-button quaternary circle style="margin-right: 1rem" @click="goBack">
          <template #icon>
            <n-icon :component="ArrowLeftIcon" />
          </template>
        </n-button>
        <h1 class="page-title">{{ pageTitle }}</h1>
      </div>

      <!-- 表單內容 -->
      <n-form
        ref="formRef"
        :model="matchForm"
        :rules="formRules"
        label-placement="top"
        :disabled="isReadonly"
        @submit.prevent="handleSubmit"
      >
        <!-- 🔧 查看模式提示 -->
        <!--        <div v-if="isReadonly" class="readonly-notice mb-4">-->
        <!--          <n-alert type="info" :show-icon="false" style="border-radius: 8px;">-->
        <!--            <template #header>-->
        <!--              <n-space align="center">-->
        <!--                <n-icon :component="EyeIcon" />-->
        <!--                <span>詳細檢視模式</span>-->
        <!--              </n-space>-->
        <!--            </template>-->
        <!--          </n-alert>-->
        <!--        </div>-->
        <!-- 比賽基本資訊 -->
        <n-divider style="margin-top: 2rem; margin-bottom: 2rem">
          <n-text style="font-size: 14px; color: #666">比賽基本資訊</n-text>
        </n-divider>

        <n-grid :x-gap="20" :y-gap="20" cols="1 s:3" responsive="screen" align-items="start">
          <n-form-item-gi label="比賽日期" path="match_date">
            <n-date-picker
              v-model:value="matchForm.match_date_ts"
              type="date"
              :placeholder="isReadonly ? '' : '選擇比賽日期'"
              style="width: 100%"
              size="large"
              :disabled="isReadonly"
              :readonly="isReadonly"
            />
          </n-form-item-gi>
          <n-form-item-gi label="比賽類型" path="match_type">
            <n-select
              v-model:value="matchForm.match_type"
              :options="matchTypeOptions"
              size="large"
              :disabled="isReadonly"
              :readonly="isReadonly"
              :placeholder="isReadonly ? '' : '選擇比賽類型'"
              :clearable="!isReadonly"
            />
          </n-form-item-gi>
          <n-form-item-gi label="賽制" path="match_format">
            <n-select
              v-model:value="matchForm.match_format"
              :options="matchFormatOptions"
              size="large"
              :disabled="isReadonly"
              :readonly="isReadonly"
              :placeholder="isReadonly ? '' : '選擇賽制'"
              :clearable="!isReadonly"
            />
          </n-form-item-gi>
        </n-grid>

        <!-- 球員選擇區域 -->
        <n-divider style="margin-top: 2rem; margin-bottom: 2rem">
          <n-text style="font-size: 14px; color: #666">球員設定</n-text>
        </n-divider>

        <MatchPlayerSelector v-model="matchForm" :disabled="isReadonly" />

        <!-- 比分顯示區域 -->
        <n-divider style="margin-top: 2rem; margin-bottom: 2rem">
          <n-text style="font-size: 14px; color: #666">比賽分數</n-text>
        </n-divider>

        <MatchScoreDisplay
          ref="matchScoreDisplayRef"
          v-model="matchForm"
          :allow-score-adjustment="!isReadonly"
          :read-only="isReadonly"
          :mode="mode"
          @score-changed="handleScoreChanged"
          @match-completed="handleMatchCompleted"
        />

        <!-- 可折疊的詳細設定區塊 -->
        <n-divider style="margin-top: 2rem; margin-bottom: 1rem">
          <n-button text style="color: #666; font-size: 14px" @click="showAdvancedSettings = !showAdvancedSettings">
            <template #icon>
              <n-icon :component="showAdvancedSettings ? ChevronUpIcon : ChevronDownIcon" />
            </template>
            其他設定 {{ isReadonly ? '(詳細資訊)' : '(選填)' }}
          </n-button>
        </n-divider>

        <!-- 可折疊內容 -->
        <div v-if="showAdvancedSettings" class="advanced-settings-container">
          <!-- 場地資訊 -->
          <div class="settings-section">
            <h4 style="margin-bottom: 1rem; color: #666; font-size: 14px">場地資訊</h4>
            <div class="form-row">
              <n-form-item label="場地材質" path="court_surface">
                <n-select
                  v-model:value="matchForm.court_surface"
                  :options="courtSurfaceOptions"
                  :placeholder="isReadonly ? '' : '選擇場地材質'"
                  :clearable="!isReadonly"
                  size="medium"
                  :disabled="isReadonly"
                  :readonly="isReadonly"
                />
              </n-form-item>

              <n-form-item label="場地環境" path="court_environment">
                <n-select
                  v-model:value="matchForm.court_environment"
                  :options="courtEnvironmentOptions"
                  :placeholder="isReadonly ? '' : '選擇場地環境'"
                  :clearable="!isReadonly"
                  size="medium"
                  :disabled="isReadonly"
                  :readonly="isReadonly"
                />
              </n-form-item>

              <n-form-item label="比賽時段" path="time_slot">
                <n-select
                  v-model:value="matchForm.time_slot"
                  :options="timeSlotOptions"
                  :placeholder="isReadonly ? '' : '選擇比賽時段'"
                  :clearable="!isReadonly"
                  size="medium"
                  :disabled="isReadonly"
                  :readonly="isReadonly"
                />
              </n-form-item>
            </div>
          </div>

          <!-- 比賽詳細資訊 -->
          <div class="settings-section">
            <h4 style="margin-bottom: 1rem; color: #666; font-size: 14px">比賽詳細資訊</h4>
            <div class="form-row">
              <n-form-item label="比賽時長 (分鐘)" path="duration_minutes">
                <n-input-number
                  v-model:value="matchForm.duration_minutes"
                  :placeholder="isReadonly ? '' : '分鐘'"
                  :min="isReadonly ? undefined : 10"
                  :max="isReadonly ? undefined : 180"
                  :clearable="!isReadonly"
                  size="medium"
                  style="width: 100%"
                  :disabled="isReadonly"
                  :readonly="isReadonly"
                />
              </n-form-item>

              <n-form-item label="YouTube 網址" path="youtube_url">
                <n-input
                  v-model:value="matchForm.youtube_url"
                  :placeholder="isReadonly ? '' : 'https://www.youtube.com/watch?v=...'"
                  :clearable="!isReadonly"
                  size="medium"
                  :disabled="isReadonly"
                  :readonly="isReadonly"
                />
              </n-form-item>
            </div>

            <!-- 比賽備註 -->
            <n-form-item label="比賽備註" path="match_notes" style="margin-top: 1rem">
              <n-input
                v-model:value="matchForm.match_notes"
                type="textarea"
                :placeholder="isReadonly ? '' : '記錄比賽相關備註...'"
                :rows="3"
                :clearable="!isReadonly"
                size="medium"
                :disabled="isReadonly"
                :readonly="isReadonly"
              />
            </n-form-item>
          </div>
        </div>

        <!-- 操作按鈕 -->
        <n-divider style="margin-top: 2rem; margin-bottom: 2rem" />
        <n-space justify="space-between" style="width: 100%">
          <n-button size="large" @click="goBack">
            <template #icon>
              <n-icon :component="ArrowLeftIcon" />
            </template>
            返回
          </n-button>

          <!-- 根據模式和權限顯示不同的操作按鈕 -->
          <n-space v-if="!isReadonly">
            <n-button size="large" @click="resetForm">
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              重置
            </n-button>
            <n-button type="primary" size="large" :loading="submitting" :disabled="!canSubmit" @click="handleSubmit">
              <template #icon>
                <n-icon :component="SaveIcon" />
              </template>
              {{ mode === 'add' ? '儲存比賽結果' : '更新比賽結果' }}
            </n-button>
          </n-space>

          <!-- 查看模式下的管理按鈕 (僅幹部以上可見) -->
          <n-space v-else-if="hasManagementAccess">
            <n-button type="warning" size="large" @click="switchToEditMode">
              <template #icon>
                <n-icon :component="EditIcon" />
              </template>
              編輯比賽
            </n-button>
            <n-button type="error" size="large" @click="confirmDelete">
              <template #icon>
                <n-icon :component="DeleteIcon" />
              </template>
              刪除比賽
            </n-button>
          </n-space>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
  // 1. 引入 (Imports)
  import { computed, ref, onMounted, nextTick } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useMessage, useDialog } from 'naive-ui'
  import { useAuthStore } from '@/stores/authStore.js'
  import { usePermissions } from '@/composables/usePermissions'
  import apiClient from '@/services/apiClient'
  import { useOptions } from '@/composables/useOptions'

  // 引入組件
  import MatchPlayerSelector from '@/components/match/MatchPlayerSelector.vue'
  import MatchScoreDisplay from '@/components/match/MatchScoreDisplay.vue'

  // 引入圖標
  import {
    ArrowBackOutline as ArrowLeftIcon,
    ChevronDownOutline as ChevronDownIcon,
    ChevronUpOutline as ChevronUpIcon,
    RefreshOutline as RefreshIcon,
    SaveOutline as SaveIcon,
    CreateOutline as EditIcon,
    TrashOutline as DeleteIcon,
    EyeOutline as EyeIcon
  } from '@vicons/ionicons5'

  // 2. Props 定義
  const props = defineProps({
    mode: {
      type: String,
      default: 'add', // 'add' | 'edit' | 'view'
      validator: value => ['add', 'edit', 'view'].includes(value)
    },
    matchId: {
      type: [String, Number],
      default: null
    }
  })

  // 3. 實例化 hooks
  const router = useRouter()
  const message = useMessage()
  const dialog = useDialog()
  const { hasManagementAccess } = usePermissions()

  // 4. 狀態管理 (State)
  const loading = ref(false)
  const submitting = ref(false)
  const showAdvancedSettings = ref(false)
  const formRef = ref(null)
  const matchScoreDisplayRef = ref(null)

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
    loadPlayerOptions
  } = useOptions()

  // 5. 計算屬性 - 權限和模式
  const isReadonly = computed(() => props.mode === 'view')

  const pageTitle = computed(() => {
    switch (props.mode) {
      case 'add':
        return '記錄新比賽'
      case 'edit':
        return '編輯比賽記錄'
      case 'view':
        return '比賽詳細資料'
      default:
        return '比賽記錄'
    }
  })

  // 6. 表單數據 (Form Data)
  const matchForm = ref({
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
    duration_minutes: null,
    youtube_url: '',
    first_serve_side: null,

    // 詳細局比分
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

  // 8. 計算屬性 (Computed Properties)
  const teamNames = computed(() => {
    const getTeamName = (player1Id, player2Id) => {
      if (matchForm.value.match_type === 'singles') {
        return player1Id ? '球員' : '隊伍'
      } else {
        return player1Id && player2Id ? '隊伍' : '隊伍'
      }
    }

    return {
      teamA: getTeamName(matchForm.value.player1_id, matchForm.value.player2_id),
      teamB: getTeamName(matchForm.value.player3_id, matchForm.value.player4_id)
    }
  })

  const canSubmit = computed(() => {
    if (isReadonly.value) return false

    const form = matchForm.value

    // 基本必填檢查：球員1和球員3必須選擇
    if (!form.player1_id || !form.player3_id) {
      return false
    }

    // 如果是雙打模式，球員2和球員4也必須選擇
    if (form.match_type === 'doubles' && (!form.player2_id || !form.player4_id)) {
      return false
    }

    // 簡化的比分檢查：只要有一方的分數大於0就可以提交
    return form.a_games > 0 || form.b_games > 0
  })

  // 9. 表單驗證規則 (Form Rules)
  const formRules = {
    match_date: [{ required: true, message: '請選擇比賽日期', trigger: 'change' }],
    match_type: [{ required: true, message: '請選擇比賽類型', trigger: 'change' }],
    match_format: [{ required: true, message: '請選擇賽制', trigger: 'change' }],
    player1_id: [{ required: true, message: '請選擇球員1', trigger: 'change' }],
    player3_id: [{ required: true, message: '請選擇球員3', trigger: 'change' }]
  }

  // 10. 事件處理函數 (Event Handlers)
  const handleScoreChanged = event => {
    console.log('比分已變更:', event)
  }

  const handleMatchCompleted = result => {
    console.log('比賽完成:', result)
    message.success(`🎉 ${result.winner} 獲勝！`)
  }

  const handleSubmit = async () => {
    if (props.mode === 'add') {
      await handleCreateMatch()
    } else if (props.mode === 'edit') {
      await handleUpdateMatch()
    }
  }

  const handleCreateMatch = async () => {
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

    submitting.value = true

    try {
      const response = await apiClient.post('/match-records', buildPayload())
      message.success(response.message || '比賽結果已成功儲存！')

      setTimeout(() => {
        router.push({ name: 'MatchManagement' })
      }, 1500)
    } catch (err) {
      handleApiError(err, '儲存')
    } finally {
      submitting.value = false
    }
  }

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

    submitting.value = true

    try {
      const response = await apiClient.put(`/match-records/${props.matchId}`, buildPayload())
      message.success(response.message || '比賽記錄已成功更新！')

      setTimeout(() => {
        router.push({ name: 'MatchManagement' })
      }, 1500)
    } catch (err) {
      handleApiError(err, '更新')
    } finally {
      submitting.value = false
    }
  }

  const buildPayload = () => {
    const formatDate = timestamp => {
      if (!timestamp) return null
      const date = new Date(timestamp)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    // 基礎 payload
    const payload = {
      match_date: formatDate(matchForm.value.match_date_ts),
      match_type: matchForm.value.match_type,
      match_format: matchForm.value.match_format,
      player1_id: matchForm.value.player1_id,
      player2_id: matchForm.value.match_type === 'singles' ? null : matchForm.value.player2_id,
      player3_id: matchForm.value.player3_id,
      player4_id: matchForm.value.match_type === 'singles' ? null : matchForm.value.player4_id,
      a_games: matchForm.value.a_games,
      b_games: matchForm.value.b_games,

      // 基本資訊
      notes: matchForm.value.match_notes || null,
      court_surface: matchForm.value.court_surface || null,
      court_environment: matchForm.value.court_environment || null,
      time_slot: matchForm.value.time_slot || null,
      duration_minutes: matchForm.value.duration_minutes || null,
      youtube_url: matchForm.value.youtube_url || null
    }

    // 檢查是否有詳細比分數據
    const hasDetailedScores = Object.keys(matchForm.value)
      .filter(key => key.startsWith('game') && key.endsWith('_score'))
      .some(key => matchForm.value[key] > 0)

    if (hasDetailedScores) {
      // 包含先發球方和所有局比分
      payload.first_serve_side = matchForm.value.first_serve_side || null
      payload.games = Array.from({ length: 9 }, (_, i) => ({
        a_score: matchForm.value[`game${i + 1}_a_score`] || 0,
        b_score: matchForm.value[`game${i + 1}_b_score`] || 0
      }))
    }

    // 移除空值；搭檔欄位保留 null，改成單打時才能清掉原本的搭檔
    const keepNull = ['player2_id', 'player4_id']
    Object.keys(payload).forEach(key => {
      if (keepNull.includes(key)) return
      if (payload[key] === null || payload[key] === undefined || payload[key] === '') {
        delete payload[key]
      }
    })

    return payload
  }

  const handleApiError = (err, action) => {
    console.error(`${action}失敗詳細信息:`, {
      error: err,
      response: err.response?.data,
      status: err.response?.status,
      statusText: err.response?.statusText
    })

    const errorData = err.response?.data

    let errorMessage = `${action}失敗，請稍後再試。`

    if (errorData?.details) {
      errorMessage = '輸入數據有誤：\n' + Object.values(errorData.details).flat().join('\n')
      message.error(errorMessage, { duration: 7000, closable: true })
    } else if (errorData?.message) {
      errorMessage = errorData.message
      message.error(errorMessage)
    } else {
      message.error(errorMessage)
    }
  }

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
      duration_minutes: null,
      youtube_url: '',
      first_serve_side: null
    }

    // 重置所有詳細分數
    for (let i = 1; i <= 9; i++) {
      matchForm.value[`game${i}_a_score`] = 0
      matchForm.value[`game${i}_b_score`] = 0
    }

    message.info('表單已重置')
  }

  const switchToEditMode = () => {
    router.push({ name: 'EditMatch', params: { id: props.matchId } })
  }

  const confirmDelete = () => {
    dialog.error({
      title: '確認刪除比賽記錄',
      content: '您確定要刪除這場比賽記錄嗎？此操作無法撤銷。',
      positiveText: '確認刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await apiClient.delete(`/match-records/${props.matchId}`)
          message.success('比賽記錄已成功刪除')
          router.push({ name: 'MatchManagement' })
        } catch (err) {
          console.error('刪除失敗:', err)
          message.error(err.response?.data?.message || '刪除失敗')
        }
      }
    })
  }

  // 把 API 的 games 陣列轉成表單使用的 game{n}_a_score / game{n}_b_score 欄位
  const gameScoreFields = (games = []) => {
    const fields = {}
    for (let i = 1; i <= 9; i++) {
      const game = games.find(g => g.game === i)
      fields[`game${i}_a_score`] = game?.a_score || 0
      fields[`game${i}_b_score`] = game?.b_score || 0
    }
    return fields
  }

  const loadMatchData = async () => {
    if (!props.matchId || props.mode === 'add') return

    loading.value = true

    try {
      const response = await apiClient.get(`/match-records/${props.matchId}`)
      const record = response.data

      // 處理日期轉換
      let matchDate = null
      if (record.match_date) {
        try {
          const date = new Date(record.match_date)
          if (!isNaN(date.getTime())) {
            matchDate = date.getTime()
          }
        } catch (e) {
          console.warn('日期解析失敗:', record.match_date, e)
          matchDate = new Date().getTime()
        }
      } else {
        matchDate = new Date().getTime()
      }

      // 填充表單數據
      matchForm.value = {
        match_date_ts: matchDate,
        match_date: record.match_date || '',
        match_type: record.match_type || 'doubles',
        match_format: record.match_format || 'games_9',

        // 球員 ID
        player1_id: record.player1?.id || record.player1_id || null,
        player2_id: record.player2?.id || record.player2_id || null,
        player3_id: record.player3?.id || record.player3_id || null,
        player4_id: record.player4?.id || record.player4_id || null,

        // 總比分
        a_games: record.a_games || 0,
        b_games: record.b_games || 0,

        // 每局比分
        ...gameScoreFields(record.games),

        // 其他比賽資訊
        match_notes: record.notes || '',
        court_surface: record.court_surface || null,
        court_environment: record.court_environment || null,
        time_slot: record.time_slot || null,
        duration_minutes: record.duration_minutes || null,
        youtube_url: record.youtube_url || '',
        first_serve_side: record.first_serve_side || null
      }

      // 數據載入完成後，通知子組件重新初始化
      await nextTick()

      if (matchScoreDisplayRef.value) {
        matchScoreDisplayRef.value.initializeDetailedScoring?.()
      }
    } catch (err) {
      console.error('載入比賽數據失敗:', err)
      const errorMsg = err.response?.data?.message || err.message || '載入比賽數據失敗'
      message.error(`載入比賽數據失敗: ${errorMsg}`)

      if (err.response?.status === 404) {
        message.error(`找不到 ID 為 ${props.matchId} 的比賽記錄`)
      }

      setTimeout(() => {
        router.push({ name: 'MatchManagement' })
      }, 2000)
    } finally {
      loading.value = false
    }
  }

  const goBack = () => {
    router.push({ name: 'MatchManagement' })
  }

  // 11. 生命週期
  onMounted(async () => {
    // 🔧 先載入球員選項，然後載入比賽數據
    await loadPlayerOptions()
    await loadMatchData()
  })
</script>

<style scoped>
  .match-record-form-page {
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
  }

  .page-title {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1f2937;
  }

  .view-mode-badge {
    margin-left: auto;
  }

  .form-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }

  /* 🔧 查看模式樣式 */
  .form-card.readonly-mode {
    background: #fafafa;
    border: 2px solid #e0e7ff;
  }

  .readonly-notice {
    margin-bottom: 1rem;
  }

  /* 🔧 查看模式下的表單元素樣式 */
  .readonly-mode :deep(.n-input.n-input--disabled),
  .readonly-mode :deep(.n-input-number.n-input-number--disabled),
  .readonly-mode :deep(.n-select.n-select--disabled),
  .readonly-mode :deep(.n-date-picker.n-date-picker--disabled) {
    background-color: #f8f9fa !important;
    border-color: #e9ecef !important;
    cursor: default !important;
  }

  .readonly-mode :deep(.n-input__input-el[disabled]),
  .readonly-mode :deep(.n-input__textarea-el[disabled]) {
    color: #495057 !important;
    background-color: #f8f9fa !important;
  }

  .readonly-mode :deep(.n-select .n-base-selection.n-base-selection--disabled) {
    background-color: #f8f9fa !important;
    border-color: #e9ecef !important;
  }

  .readonly-mode :deep(.n-select .n-base-selection .n-base-selection-label) {
    color: #495057 !important;
  }

  .advanced-settings-container {
    background: #f9fafb;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 1rem;
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .settings-section {
    margin-bottom: 1.5rem;
  }

  .settings-section:last-child {
    margin-bottom: 0;
  }

  .form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  /* 響應式設計 */
  @media (max-width: 768px) {
    .form-card {
      padding: 1rem;
      margin: 0 0.5rem;
    }

    .page-title {
      font-size: 1.25rem;
    }

    .advanced-settings-container {
      padding: 1rem;
    }
  }

  @media (max-width: 480px) {
    .match-record-form-page {
      padding: 0.5rem;
    }

    .form-card {
      padding: 0.75rem;
      margin: 0;
    }
  }
</style>
