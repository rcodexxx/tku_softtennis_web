<template>
  <div class="new-season">
    <PageHeader
      eyebrow="NEW SEASON"
      title="開新賽季"
      subtitle="封存目前的排行榜、整理名單，所有人的分數從起始分數重新開始。"
    />

    <n-steps :current="step + 1" class="steps" size="small" @update:current="value => goTo(value - 1)">
      <n-step v-for="item in STEPS" :key="item" :title="item" />
    </n-steps>

    <n-spin :show="loading">
      <section class="panel">
        <transition :name="direction" mode="out-in">
          <div :key="step" class="step-body">
            <!-- 1. 基本資料 -->
            <template v-if="step === 0">
              <div v-if="currentSeason" class="archive-card">
                <n-icon :component="Archive" size="28" />
                <div>
                  <b>{{ currentSeason.name }}</b> 將會封存
                  <p>
                    {{ currentSeason.start_date }} 起・共 {{ currentSeason.match_count }} 場比賽。
                    封存後仍可在排行榜切換查看。
                  </p>
                </div>
              </div>
              <n-form label-placement="top" class="basics">
                <n-form-item label="賽季名稱">
                  <n-input v-model:value="name" maxlength="50" placeholder="例如 115 學年度" />
                </n-form-item>
                <n-form-item label="開始日期">
                  <n-date-picker
                    v-model:value="startDate"
                    type="date"
                    class="full"
                    :is-date-disabled="isDateDisabled"
                    :clearable="false"
                  />
                </n-form-item>
              </n-form>
              <p class="note">這天以後的比賽算新賽季；之前的比賽留在舊賽季，之後補記錄也會自動歸到對的賽季。</p>
            </template>

            <!-- 2. 整理名單 -->
            <template v-else-if="step === 1">
              <RosterEditor :rows="rows" />
            </template>

            <!-- 3. 確認 -->
            <template v-else>
              <div class="confirm-hero">
                <span class="confirm-eyebrow">準備開始</span>
                <h2>{{ name }}</h2>
                <span class="confirm-date num">{{ formatDate(startDate) }} 起</span>
              </div>
              <div class="outcomes">
                <article v-for="choice in ROSTER_CHOICES" :key="choice.value" class="outcome" :class="choice.value">
                  <span class="outcome-label">{{ OUTCOME_LABELS[choice.value] }}</span>
                  <span class="outcome-count num">{{ summary[choice.value].count }}</span>
                  <span v-if="summary[choice.value].moved.length" class="outcome-moved">
                    這次變動：{{ summary[choice.value].moved.join('、') }}
                  </span>
                </article>
              </div>
              <ul class="effects">
                <li v-if="currentSeason">{{ currentSeason.name }}的排行榜封存，可在排行榜切換查看。</li>
                <li>所有人的分數回到起始分數（男 5.0、女 4.0，甲組加 1）。</li>
                <li>離隊的人保留比賽紀錄，還能記錄比賽、出現在綜合榜。</li>
              </ul>
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
        <template #icon><n-icon :component="Flag" /></template>
        開始 {{ name }}
      </n-button>
    </footer>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { Archive, ArrowLeft, ArrowRight, Flag } from '@vicons/carbon'
  import { membersApi, seasonsApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import RosterEditor from '@/components/team/RosterEditor.vue'
  import { celebrate } from '@/utils/celebrate'
  import { dateToTimestamp, formatDate } from '@/utils/format'
  import { defaultSeasonName, defaultSeasonStart, ROSTER_CHOICES, rosterPayload, rosterSummary } from '@/utils/season'

  const STEPS = ['基本資料', '整理名單', '確認']
  const OUTCOME_LABELS = { team: '校隊', alumni: '校友會（畢業）', left: '離隊' }

  const router = useRouter()
  const message = useMessage()

  const loading = ref(true)
  const submitting = ref(false)
  const step = ref(0)
  const direction = ref('slide-left')
  const stepError = ref('')
  const seasons = ref([])
  const rows = ref([])
  const name = ref(defaultSeasonName())
  const startDate = ref(dateToTimestamp(formatDate(new Date())))

  const currentSeason = computed(() => seasons.value.find(season => season.is_current) ?? null)
  const summary = computed(() => rosterSummary(rows.value))

  // 開始日期不能晚於今天，也要晚於目前賽季的開始日期
  const isDateDisabled = timestamp =>
    timestamp > Date.now() ||
    Boolean(currentSeason.value && timestamp <= dateToTimestamp(currentSeason.value.start_date))

  const validateStep = () => {
    if (step.value === 0) {
      if (!name.value?.trim()) return '請輸入賽季名稱'
      if (seasons.value.some(season => season.name === name.value.trim())) return `「${name.value}」已經存在`
      if (!startDate.value || isDateDisabled(startDate.value)) return '請選擇有效的開始日期'
    }
    return ''
  }

  const goTo = target => {
    if (target === step.value || target < 0 || target >= STEPS.length) return
    if (target > step.value) {
      stepError.value = validateStep()
      if (stepError.value) return
    }
    stepError.value = ''
    direction.value = target > step.value ? 'slide-left' : 'slide-right'
    step.value = target
  }

  const submit = async () => {
    submitting.value = true
    try {
      const season = await seasonsApi.create({
        name: name.value.trim(),
        start_date: formatDate(startDate.value),
        roster: rosterPayload(rows.value)
      })
      celebrate()
      message.success(`${season.name}開始了！`)
      router.push({ name: 'Leaderboard' })
    } catch (error) {
      stepError.value = error.response?.data?.message || '開新賽季失敗，請稍後再試'
    } finally {
      submitting.value = false
    }
  }

  onMounted(async () => {
    try {
      const [seasonList, roster] = await Promise.all([seasonsApi.list(), membersApi.roster()])
      seasons.value = seasonList
      // 預設從這個學年度的 8 月 1 日開始；已經不能選時改成今天
      const schoolYearStart = dateToTimestamp(defaultSeasonStart())
      if (!isDateDisabled(schoolYearStart)) startDate.value = schoolYearStart
      rows.value = roster.map(row => ({ ...row, choice: row.status }))
    } catch (error) {
      message.error(error.response?.data?.message || '載入名單失敗')
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .new-season {
    max-width: 860px;
    margin: 0 auto;
  }
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
  .note {
    margin: 4px 0 16px;
    font-size: 15px;
    color: var(--color-text-muted);
  }

  .archive-card {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 20px;
    padding: 16px 18px;
    border-radius: var(--radius-lg);
    background: var(--ink);
    color: var(--bg);
  }
  .archive-card p {
    margin: 2px 0 0;
    font-size: 15px;
    opacity: 0.8;
  }
  .basics {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0 16px;
  }

  /* 三種去向的顏色：校隊藍、校友會金、離隊灰 */

  .confirm-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 24px 0 28px;
    text-align: center;
  }
  .confirm-eyebrow {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--red-500);
  }
  .confirm-hero h2 {
    margin: 0;
    font-size: 36px;
    font-weight: 800;
    color: var(--blue-900);
    animation: pop-in var(--duration-slow) var(--ease-spring) both;
  }
  .confirm-date {
    color: var(--color-text-muted);
  }
  .outcomes {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
  }
  .outcome.team {
    --edge: var(--ink);
    --tint: var(--surface);
  }
  .outcome.alumni {
    --edge: var(--accent);
    --tint: var(--accent-tint);
  }
  .outcome.left {
    --edge: var(--ink-4);
    --tint: var(--surface-sunk);
  }
  .outcome {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 16px;
    border-radius: var(--radius-lg);
    border: 1px solid var(--line-soft);
    border-top: 3px solid var(--edge);
    background: var(--tint);
  }
  .outcome-label {
    font-size: 15px;
    font-weight: 700;
    color: var(--gray-700);
  }
  .outcome-count {
    font-size: 32px;
    font-weight: 700;
    color: var(--blue-900);
  }
  .outcome-moved {
    font-size: 14px;
    color: var(--gray-700);
  }
  .effects {
    margin: 20px 0 0;
    padding-left: 20px;
    color: var(--gray-700);
    line-height: 1.8;
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
  @keyframes pop-in {
    from {
      opacity: 0;
      transform: scale(0.8);
    }
  }

  @media (max-width: 640px) {
    .panel {
      padding: 16px;
    }
    .steps :deep(.n-step:not(.n-step--process-status) .n-step-content) {
      display: none;
    }
    .basics,
    .outcomes {
      grid-template-columns: minmax(0, 1fr);
    }
    .nav {
      bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
    }
  }
</style>
