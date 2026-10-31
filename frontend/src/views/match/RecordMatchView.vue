<template>
  <div class="record-page">
    <PageHeader :eyebrow="isEdit ? 'Edit' : 'Record'" :title="isEdit ? '編輯比賽' : '記錄一場'">
      <template v-if="!isEdit" #actions>
        <n-button size="small" @click="router.push({ name: 'BatchRecordMatch' })">
          <template #icon><n-icon :component="Layers" /></template>
          批次補登
        </n-button>
      </template>
    </PageHeader>

    <n-spin :show="loading">
      <!-- 設定：日期、單雙打、賽制、分類 -->
      <section class="block settings">
        <n-date-picker v-model:value="form.match_date_ts" type="date" class="date" :clearable="false" />
        <div class="segments" role="radiogroup" aria-label="單雙打">
          <button
            v-for="option in matchTypeOptions"
            :key="option.value"
            type="button"
            class="segment"
            :class="{ active: form.match_type === option.value }"
            @click="form.match_type = option.value"
          >
            {{ option.label }}
          </button>
        </div>
        <div class="segments" role="radiogroup" aria-label="賽制">
          <button
            v-for="option in matchFormatOptions"
            :key="option.value"
            type="button"
            class="segment"
            :class="{ active: form.match_format === option.value }"
            @click="changeFormat(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
        <MatchCategoryPicker v-model:category="form.category" v-model:event-id="form.event_id" class="category" />
      </section>

      <!-- 兩隊球員 -->
      <section class="block teams">
        <div v-for="side in SIDES" :key="side.key" class="team" :class="[side.key, { won: winner === side.key }]">
          <span class="hud-label">{{ side.label }}<template v-if="winner === side.key"> · 勝</template></span>
          <PlayerSelect
            v-for="field in fieldsOf(side)"
            :key="field"
            v-model="form[field]"
            :players="players"
            :excluded="chosenIds"
            :organizations="organizations"
            @created="loadPlayers"
          />
        </div>
      </section>

      <!-- 比分 -->
      <section class="block score">
        <div class="quick">
          <div v-for="side in SIDES" :key="side.key" class="quick-row">
            <span class="hud-label">{{ side.short }}勝</span>
            <button
              v-for="result in quick[side.key]"
              :key="`${result.a}-${result.b}`"
              type="button"
              class="quick-chip num"
              :class="{ active: form.a_games === result.a && form.b_games === result.b && !detailed }"
              :disabled="detailed"
              @click="setScore(result)"
            >
              {{ result.a }}:{{ result.b }}
            </button>
          </div>
        </div>
        <n-collapse :default-expanded-names="detailed ? ['games'] : []">
          <n-collapse-item title="每局比分（選填）" name="games">
            <GameScoreEditor v-model="form" />
          </n-collapse-item>
          <n-collapse-item title="更多資訊（選填）" name="more">
            <n-grid :cols="3" :x-gap="12" responsive="screen" item-responsive>
              <n-form-item-gi span="3 m:1" label="時段" :show-feedback="false">
                <n-select v-model:value="form.time_slot" :options="timeSlotOptions" clearable />
              </n-form-item-gi>
              <n-form-item-gi span="3 m:1" label="場地" :show-feedback="false">
                <n-select v-model:value="form.court_surface" :options="courtSurfaceOptions" clearable />
              </n-form-item-gi>
              <n-form-item-gi span="3 m:1" label="環境" :show-feedback="false">
                <n-select v-model:value="form.court_environment" :options="courtEnvironmentOptions" clearable />
              </n-form-item-gi>
              <n-form-item-gi span="3" label="備註" :show-feedback="false" class="notes">
                <n-input v-model:value="form.match_notes" type="textarea" :rows="2" maxlength="500" />
              </n-form-item-gi>
            </n-grid>
          </n-collapse-item>
        </n-collapse>
      </section>
    </n-spin>

    <footer class="submit-bar">
      <div class="scoreline num" aria-live="polite">
        <span :class="{ won: winner === 'a' }">{{ form.a_games }}</span>
        <span class="colon">:</span>
        <span :class="{ won: winner === 'b' }">{{ form.b_games }}</span>
      </div>
      <span class="status">{{ error }}</span>
      <n-button v-if="isEdit" size="large" @click="router.back()">取消</n-button>
      <n-button type="primary" size="large" :loading="submitting" @click="submit">
        {{ isEdit ? '儲存' : '送出' }}
      </n-button>
    </footer>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { Layers } from '@vicons/carbon'
  import { matchesApi, membersApi, organizationsApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import GameScoreEditor from '@/components/match/GameScoreEditor.vue'
  import MatchCategoryPicker from '@/components/match/MatchCategoryPicker.vue'
  import PlayerSelect from '@/components/match/PlayerSelect.vue'
  import { useOptions } from '@/composables/useOptions'
  import { celebrate } from '@/utils/celebrate'
  import {
    emptyGameFields,
    hasGameScores,
    matchFormFromRecord,
    matchPayloadFromForm,
    newMatchForm,
    recordFormError
  } from '@/utils/matchForm'
  import { quickResults } from '@/utils/matchRules'

  const SIDES = [
    { key: 'a', label: 'A 隊', short: 'A ', fields: ['player1_id', 'player2_id'] },
    { key: 'b', label: 'B 隊', short: 'B ', fields: ['player3_id', 'player4_id'] }
  ]
  // 連續記錄時保留的設定
  const KEEP_FIELDS = ['match_date_ts', 'match_type', 'match_format', 'category', 'event_id', 'time_slot']

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
  const tried = ref(false)
  const form = ref(newMatchForm())
  const players = ref([])
  const organizations = ref([])

  const fieldsOf = side => (form.value.match_type === 'singles' ? side.fields.slice(0, 1) : side.fields)
  const chosenIds = computed(() =>
    SIDES.flatMap(fieldsOf)
      .map(field => form.value[field])
      .filter(Boolean)
  )
  const quick = computed(() => quickResults(form.value.match_format))
  const detailed = computed(() => hasGameScores(form.value))
  const winner = computed(() => {
    const { a_games: a, b_games: b } = form.value
    return a > b ? 'a' : b > a ? 'b' : null
  })
  // 按過送出才顯示錯誤，避免一進來就滿是紅字
  const error = computed(() => (tried.value ? recordFormError(form.value) : ''))

  const setScore = ({ a, b }) => {
    form.value = { ...form.value, a_games: a, b_games: b }
  }

  const changeFormat = value => {
    if (value === form.value.match_format) return
    form.value = { ...form.value, match_format: value, ...emptyGameFields(), a_games: 0, b_games: 0 }
  }

  // 改成單打時清掉搭檔
  watch(
    () => form.value.match_type,
    type => {
      if (type === 'singles') form.value = { ...form.value, player2_id: null, player4_id: null }
    }
  )

  const loadPlayers = async () => {
    players.value = await membersApi.list({ include_guests: true, sort_by: 'roster' })
  }

  const submit = async () => {
    tried.value = true
    if (error.value) {
      message.warning(error.value)
      return
    }
    submitting.value = true
    try {
      const payload = matchPayloadFromForm(form.value)
      if (isEdit.value) {
        const record = await matchesApi.update(props.matchId, payload)
        message.success('比賽紀錄已更新')
        router.push({ name: 'ViewMatch', params: { id: record.id } })
        return
      }
      await matchesApi.create(payload)
      celebrate({ particleCount: 60 })
      message.success('已記錄，可以接著記下一場')
      // 保留日期、賽制、分類，清掉球員與比分
      const kept = Object.fromEntries(KEEP_FIELDS.map(field => [field, form.value[field]]))
      form.value = { ...newMatchForm(), ...kept }
      tried.value = false
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (err) {
      const data = err.response?.data
      message.error(data?.details ? Object.values(data.details).flat().join('；') : data?.message || '送出失敗')
    } finally {
      submitting.value = false
    }
  }

  onMounted(async () => {
    loading.value = true
    try {
      const [, orgs, record] = await Promise.all([
        loadPlayers(),
        organizationsApi.list(),
        isEdit.value ? matchesApi.get(props.matchId) : null
      ])
      organizations.value = orgs
      if (record) form.value = matchFormFromRecord(record)
    } catch {
      message.error(isEdit.value ? '找不到這場比賽' : '載入球員失敗')
      if (isEdit.value) router.push({ name: 'MatchManagement' })
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .record-page {
    max-width: 860px;
    margin: 0 auto;
    padding-bottom: 12px;
  }
  .block {
    margin-bottom: 14px;
    padding: 16px;
    border: 1px solid var(--line-soft);
    background: var(--surface);
  }
  .settings {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
  }
  .date {
    width: 170px;
  }
  .category {
    flex-basis: 100%;
  }
  .segments {
    display: flex;
    border: 1px solid var(--line);
  }
  .segment {
    padding: 8px 14px;
    border: 0;
    border-left: 1px solid var(--line);
    background: transparent;
    color: var(--ink-3);
    font: inherit;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }
  .segment:first-child {
    border-left: 0;
  }
  .segment.active {
    background: var(--ink);
    color: var(--bg);
  }

  .teams {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }
  .team {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-top: 10px;
    border-top: 2px solid var(--line);
    transition: border-color var(--duration-fast);
  }
  .team.won {
    border-top-color: var(--accent);
  }
  .team.won .hud-label {
    color: var(--accent-text);
  }

  .quick {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 8px;
  }
  .quick-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
  }
  .quick-row .hud-label {
    width: 52px;
  }
  .quick-chip {
    min-width: 58px;
    padding: 8px 10px;
    border: 1px solid var(--line);
    background: var(--surface-2);
    color: var(--ink);
    font-size: 17px;
    cursor: pointer;
    transition:
      background var(--duration-fast),
      border-color var(--duration-fast);
  }
  .quick-chip:hover:not(:disabled) {
    border-color: var(--ink);
  }
  .quick-chip.active {
    border-color: var(--ink);
    background: var(--ink);
    color: var(--bg);
  }
  .quick-chip:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .notes {
    margin-top: 10px;
  }

  .submit-bar {
    position: sticky;
    bottom: 0;
    z-index: 5;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    border: 1px solid var(--line);
    border-top: 2px solid var(--accent);
    background: var(--surface-2);
  }
  .scoreline {
    display: flex;
    align-items: baseline;
    gap: 6px;
    font-size: 30px;
    color: var(--ink-3);
  }
  .scoreline .won {
    color: var(--ink);
  }
  .colon {
    font-size: 22px;
  }
  .status {
    flex: 1;
    min-width: 0;
    font-size: 14px;
    color: var(--ink-3);
  }

  @media (max-width: 900px) {
    .submit-bar {
      bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
    }
  }
  @media (max-width: 640px) {
    .teams {
      grid-template-columns: minmax(0, 1fr);
    }
    .date {
      width: 100%;
    }
    .quick-chip {
      flex: 1;
      min-width: 0;
    }
  }
</style>
