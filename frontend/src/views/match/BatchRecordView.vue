<template>
  <div class="batch-page">
    <PageHeader
      eyebrow="BATCH ENTRY"
      title="批次記錄"
      subtitle="事後補登多場比賽：一列一場，打字搜尋球員、比分輸入 4-2，按 Enter 新增下一列。"
    >
      <template #actions>
        <n-button quaternary @click="router.push({ name: 'RecordMatch' })">
          <template #icon><n-icon :component="Pedestrian" /></template>
          改用單場精靈
        </n-button>
      </template>
    </PageHeader>

    <Transition name="banner">
      <div v-if="lastSaved" class="saved-banner">
        <span class="saved-icon">🎉</span>
        <span>
          已建立 <strong class="num">{{ lastSaved }}</strong> 場比賽紀錄，排名分數已依日期重新計算。
        </span>
        <n-button text type="primary" @click="router.push({ name: 'MatchManagement' })">到比賽管理查看 →</n-button>
        <n-button text class="banner-close" aria-label="關閉" @click="lastSaved = 0">
          <n-icon :component="Close" />
        </n-button>
      </div>
    </Transition>

    <section class="shared">
      <span class="shared-title">整批共用</span>
      <n-select
        v-model:value="shared.court_surface"
        :options="courtSurfaceOptions"
        clearable
        placeholder="場地"
        class="shared-field"
      />
      <n-select
        v-model:value="shared.court_environment"
        :options="courtEnvironmentOptions"
        clearable
        placeholder="室內外"
        class="shared-field"
      />
      <n-select
        v-model:value="shared.time_slot"
        :options="timeSlotOptions"
        clearable
        placeholder="時段"
        class="shared-field"
      />
      <span class="shared-hint">日期、單雙打、賽制可以每列不同；新的一列會沿用上一列。</span>
    </section>

    <n-alert v-if="playersError" type="error" :title="playersError" class="block">
      <n-button size="small" @click="loadPlayers">重試</n-button>
    </n-alert>

    <TransitionGroup name="row" tag="ol" class="rows">
      <li
        v-for="(row, index) in rows"
        :key="row.key"
        :data-row="row.key"
        class="row"
        :class="[`is-${statuses[index].state}`, winners[index] && `won-${winners[index]}`]"
      >
        <div class="row-index num">{{ index + 1 }}</div>

        <div class="row-main">
          <div class="side side-a">
            <n-select
              v-for="(field, slot) in sideFields(row, 'a')"
              :key="field"
              :ref="el => slot === 0 && setFirstSelect(row.key, el)"
              :value="row[field]"
              :options="optionsFor(row, field)"
              :render-label="renderPlayer"
              :filter="filterPlayer"
              :loading="playersLoading"
              filterable
              clearable
              :consistent-menu-width="false"
              show-on-focus
              placeholder="隊伍 A"
              @update:value="value => setField(row, field, value)"
            />
          </div>

          <div class="side side-b">
            <n-select
              v-for="field in sideFields(row, 'b')"
              :key="field"
              :value="row[field]"
              :options="optionsFor(row, field)"
              :render-label="renderPlayer"
              :filter="filterPlayer"
              :loading="playersLoading"
              filterable
              clearable
              :consistent-menu-width="false"
              show-on-focus
              placeholder="隊伍 B"
              @update:value="value => setField(row, field, value)"
            />
          </div>

          <!-- 放在最後讓 Tab 順序是 A1 → A2 → B1 → B2 → 比分；畫面位置由 grid-area 決定 -->
          <div class="score" :class="{ locked: hasGameScores(row) }">
            <input
              class="score-input num"
              :value="scoreDraft(row)"
              :disabled="hasGameScores(row)"
              :title="hasGameScores(row) ? '由每局比分計算' : '輸入總局數，例如 4-2'"
              placeholder="4-2"
              inputmode="numeric"
              :aria-label="`第 ${index + 1} 場比分`"
              @input="event => onScoreInput(row, event.target.value)"
              @blur="scoreDrafts[row.key] = undefined"
              @keydown.enter.exact.prevent="addRow(index)"
            />
            <span class="score-caption">{{ formatToWin(row) }}</span>
          </div>
        </div>

        <div class="row-meta">
          <n-date-picker
            :value="row.match_date_ts"
            type="date"
            size="small"
            class="meta-date"
            :is-date-disabled="ts => ts > Date.now()"
            @update:value="value => setField(row, 'match_date_ts', value ?? Date.now())"
          />
          <n-radio-group
            :value="row.match_type"
            size="small"
            @update:value="value => setField(row, 'match_type', value)"
          >
            <n-radio-button v-for="option in matchTypeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </n-radio-button>
          </n-radio-group>
          <n-select
            :value="row.match_format"
            :options="matchFormatOptions"
            size="small"
            class="meta-format"
            @update:value="value => setField(row, 'match_format', value)"
          />
          <n-button size="small" :type="hasGameScores(row) ? 'primary' : 'default'" secondary @click="openGames(row)">
            <template #icon><n-icon :component="Grid" /></template>
            {{ hasGameScores(row) ? '已填每局比分' : '每局比分（選填）' }}
          </n-button>

          <span class="status" :class="statuses[index].state">
            <n-icon :component="STATUS_ICONS[statuses[index].state]" />
            {{ statuses[index].message || STATUS_TEXT[statuses[index].state] }}
          </span>

          <div class="row-actions">
            <n-button size="small" quaternary circle title="複製這一列" @click="duplicateRow(index)">
              <template #icon><n-icon :component="Copy" /></template>
            </n-button>
            <n-button size="small" quaternary circle title="刪除這一列" @click="removeRow(index)">
              <template #icon><n-icon :component="TrashCan" /></template>
            </n-button>
          </div>
        </div>
      </li>
    </TransitionGroup>

    <button type="button" class="add-row" @click="addRow(rows.length - 1)">
      <n-icon :component="Add" :size="20" />
      新增一列
      <kbd>Enter</kbd>
    </button>

    <footer class="save-bar">
      <div class="counts">
        <span class="count ready">
          <strong class="num"><CountUp :value="counts.ready" :duration="400" /></strong> 場可儲存
        </span>
        <span v-if="counts.incomplete" class="count incomplete">{{ counts.incomplete }} 場未完成</span>
        <span v-if="counts.invalid" class="count invalid">{{ counts.invalid }} 場有問題</span>
      </div>
      <div class="progress" aria-hidden="true">
        <span class="progress-fill" :style="{ width: `${progress}%` }"></span>
      </div>
      <n-button quaternary :disabled="saving" @click="confirmClear">清空</n-button>
      <n-button
        type="primary"
        size="large"
        class="save-button"
        :class="{ pulse: counts.ready && !saving }"
        :disabled="!counts.ready"
        :loading="saving"
        @click="save"
      >
        儲存 {{ counts.ready || '' }} 場
        <kbd class="save-kbd">{{ modKey }}+Enter</kbd>
      </n-button>
    </footer>

    <n-modal
      :show="Boolean(gamesRow)"
      preset="card"
      :title="gamesRow ? `第 ${rows.indexOf(gamesRow) + 1} 場・每局比分` : ''"
      style="width: min(640px, 94vw)"
      @update:show="value => !value && (gamesRowKey = null)"
    >
      <GameScoreEditor
        v-if="gamesRow"
        :model-value="gamesRow"
        @update:model-value="value => replaceRow(gamesRow.key, value)"
        @completed="celebrate({ particleCount: 50 })"
      />
      <template #footer>
        <div class="modal-footer">
          <n-button type="primary" @click="gamesRowKey = null">完成</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { computed, h, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog, useMessage } from 'naive-ui'
  import {
    Add,
    CheckmarkFilled,
    CircleDash,
    Close,
    Copy,
    Grid,
    Pedestrian,
    Time,
    TrashCan,
    WarningAlt
  } from '@vicons/carbon'
  import { matchesApi, membersApi } from '@/api'
  import CountUp from '@/components/base/CountUp.vue'
  import PageHeader from '@/components/base/PageHeader.vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import GameScoreEditor from '@/components/match/GameScoreEditor.vue'
  import { useOptions } from '@/composables/useOptions'
  import {
    batchErrorsByIndex,
    batchPayload,
    isEmptyRow,
    newBatchRow,
    parseScoreText,
    rowDefaultsFrom,
    rowStatus,
    scoreText,
    winnerOf
  } from '@/utils/batchRecord'
  import { celebrate } from '@/utils/celebrate'
  import { hasGameScores } from '@/utils/matchForm'
  import { gamesToWin } from '@/utils/matchRules'
  import { organizationLabel } from '@/utils/player'

  const DRAFT_KEY = 'tkust:batch-record-draft'
  const STATUS_ICONS = {
    empty: CircleDash,
    incomplete: Time,
    invalid: WarningAlt,
    ready: CheckmarkFilled
  }
  const STATUS_TEXT = { empty: '空白列，儲存時略過', incomplete: '', invalid: '', ready: '可以儲存' }

  const router = useRouter()
  const message = useMessage()
  const dialog = useDialog()
  const { courtSurfaceOptions, courtEnvironmentOptions, timeSlotOptions, matchTypeOptions, matchFormatOptions } =
    useOptions()
  const modKey = /Mac|iPhone|iPad/.test(navigator.platform) ? '⌘' : 'Ctrl'

  const rows = ref([newBatchRow()])
  const shared = reactive({ court_surface: 'hard_court', court_environment: 'outdoor', time_slot: null })
  const players = ref([])
  const playersLoading = ref(false)
  const playersError = ref('')
  const saving = ref(false)
  const lastSaved = ref(0)
  const gamesRowKey = ref(null)
  // 正在輸入中的比分文字（例如只打了「4」），離開欄位後改顯示整理過的比分
  const scoreDrafts = reactive({})
  const firstSelects = new Map()

  const statuses = computed(() => rows.value.map(rowStatus))
  const winners = computed(() => rows.value.map(winnerOf))
  const counts = computed(() => {
    const result = { ready: 0, incomplete: 0, invalid: 0 }
    for (const { state } of statuses.value) if (state in result) result[state]++
    return result
  })
  const progress = computed(() => {
    const filled = counts.value.ready + counts.value.incomplete + counts.value.invalid
    return filled ? Math.round((counts.value.ready / filled) * 100) : 0
  })
  const gamesRow = computed(() => rows.value.find(row => row.key === gamesRowKey.value) || null)

  // ---------- 球員選單 ----------

  const playerOptions = computed(() => players.value.map(member => ({ label: member.name, value: member.id, member })))

  const sideFields = (row, side) => {
    const fields = side === 'a' ? ['player1_id', 'player2_id'] : ['player3_id', 'player4_id']
    return row.match_type === 'singles' ? fields.slice(0, 1) : fields
  }

  /** 同一列已經選過的球員在其他欄位停用。 */
  const optionsFor = (row, field) => {
    const taken = new Set([...sideFields(row, 'a'), ...sideFields(row, 'b')].filter(f => f !== field).map(f => row[f]))
    return playerOptions.value.map(option => (taken.has(option.value) ? { ...option, disabled: true } : option))
  }

  const filterPlayer = (pattern, option) => {
    const term = pattern.trim().toLowerCase()
    const { member } = option
    return [member.name, member.organization?.name, member.organization?.short_name]
      .filter(Boolean)
      .some(text => text.toLowerCase().includes(term))
  }

  const renderPlayer = option => {
    const { member } = option
    // 球員名單還沒載入（例如剛還原草稿）時，選單只拿得到 id
    if (!member) return playersLoading.value ? '載入中…' : `#${option.value}`
    return h('span', { class: 'batch-player-option' }, [
      h(PlayerAvatar, { name: member.name, id: member.id, src: member.avatar_url, size: 22 }),
      h('span', { class: 'batch-player-option__name' }, member.name),
      h(
        'span',
        { class: 'batch-player-option__meta' },
        member.is_guest ? `訪客${orgSuffix(member)}` : organizationLabel(member)
      )
    ])
  }

  const orgSuffix = member => (member.organization ? `・${organizationLabel(member)}` : '')

  const loadPlayers = async () => {
    playersLoading.value = true
    playersError.value = ''
    try {
      players.value = await membersApi.list({ include_guests: true, sort_by: 'name', sort_order: 'asc' })
    } catch (err) {
      playersError.value = err.response?.data?.message || '無法載入球員名單'
    } finally {
      playersLoading.value = false
    }
  }

  // ---------- 列的編輯 ----------

  const replaceRow = (key, value) => {
    const index = rows.value.findIndex(row => row.key === key)
    if (index !== -1) rows.value[index] = { ...value, key, server_error: '' }
  }

  const setField = (row, field, value) => {
    const changes = { [field]: value }
    if (field === 'match_type' && value === 'singles') Object.assign(changes, { player2_id: null, player4_id: null })
    replaceRow(row.key, { ...row, ...changes })
  }

  const scoreDraft = row => scoreDrafts[row.key] ?? scoreText(row)

  const onScoreInput = (row, text) => {
    scoreDrafts[row.key] = text
    const parsed = parseScoreText(text)
    if (parsed) replaceRow(row.key, { ...row, a_games: parsed.a, b_games: parsed.b })
    else if (!text.trim()) replaceRow(row.key, { ...row, a_games: 0, b_games: 0 })
  }

  const formatToWin = row => (hasGameScores(row) ? '由每局比分計算' : `先贏 ${gamesToWin(row.match_format)} 局`)

  const setFirstSelect = (key, el) => {
    if (el) firstSelects.set(key, el)
    else firstSelects.delete(key)
  }

  /** 新的一列從第一位球員開始填；複製的列球員已經填好，直接跳到比分。 */
  const focusRow = async (key, target = 'player') => {
    await nextTick()
    const element = document.querySelector(`[data-row="${key}"]`)
    // 避免新的一列被底部的儲存列擋住
    element?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    if (target === 'score') element?.querySelector('.score-input')?.focus({ preventScroll: true })
    else firstSelects.get(key)?.focus()
  }

  const addRow = (afterIndex, defaults = rowDefaultsFrom(rows.value[afterIndex]), focus = 'player') => {
    const row = newBatchRow(defaults)
    rows.value.splice(afterIndex + 1, 0, row)
    focusRow(row.key, focus)
  }

  const duplicateRow = index => {
    const source = rows.value[index]
    const { player1_id, player2_id, player3_id, player4_id } = source
    addRow(index, { ...rowDefaultsFrom(source), player1_id, player2_id, player3_id, player4_id }, 'score')
  }

  const removeRow = index => {
    rows.value.splice(index, 1)
    if (!rows.value.length) rows.value.push(newBatchRow())
  }

  const openGames = row => {
    gamesRowKey.value = row.key
  }

  const confirmClear = () => {
    if (rows.value.every(isEmptyRow)) return
    dialog.warning({
      title: '清空所有列？',
      content: '還沒儲存的比賽都會被清掉。',
      positiveText: '清空',
      negativeText: '取消',
      onPositiveClick: () => {
        rows.value = [newBatchRow(rowDefaultsFrom(rows.value[0]))]
      }
    })
  }

  // ---------- 儲存 ----------

  const save = () => {
    if (!counts.value.ready || saving.value) return
    const pending = counts.value.incomplete + counts.value.invalid
    if (!pending) return submit()
    dialog.info({
      title: `只儲存 ${counts.value.ready} 場完成的比賽？`,
      content: `另外 ${pending} 場還沒填完或有問題，會留在表格裡。`,
      positiveText: '儲存完成的',
      negativeText: '回去修改',
      onPositiveClick: submit
    })
  }

  const submit = async () => {
    const ready = rows.value.filter((_, index) => statuses.value[index].state === 'ready')
    saving.value = true
    try {
      const created = await matchesApi.createBatch(batchPayload(ready, shared))
      const savedKeys = new Set(ready.map(row => row.key))
      const lastRow = ready.at(-1)
      rows.value = rows.value.filter(row => !savedKeys.has(row.key) && !isEmptyRow(row))
      if (!rows.value.length) addRow(-1, rowDefaultsFrom(lastRow))
      lastSaved.value = created.length
      celebrate({ particleCount: 140, spread: 100 })
    } catch (err) {
      const data = err.response?.data
      const errors = batchErrorsByIndex(data?.details)
      for (const [index, text] of Object.entries(errors)) {
        const row = ready[index]
        if (row) replaceRow(row.key, { ...row, server_error: text })
      }
      message.error(data?.message || '儲存失敗，請稍後再試')
    } finally {
      saving.value = false
    }
  }

  const onKeydown = event => {
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
      event.preventDefault()
      save()
    }
  }

  // ---------- 草稿 ----------

  const restoreDraft = () => {
    try {
      const draft = JSON.parse(localStorage.getItem(DRAFT_KEY) || 'null')
      if (!draft?.rows?.some(row => !isEmptyRow(row))) return
      rows.value = draft.rows.map(row => ({ ...newBatchRow(), ...row, key: newBatchRow().key }))
      Object.assign(shared, draft.shared)
      message.info(`已還原上次未儲存的 ${draft.rows.filter(row => !isEmptyRow(row)).length} 場比賽`)
    } catch {
      // 草稿壞掉就當作沒有
    }
  }

  watch(
    [rows, shared],
    () => {
      try {
        if (rows.value.every(isEmptyRow)) localStorage.removeItem(DRAFT_KEY)
        else localStorage.setItem(DRAFT_KEY, JSON.stringify({ rows: rows.value, shared }))
      } catch {
        // 無法使用 localStorage（例如隱私模式）時不保存草稿
      }
    },
    { deep: true }
  )

  onMounted(() => {
    restoreDraft()
    loadPlayers()
    window.addEventListener('keydown', onKeydown)
    focusRow(rows.value[0].key)
  })
  onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
  .batch-page {
    padding-bottom: 96px;
  }
  .block {
    margin-bottom: 16px;
  }

  /* 儲存成功的橫幅 */
  .saved-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 14px 18px;
    margin-bottom: 16px;
    border-radius: var(--radius-lg);
    background: var(--win-tint);
    border: 1px solid #bbf7d0;
    color: #14532d;
    font-weight: 600;
  }
  .saved-icon {
    font-size: 22px;
    animation: pop var(--duration-slow) var(--ease-spring);
  }
  .banner-close {
    margin-left: auto;
  }
  .banner-enter-active,
  .banner-leave-active {
    transition:
      opacity var(--duration-base) var(--ease-out),
      transform var(--duration-base) var(--ease-out);
  }
  .banner-enter-from,
  .banner-leave-to {
    opacity: 0;
    transform: translateY(-12px);
  }

  /* 整批共用設定 */
  .shared {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    padding: 12px 16px;
    margin-bottom: 18px;
    border-radius: var(--radius-lg);
    background: var(--blue-50);
    border: 1px dashed var(--blue-200);
  }
  .shared-title {
    font-weight: 800;
    color: var(--blue-900);
  }
  .shared-field {
    width: 140px;
  }
  .shared-hint {
    font-size: 13px;
    color: var(--color-text-muted);
  }

  /* 每一列 */
  .rows {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .row {
    position: relative;
    display: grid;
    grid-template-columns: 40px minmax(0, 1fr);
    grid-template-areas:
      'index main'
      'index meta';
    gap: 10px 14px;
    padding: 14px 16px 12px;
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    transition:
      border-color var(--duration-base) var(--ease-out),
      box-shadow var(--duration-base) var(--ease-out),
      transform var(--duration-base) var(--ease-out);
  }
  .row::before {
    content: '';
    position: absolute;
    left: 0;
    top: 12px;
    bottom: 12px;
    width: 4px;
    border-radius: 0 4px 4px 0;
    background: var(--gray-200);
    transition: background var(--duration-base) var(--ease-out);
  }
  .row:focus-within {
    border-color: var(--blue-200);
    box-shadow: var(--shadow-md);
  }
  .row.is-ready::before {
    background: var(--green-500);
  }
  .row.is-incomplete::before {
    background: var(--gold-500);
  }
  .row.is-invalid {
    border-color: #fecaca;
  }
  .row.is-invalid::before {
    background: var(--red-500);
  }
  .row.is-invalid .score-input {
    animation: shake 0.4s;
  }

  .row-index {
    grid-area: index;
    align-self: start;
    display: grid;
    place-items: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--gray-100);
    color: var(--gray-500);
    font-size: 20px;
    font-weight: 700;
    transition:
      background var(--duration-base) var(--ease-out),
      color var(--duration-base) var(--ease-out);
  }
  .row.is-ready .row-index {
    background: var(--green-100);
    color: var(--green-600);
    animation: pop var(--duration-slow) var(--ease-spring);
  }

  .row-main {
    grid-area: main;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 128px minmax(0, 1fr);
    grid-template-areas: 'a score b';
    align-items: center;
    gap: 14px;
  }
  .side {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
    gap: 8px;
    padding: 6px;
    border-radius: var(--radius-md);
    transition: background var(--duration-base) var(--ease-out);
  }
  .side-a {
    grid-area: a;
  }
  .side-b {
    grid-area: b;
  }
  .score {
    grid-area: score;
  }
  .row.won-a .side-a,
  .row.won-b .side-b {
    background: var(--accent-tint);
    box-shadow: inset 0 0 0 1px var(--gold-300);
  }

  /* 比分 */
  .score {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }
  .score-input {
    width: 100%;
    height: 52px;
    border: 2px solid var(--gray-200);
    border-radius: var(--radius-md);
    background: var(--gray-100);
    color: var(--blue-900);
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    letter-spacing: 0.08em;
    outline: none;
    transition:
      border-color var(--duration-fast) var(--ease-out),
      background var(--duration-fast) var(--ease-out),
      transform var(--duration-fast) var(--ease-out);
  }
  .score-input::placeholder {
    color: var(--gray-300);
  }
  .score-input:focus {
    border-color: var(--blue-500);
    background: var(--surface-2);
    transform: scale(1.04);
  }
  .score-input:disabled {
    cursor: not-allowed;
    background: var(--blue-50);
    border-style: dashed;
  }
  .row.is-ready .score-input {
    border-color: var(--green-500);
    background: var(--surface-2);
  }
  .score-caption {
    font-size: 11px;
    color: var(--color-text-muted);
  }

  /* 第二行：日期、類型、賽制、狀態 */
  .row-meta {
    grid-area: meta;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .meta-date {
    width: 140px;
  }
  .meta-format {
    width: 96px;
  }
  .status {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    font-weight: 600;
    color: var(--color-text-muted);
  }
  .status.ready {
    color: var(--green-600);
  }
  .status.incomplete {
    color: #a16207;
  }
  .status.invalid {
    color: var(--red-600);
  }
  .row-actions {
    margin-left: auto;
    display: flex;
    gap: 2px;
  }

  /* 列的進出場動畫 */
  .row-enter-active {
    transition:
      opacity var(--duration-base) var(--ease-out),
      transform var(--duration-slow) var(--ease-spring);
  }
  .row-leave-active {
    transition:
      opacity var(--duration-base) var(--ease-out),
      transform var(--duration-base) var(--ease-out);
  }
  .row-enter-from {
    opacity: 0;
    transform: translateY(-14px) scale(0.97);
  }
  .row-leave-to {
    opacity: 0;
    transform: translateX(60px);
  }
  .row-move {
    transition: transform var(--duration-base) var(--ease-out);
  }

  .add-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    margin-top: 12px;
    padding: 14px;
    border: 2px dashed var(--blue-200);
    border-radius: var(--radius-lg);
    background: transparent;
    color: var(--blue-700);
    font: inherit;
    font-weight: 700;
    cursor: pointer;
    transition:
      background var(--duration-fast) var(--ease-out),
      border-color var(--duration-fast) var(--ease-out);
  }
  .add-row:hover {
    background: var(--blue-50);
    border-color: var(--blue-400);
  }
  kbd {
    padding: 1px 6px;
    border-radius: 6px;
    border: 1px solid currentColor;
    font-family: var(--font-number);
    font-size: 12px;
    opacity: 0.6;
  }

  /* 底部儲存列 */
  .save-bar {
    position: sticky;
    bottom: 16px;
    z-index: 10;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 20px;
    padding: 12px 14px 12px 20px;
    border-radius: var(--radius-xl);
    background: color-mix(in srgb, var(--surface) 92%, transparent);
    backdrop-filter: blur(10px);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-lg);
  }
  .counts {
    display: flex;
    align-items: baseline;
    gap: 14px;
    white-space: nowrap;
  }
  .count {
    font-size: 13px;
    font-weight: 600;
  }
  .count.ready strong {
    font-size: 26px;
    color: var(--green-600);
  }
  .count.incomplete {
    color: #a16207;
  }
  .count.invalid {
    color: var(--red-600);
  }
  .progress {
    flex: 1;
    height: 8px;
    border-radius: var(--radius-full);
    background: var(--gray-100);
    overflow: hidden;
  }
  .progress-fill {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: var(--win);
    transition: width var(--duration-slow) var(--ease-spring);
  }
  .save-kbd {
    margin-left: 8px;
    border-color: var(--line);
  }
  .save-button.pulse {
    animation: pulse 2s infinite;
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
  }

  @keyframes pop {
    0% {
      transform: scale(0.6);
    }
    100% {
      transform: scale(1);
    }
  }
  @keyframes shake {
    0%,
    100% {
      transform: translateX(0);
    }
    25% {
      transform: translateX(-4px);
    }
    75% {
      transform: translateX(4px);
    }
  }
  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(31, 79, 168, 0.45);
    }
    70% {
      box-shadow: 0 0 0 12px rgba(31, 79, 168, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(31, 79, 168, 0);
    }
  }

  @media (max-width: 900px) {
    .row-main {
      grid-template-columns: minmax(0, 1fr);
      grid-template-areas: 'a' 'score' 'b';
    }
    .save-bar {
      flex-wrap: wrap;
      bottom: calc(var(--bottom-nav-height) + 12px);
    }
    .progress {
      order: 3;
      flex-basis: 100%;
    }
    .save-kbd {
      display: none;
    }
  }
</style>

<style>
  /* 下拉選單會被移到 body 底下，scoped 樣式套不到 */
  .batch-player-option {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
  }
  .batch-player-option__name {
    font-weight: 600;
  }
  .batch-player-option__meta {
    font-size: 12px;
    color: var(--color-text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
