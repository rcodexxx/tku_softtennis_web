<template>
  <div class="practice-day">
    <n-button text class="back" @click="router.push({ name: 'Practice' })">
      <template #icon><n-icon :component="ArrowLeft" /></template>
      練習日
    </n-button>

    <n-skeleton v-if="!session" height="120px" />
    <template v-else>
      <PageHeader eyebrow="Practice" :title="session.session_date">
        <template #actions>
          <span class="hud-label">{{ session.location || '' }}</span>
          <n-button size="small" @click="attendeesOpen = true">到場 {{ session.attendees.length }} 人</n-button>
        </template>
      </PageHeader>

      <!-- 排下一輪 -->
      <section class="controls">
        <div class="control">
          <span class="hud-label">場地</span>
          <n-input-number v-model:value="courts" :min="1" :max="maxCourts" size="small" class="courts" />
        </div>
        <div class="segments" role="radiogroup" aria-label="排組方式">
          <button
            v-for="option in MODES"
            :key="option.value"
            type="button"
            class="segment"
            :class="{ active: mode === option.value }"
            @click="mode = option.value"
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
            :class="{ active: format === option.value }"
            @click="format = option.value"
          >
            {{ option.label }}
          </button>
        </div>
        <n-button type="primary" :loading="drawing" :disabled="pending" @click="drawRound">
          <template #icon><n-icon :component="Shuffle" /></template>
          排下一輪
        </n-button>
      </section>

      <section v-if="round.length" class="round">
        <div class="courts-grid">
          <CourtCard
            v-for="(court, index) in round"
            :key="index"
            :court="court"
            :number="index + 1"
            :players="playersById"
            :format="format"
            :saving="savingIndex === index"
            @update="changes => Object.assign(court, changes)"
            @save="saveCourt(index)"
          />
        </div>
        <p v-if="resting.length" class="resting">
          <span class="hud-label">休息</span>
          <span v-for="pid in resting" :key="pid" class="resting-name">{{ playersById[pid]?.name }}</span>
        </p>
      </section>

      <!-- 今日戰報 -->
      <section v-if="summary.lines.length" class="report">
        <div class="section-head">
          <span class="hud-label">今日戰報 · {{ records.length }} 場</span>
          <span class="rule"></span>
        </div>
        <div class="report-grid">
          <ol class="lines">
            <li v-for="(line, index) in summary.lines" :key="line.player.id" class="line">
              <span class="num rank">{{ String(index + 1).padStart(2, '0') }}</span>
              <PlayerAvatar :id="line.player.id" :name="line.player.name" :src="line.player.avatar_url" :size="28" />
              <span class="line-name">{{ line.player.name }}</span>
              <span class="num line-record">{{ line.wins }}W {{ line.losses }}L</span>
              <span class="num line-games">{{ signed(line.games_for - line.games_against) }}</span>
              <ScoreChange :change="line.rating_change" />
            </li>
          </ol>
          <div class="best-pairs">
            <span class="hud-label">今日最佳組合</span>
            <div v-for="pair in summary.pairs.slice(0, 3)" :key="pair.players.map(p => p.id).join('-')" class="pair">
              <span class="pair-names">{{ pair.players.map(p => p.name).join(' / ') }}</span>
              <span class="num">{{ pair.wins }}W {{ pair.losses }}L</span>
            </div>
          </div>
        </div>
      </section>

      <n-modal v-model:show="attendeesOpen" preset="card" title="到場" style="width: min(720px, 96vw)">
        <AttendeePicker v-model="attendeeIds" :players="players" />
        <template #footer>
          <div class="modal-footer">
            <n-button @click="attendeesOpen = false">取消</n-button>
            <n-button type="primary" :loading="savingAttendees" @click="saveAttendees">儲存</n-button>
          </div>
        </template>
      </n-modal>
    </template>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { ArrowLeft, Shuffle } from '@vicons/carbon'
  import { matchesApi, membersApi, practiceApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import ScoreChange from '@/components/leaderboard/ScoreChange.vue'
  import AttendeePicker from '@/components/practice/AttendeePicker.vue'
  import CourtCard from '@/components/practice/CourtCard.vue'
  import { useOptions } from '@/composables/useOptions'

  const MODES = [
    { value: 'rotate', label: '輪換搭檔' },
    { value: 'balanced', label: '實力平均' }
  ]

  const props = defineProps({ id: { type: [String, Number], required: true } })

  const router = useRouter()
  const message = useMessage()
  const { matchFormatOptions } = useOptions()

  const session = ref(null)
  const summary = ref({ lines: [], pairs: [] })
  const records = ref([])
  const players = ref([])
  const round = ref([])
  const resting = ref([])
  const courts = ref(2)
  const mode = ref('rotate')
  const format = ref('games_7')
  const drawing = ref(false)
  const savingIndex = ref(null)
  const attendeesOpen = ref(false)
  const attendeeIds = ref([])
  const savingAttendees = ref(false)

  // 這一輪的排組存在瀏覽器裡，手機重新整理也不會不見
  const roundKey = computed(() => `practice-round-${props.id}`)
  const restoreRound = () => {
    try {
      const saved = JSON.parse(localStorage.getItem(roundKey.value) ?? 'null')
      if (saved) {
        round.value = saved.round
        resting.value = saved.resting
      }
    } catch {
      // 讀不到就重新排
    }
  }
  watch(
    [round, resting],
    () => {
      try {
        if (round.value.length && round.value.some(court => !court.saved)) {
          localStorage.setItem(roundKey.value, JSON.stringify({ round: round.value, resting: resting.value }))
        } else {
          localStorage.removeItem(roundKey.value)
        }
      } catch {
        // 無法存取 localStorage 時只在這次瀏覽有效
      }
    },
    { deep: true }
  )

  const playersById = computed(() => Object.fromEntries(players.value.map(player => [player.id, player])))
  const maxCourts = computed(() => Math.max(1, Math.floor((session.value?.attendees.length ?? 4) / 4)))
  // 這一輪還有沒記錄的場地時，先不排下一輪
  const pending = computed(() => round.value.some(court => !court.saved))
  const signed = value => (value > 0 ? `+${value}` : `${value}`)

  const load = async () => {
    const [detail, list] = await Promise.all([
      practiceApi.get(props.id),
      matchesApi.list({ session_id: props.id, per_page: 200 })
    ])
    const firstLoad = !session.value
    session.value = detail
    summary.value = detail.summary
    records.value = list.items
    attendeeIds.value = detail.attendees.map(player => player.id)
    // 預設盡量用滿場地（最多 3 面），之後照使用者選的
    courts.value = firstLoad ? Math.min(3, maxCourts.value) : Math.min(courts.value, maxCourts.value)
  }

  const drawRound = async () => {
    drawing.value = true
    try {
      const result = await practiceApi.nextRound(props.id, {
        courts: courts.value,
        mode: mode.value,
        seed: Math.floor(Math.random() * 100000)
      })
      round.value = result.courts.map(court => ({
        ...court,
        a_games: null,
        b_games: null,
        a_front_id: null,
        b_front_id: null,
        saved: false
      }))
      resting.value = result.resting
    } finally {
      drawing.value = false
    }
  }

  const saveCourt = async index => {
    const court = round.value[index]
    savingIndex.value = index
    try {
      await matchesApi.create({
        match_date: session.value.session_date,
        match_type: 'doubles',
        match_format: format.value,
        category: 'internal',
        session_id: session.value.id,
        player1_id: court.side_a[0],
        player2_id: court.side_a[1],
        player3_id: court.side_b[0],
        player4_id: court.side_b[1],
        a_front_id: court.a_front_id,
        b_front_id: court.b_front_id,
        a_games: court.a_games,
        b_games: court.b_games
      })
      court.saved = true
      await load()
    } catch (error) {
      message.error(error.response?.data?.message || '記錄失敗')
    } finally {
      savingIndex.value = null
    }
  }

  const saveAttendees = async () => {
    savingAttendees.value = true
    try {
      await practiceApi.update(props.id, { player_ids: attendeeIds.value })
      attendeesOpen.value = false
      await load()
    } finally {
      savingAttendees.value = false
    }
  }

  watch(attendeesOpen, show => {
    if (show) attendeeIds.value = session.value.attendees.map(player => player.id)
  })

  onMounted(async () => {
    restoreRound()
    try {
      const [, list] = await Promise.all([load(), membersApi.list({ include_guests: true, sort_by: 'roster' })])
      players.value = list
    } catch (error) {
      message.error(error.response?.data?.message || '載入練習日失敗')
    }
  })
</script>

<style scoped>
  .practice-day {
    max-width: 1100px;
    margin: 0 auto;
  }
  .back {
    margin-bottom: 8px;
  }
  .controls {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 16px;
    padding: 12px 14px;
    border: 1px solid var(--line-soft);
    background: var(--surface);
  }
  .control {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .courts {
    width: 96px;
  }
  .segments {
    display: flex;
    border: 1px solid var(--line);
  }
  .segment {
    padding: 6px 12px;
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
  .controls > :last-child {
    margin-left: auto;
  }
  .courts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px;
  }
  .resting {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin: 12px 0 0;
  }
  .resting-name {
    padding: 2px 8px;
    border: 1px dashed var(--line);
    color: var(--ink-3);
  }
  .report {
    margin-top: 24px;
  }
  .section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }
  .rule {
    flex: 1;
    height: 1px;
    background: var(--line);
  }
  .report-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
    gap: 16px;
  }
  .lines {
    margin: 0;
    padding: 0;
    list-style: none;
    border: 1px solid var(--line-soft);
  }
  .line {
    display: grid;
    grid-template-columns: 28px 28px minmax(0, 1fr) 70px 44px 60px;
    align-items: center;
    gap: 10px;
    padding: 7px 12px;
    border-top: 1px solid var(--line-soft);
    background: var(--surface);
  }
  .line:first-child {
    border-top: 0;
  }
  .rank,
  .line-games {
    color: var(--ink-3);
    font-size: 14px;
  }
  .line-name {
    font-weight: 600;
    color: var(--ink);
  }
  .line-record {
    color: var(--ink-2);
  }
  .best-pairs {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 14px;
    border: 1px solid var(--line-soft);
    border-top: 2px solid var(--accent);
    background: var(--surface);
    align-self: start;
  }
  .pair {
    display: flex;
    justify-content: space-between;
    gap: 8px;
  }
  .pair-names {
    font-weight: 600;
    color: var(--ink);
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
  @media (max-width: 760px) {
    .report-grid {
      grid-template-columns: minmax(0, 1fr);
    }
    .controls > :last-child {
      margin-left: 0;
      width: 100%;
    }
    .line {
      grid-template-columns: 24px 28px minmax(0, 1fr) 64px 56px;
    }
    .line-games {
      display: none;
    }
  }
</style>
