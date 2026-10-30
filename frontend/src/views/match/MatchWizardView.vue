<template>
  <div class="wizard">
    <PageHeader
      :eyebrow="isEdit ? 'EDIT MATCH' : 'NEW MATCH'"
      :title="isEdit ? '編輯比賽' : '記錄比賽'"
      :subtitle="isEdit ? '修改後所有球員的分數會依時間重新計算。' : '四個步驟完成一場比賽紀錄。'"
    >
      <template v-if="!isEdit" #actions>
        <n-button quaternary @click="router.push({ name: 'BatchRecordMatch' })">
          <template #icon><n-icon :component="Layers" /></template>
          補登很多場？改用批次記錄
        </n-button>
      </template>
    </PageHeader>

    <n-steps
      :current="step + 1"
      :status="stepStatus"
      class="steps"
      size="small"
      @update:current="value => goTo(value - 1)"
    >
      <n-step v-for="item in STEPS" :key="item" :title="item" />
    </n-steps>

    <n-spin :show="loading">
      <section class="panel">
        <transition :name="direction" mode="out-in">
          <div :key="step" class="step-body">
            <!-- 1. 比賽設定 -->
            <template v-if="step === 0">
              <n-form label-placement="top">
                <n-form-item label="比賽日期">
                  <n-date-picker v-model:value="form.match_date_ts" type="date" class="full" />
                </n-form-item>
                <n-form-item label="比賽類型">
                  <div class="choices">
                    <button
                      v-for="option in matchTypeOptions"
                      :key="option.value"
                      type="button"
                      class="choice"
                      :class="{ active: form.match_type === option.value }"
                      @click="form.match_type = option.value"
                    >
                      <span class="choice-icon">{{ option.value === 'singles' ? '👤' : '👥' }}</span>
                      {{ option.label }}
                    </button>
                  </div>
                </n-form-item>
                <n-form-item label="賽制">
                  <div class="choices">
                    <button
                      v-for="option in matchFormatOptions"
                      :key="option.value"
                      type="button"
                      class="choice"
                      :class="{ active: form.match_format === option.value }"
                      @click="changeFormat(option.value)"
                    >
                      <span class="choice-icon num">{{ maxGames(option.value) }}</span>
                      {{ option.label }}
                    </button>
                  </div>
                </n-form-item>
                <n-collapse>
                  <n-collapse-item title="更多資訊（選填）" name="more">
                    <n-grid :cols="3" :x-gap="12" responsive="screen" item-responsive>
                      <n-form-item-gi span="3 m:1" label="時段">
                        <n-select v-model:value="form.time_slot" :options="timeSlotOptions" clearable />
                      </n-form-item-gi>
                      <n-form-item-gi span="3 m:1" label="場地">
                        <n-select v-model:value="form.court_surface" :options="courtSurfaceOptions" clearable />
                      </n-form-item-gi>
                      <n-form-item-gi span="3 m:1" label="環境">
                        <n-select v-model:value="form.court_environment" :options="courtEnvironmentOptions" clearable />
                      </n-form-item-gi>
                      <n-form-item-gi span="3 m:1" label="比賽時長（分鐘）">
                        <n-input-number
                          v-model:value="form.duration_minutes"
                          :min="1"
                          :max="600"
                          clearable
                          class="full"
                        />
                      </n-form-item-gi>
                      <n-form-item-gi span="3 m:2" label="YouTube 影片">
                        <n-input v-model:value="form.youtube_url" placeholder="https://www.youtube.com/watch?v=…" />
                      </n-form-item-gi>
                      <n-form-item-gi span="3" label="備註">
                        <n-input
                          v-model:value="form.match_notes"
                          type="textarea"
                          :rows="2"
                          maxlength="500"
                          show-count
                        />
                      </n-form-item-gi>
                    </n-grid>
                  </n-collapse-item>
                </n-collapse>
              </n-form>
            </template>

            <!-- 2. 選擇球員 -->
            <TeamsPicker v-else-if="step === 1" v-model="form" />

            <!-- 3. 比分 -->
            <GameScoreEditor v-else-if="step === 2" v-model="form" @completed="celebrate({ particleCount: 60 })" />

            <!-- 4. 確認 -->
            <template v-else>
              <MatchScoreboard
                :team-a="teamA"
                :team-b="teamB"
                :a-games="form.a_games"
                :b-games="form.b_games"
                :match-date="formatDate(form.match_date_ts)"
                :match-type="form.match_type"
                :match-format="form.match_format"
                :games="previewGames"
              />
              <p class="review-note">確認無誤後送出，比賽的勝負會立即反映在所有球員的分數上。</p>
            </template>
          </div>
        </transition>
      </section>
    </n-spin>

    <footer class="nav">
      <n-button v-if="step > 0" size="large" @click="goTo(step - 1)">
        <template #icon><n-icon :component="ArrowLeft" /></template>
        上一步
      </n-button>
      <n-button v-else size="large" quaternary @click="router.back()">取消</n-button>
      <n-alert v-if="stepError" type="warning" :show-icon="false" class="step-error">{{ stepError }}</n-alert>
      <n-button
        v-if="step < STEPS.length - 1"
        type="primary"
        size="large"
        icon-placement="right"
        @click="goTo(step + 1)"
      >
        下一步
        <template #icon><n-icon :component="ArrowRight" /></template>
      </n-button>
      <n-button v-else type="primary" size="large" :loading="submitting" @click="submit">
        {{ isEdit ? '儲存變更' : '送出比賽' }}
      </n-button>
    </footer>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { ArrowLeft, ArrowRight, Layers } from '@vicons/carbon'
  import { matchesApi, membersApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import GameScoreEditor from '@/components/match/GameScoreEditor.vue'
  import MatchScoreboard from '@/components/match/MatchScoreboard.vue'
  import TeamsPicker from '@/components/match/TeamsPicker.vue'
  import { useOptions } from '@/composables/useOptions'
  import { celebrate } from '@/utils/celebrate'
  import { formatDate } from '@/utils/format'
  import {
    emptyGameFields,
    gameScoresFromForm,
    matchFormFromRecord,
    matchPayloadFromForm,
    newMatchForm
  } from '@/utils/matchForm'
  import { maxGames } from '@/utils/matchRules'

  const STEPS = ['比賽設定', '選擇球員', '輸入比分', '確認送出']

  const props = defineProps({
    mode: { type: String, default: 'add', validator: value => ['add', 'edit'].includes(value) },
    matchId: { type: [String, Number], default: null }
  })

  const router = useRouter()
  const message = useMessage()
  const { matchTypeOptions, matchFormatOptions, timeSlotOptions, courtSurfaceOptions, courtEnvironmentOptions } =
    useOptions()

  const isEdit = computed(() => props.mode === 'edit')
  const loading = ref(false)
  const submitting = ref(false)
  const step = ref(0)
  const direction = ref('slide-left')
  const stepError = ref('')
  const form = ref(newMatchForm())
  const players = ref({})

  const stepStatus = computed(() => (stepError.value ? 'error' : 'process'))
  const teamOf = fields => fields.map(field => players.value[form.value[field]]).filter(Boolean)
  const teamA = computed(() => teamOf(['player1_id', 'player2_id']))
  const teamB = computed(() => teamOf(['player3_id', 'player4_id']))
  const previewGames = computed(() =>
    gameScoresFromForm(form.value)
      .map(({ a, b }, index) => ({ game: index + 1, a_score: a, b_score: b }))
      .filter(game => game.a_score || game.b_score)
  )

  /** 每一步離開前的檢查，回傳錯誤訊息或空字串。 */
  const validators = [
    () => (!form.value.match_date_ts ? '請選擇比賽日期' : ''),
    () => {
      const f = form.value
      const needed =
        f.match_type === 'singles'
          ? [f.player1_id, f.player3_id]
          : [f.player1_id, f.player2_id, f.player3_id, f.player4_id]
      return needed.every(Boolean) ? '' : '請選齊兩隊的球員'
    },
    () => {
      const { a_games: a, b_games: b } = form.value
      if (!a && !b) return '請輸入比分'
      return a === b ? '比賽不能平手' : ''
    },
    () => ''
  ]

  const goTo = async target => {
    if (target === step.value) return
    if (target > step.value) {
      // 往後跳時，中間每一步都要通過檢查
      for (let index = step.value; index < target; index++) {
        const error = validators[index]()
        if (error) {
          stepError.value = error
          step.value = index
          return
        }
      }
    }
    stepError.value = ''
    direction.value = target > step.value ? 'slide-left' : 'slide-right'
    step.value = target
    if (target === STEPS.length - 1) await loadPlayers()
  }

  const changeFormat = value => {
    if (value === form.value.match_format) return
    form.value = { ...form.value, match_format: value, ...emptyGameFields(), a_games: 0, b_games: 0 }
  }

  const loadPlayers = async () => {
    const ids = ['player1_id', 'player2_id', 'player3_id', 'player4_id'].map(f => form.value[f]).filter(Boolean)
    const missing = ids.filter(id => !players.value[id])
    const loaded = await Promise.all(missing.map(id => membersApi.get(id).catch(() => null)))
    players.value = { ...players.value, ...Object.fromEntries(loaded.filter(Boolean).map(p => [p.id, p])) }
  }

  const submit = async () => {
    submitting.value = true
    try {
      const payload = matchPayloadFromForm(form.value)
      const record = isEdit.value ? await matchesApi.update(props.matchId, payload) : await matchesApi.create(payload)
      celebrate()
      message.success(isEdit.value ? '比賽紀錄已更新' : '比賽已記錄！')
      router.push({ name: 'ViewMatch', params: { id: record.id } })
    } catch (error) {
      const data = error.response?.data
      message.error(data?.details ? Object.values(data.details).flat().join('；') : data?.message || '送出失敗')
    } finally {
      submitting.value = false
    }
  }

  watch(
    form,
    () => {
      if (stepError.value && !validators[step.value]()) stepError.value = ''
    },
    { deep: true }
  )

  onMounted(async () => {
    if (!isEdit.value) return
    loading.value = true
    try {
      form.value = matchFormFromRecord(await matchesApi.get(props.matchId))
    } catch {
      message.error('找不到這場比賽')
      router.push({ name: 'MatchManagement' })
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .steps {
    margin-bottom: 20px;
  }
  .panel {
    padding: 24px;
    border-radius: var(--radius-xl);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    min-height: 320px;
  }
  .full {
    width: 100%;
  }
  .choices {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    width: 100%;
  }
  .choice {
    flex: 1;
    min-width: 110px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 14px;
    border: 2px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
    font: inherit;
    font-weight: 700;
    color: var(--gray-700);
    cursor: pointer;
    transition:
      border-color var(--duration-fast),
      transform var(--duration-base) var(--ease-spring),
      background var(--duration-fast);
  }
  .choice:hover {
    transform: translateY(-2px);
  }
  .choice.active {
    border-color: var(--blue-600);
    background: var(--blue-50);
    color: var(--blue-700);
  }
  .choice-icon {
    font-size: 26px;
    font-weight: 700;
  }
  .review-note {
    margin: 18px 0 0;
    text-align: center;
    color: var(--color-text-muted);
  }
  .nav {
    position: sticky;
    bottom: 0;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 20px;
    padding: 12px 0;
    background: linear-gradient(transparent, var(--color-bg) 30%);
  }
  .step-error {
    flex: 1;
  }
  .nav > :last-child {
    margin-left: auto;
  }
  .slide-left-enter-active,
  .slide-left-leave-active,
  .slide-right-enter-active,
  .slide-right-leave-active {
    transition:
      opacity var(--duration-base) var(--ease-out),
      transform var(--duration-base) var(--ease-out);
  }
  .slide-left-enter-from,
  .slide-right-leave-to {
    opacity: 0;
    transform: translateX(40px);
  }
  .slide-left-leave-to,
  .slide-right-enter-from {
    opacity: 0;
    transform: translateX(-40px);
  }
  @media (max-width: 640px) {
    .panel {
      padding: 16px;
    }
    /* 手機只顯示目前步驟的標題，其他步驟只留圓點，避免橫向溢出 */
    .steps :deep(.n-step:not(.n-step--process-status) .n-step-content) {
      display: none;
    }
    .nav {
      bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
    }
  }
</style>
