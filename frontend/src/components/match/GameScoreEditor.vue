<template>
  <div class="score-editor">
    <n-radio-group :value="mode" class="mode" @update:value="switchMode">
      <n-radio-button value="quick">只記總局數</n-radio-button>
      <n-radio-button value="games">記錄每局比分</n-radio-button>
    </n-radio-group>

    <div class="totals">
      <div v-for="side in SIDES" :key="side.key" class="total" :class="[side.key, { won: winner === side.key }]">
        <span class="total-label">{{ side.label }}</span>
        <div class="total-value">
          <n-button
            v-if="mode === 'quick'"
            circle
            secondary
            :disabled="modelValue[side.field] <= 0"
            @click="adjust(side.field, -1)"
          >
            <template #icon><n-icon :component="Subtract" /></template>
          </n-button>
          <span class="num">{{ modelValue[side.field] || 0 }}</span>
          <n-button
            v-if="mode === 'quick'"
            circle
            secondary
            :disabled="modelValue[side.field] >= toWin"
            @click="adjust(side.field, 1)"
          >
            <template #icon><n-icon :component="Add" /></template>
          </n-button>
        </div>
        <span v-if="winner === side.key" class="winner-tag">🏆 獲勝</span>
      </div>
    </div>

    <p class="rule">{{ formatLabel }}：先贏 {{ toWin }} 局獲勝</p>

    <template v-if="mode === 'games'">
      <div class="serve-picker">
        <span>第一局發球</span>
        <n-button-group>
          <n-button
            v-for="side in SIDES"
            :key="side.key"
            :type="modelValue.first_serve_side === side.serve ? 'primary' : 'default'"
            @click="update({ first_serve_side: side.serve })"
          >
            🎾 {{ side.label }}
          </n-button>
        </n-button-group>
      </div>

      <ol class="games">
        <li
          v-for="game in gameRows"
          :key="game.number"
          class="game"
          :class="[game.status, { tiebreak: game.tiebreak, locked: game.locked }]"
        >
          <span class="game-label">{{ game.tiebreak ? '決勝局' : `第 ${game.number} 局` }}</span>
          <span class="serve" :class="{ on: game.serve === 'side_a' }">🎾</span>
          <n-input-number
            :value="game.a"
            :min="0"
            :max="50"
            button-placement="both"
            :disabled="game.locked"
            class="stepper"
            @update:value="value => setScore(game.number, 'a', value)"
          />
          <span class="dash">:</span>
          <n-input-number
            :value="game.b"
            :min="0"
            :max="50"
            button-placement="both"
            :disabled="game.locked"
            class="stepper"
            @update:value="value => setScore(game.number, 'b', value)"
          />
          <span class="serve" :class="{ on: game.serve === 'side_b' }">🎾</span>
          <span class="game-status">{{ game.statusLabel }}</span>
        </li>
      </ol>
      <p class="hint">一般局先拿 4 分（3:3 後需領先 2 分），決勝局先拿 7 分（6:6 後需領先 2 分）。</p>
    </template>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useMessage } from 'naive-ui'
  import { Add, Subtract } from '@vicons/carbon'
  import { useOptions } from '@/composables/useOptions'
  import { emptyGameFields, gameField, gameScoresFromForm, hasGameScores } from '@/utils/matchForm'
  import {
    countGamesWon,
    gamesToWin,
    isTiebreakGame,
    maxGames,
    serveSideForGame,
    validateGameScore
  } from '@/utils/matchRules'

  const SIDES = [
    { key: 'a', label: '隊伍 A', field: 'a_games', serve: 'side_a' },
    { key: 'b', label: '隊伍 B', field: 'b_games', serve: 'side_b' }
  ]

  /** 比分輸入。modelValue 為比賽表單；修改時回傳新物件，比賽分出勝負時發出 completed。 */
  const props = defineProps({ modelValue: { type: Object, required: true } })
  const emit = defineEmits(['update:modelValue', 'completed'])

  const message = useMessage()
  const { getMatchFormatDisplay } = useOptions()
  const mode = ref(hasGameScores(props.modelValue) ? 'games' : 'quick')

  const format = computed(() => props.modelValue.match_format)
  const toWin = computed(() => gamesToWin(format.value))
  const formatLabel = computed(() => getMatchFormatDisplay(format.value))
  const winner = computed(() => {
    const { a_games: a = 0, b_games: b = 0 } = props.modelValue
    if (a >= toWin.value && a > b) return 'a'
    if (b >= toWin.value && b > a) return 'b'
    return null
  })

  const gameRows = computed(() => {
    const scores = gameScoresFromForm(props.modelValue)
    let decided = false
    return Array.from({ length: maxGames(format.value) }, (_, index) => {
      const number = index + 1
      const { a, b } = scores[index]
      const tiebreak = isTiebreakGame(format.value, number)
      const result = validateGameScore(a, b, tiebreak)
      const played = a > 0 || b > 0
      const row = {
        number,
        a,
        b,
        tiebreak,
        serve: serveSideForGame(props.modelValue.first_serve_side, number),
        locked: decided && !played,
        status: !played
          ? 'empty'
          : !result.isValid
            ? 'invalid'
            : result.gameFinished
              ? `won-${result.winner.toLowerCase()}`
              : 'playing',
        statusLabel: !played ? '' : !result.isValid ? '無效' : result.gameFinished ? `${result.winner} 勝` : '進行中'
      }
      // 已分出勝負後，後面沒打的局就鎖住
      const won = countGamesWon(scores.slice(0, number), format.value)
      if (won.aWins >= toWin.value || won.bWins >= toWin.value) decided = true
      return row
    })
  })

  const update = changes => emit('update:modelValue', { ...props.modelValue, ...changes })

  const adjust = (field, delta) => {
    const value = (props.modelValue[field] || 0) + delta
    const next = { ...props.modelValue, [field]: value }
    emit('update:modelValue', next)
    notifyIfCompleted(props.modelValue, next)
  }

  const setScore = (number, side, value) => {
    const next = { ...props.modelValue, [gameField(number, side)]: value ?? 0 }
    const { aWins, bWins, error } = countGamesWon(gameScoresFromForm(next), format.value)
    if (error) {
      emit('update:modelValue', next)
      return
    }
    const withTotals = { ...next, a_games: aWins, b_games: bWins }
    emit('update:modelValue', withTotals)
    notifyIfCompleted(props.modelValue, withTotals)
  }

  const isDecided = form => {
    const t = toWin.value
    return (form.a_games >= t || form.b_games >= t) && form.a_games !== form.b_games
  }

  const notifyIfCompleted = (before, after) => {
    if (!isDecided(before) && isDecided(after)) emit('completed', after.a_games > after.b_games ? 'a' : 'b')
  }

  const switchMode = value => {
    if (value === 'quick' && hasGameScores(props.modelValue)) {
      message.info('已清除每局比分，改為只記總局數')
      update(emptyGameFields())
    }
    if (value === 'games')
      update({
        ...emptyGameFields(),
        a_games: 0,
        b_games: 0,
        first_serve_side: props.modelValue.first_serve_side || 'side_a'
      })
    mode.value = value
  }
</script>

<style scoped>
  .mode {
    margin-bottom: 18px;
  }
  .totals {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .total {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 18px;
    border-radius: var(--radius-lg);
    border: 2px solid var(--color-border);
    background: var(--color-surface);
    transition:
      border-color var(--duration-base),
      transform var(--duration-base) var(--ease-spring);
  }
  .total.a.won {
    border-color: var(--blue-500);
    transform: scale(1.02);
  }
  .total.b.won {
    border-color: var(--red-500);
    transform: scale(1.02);
  }
  .total-label {
    font-weight: 800;
  }
  .a .total-label {
    color: var(--blue-700);
  }
  .b .total-label {
    color: var(--red-600);
  }
  .total-value {
    display: flex;
    align-items: center;
    gap: 18px;
  }
  .total-value .num {
    min-width: 56px;
    text-align: center;
    font-size: 64px;
    font-weight: 700;
    line-height: 1;
    color: var(--blue-900);
  }
  .winner-tag {
    position: absolute;
    top: 10px;
    right: 12px;
    font-size: 13px;
    font-weight: 800;
    color: var(--accent-text);
    animation: stagger-in var(--duration-base) var(--ease-spring) both;
  }
  .rule {
    margin: 10px 0 20px;
    text-align: center;
    font-size: 13px;
    color: var(--color-text-muted);
  }
  .serve-picker {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
    font-weight: 700;
    color: var(--gray-700);
  }
  .games {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .game {
    display: grid;
    grid-template-columns: 64px 20px minmax(0, 1fr) 12px minmax(0, 1fr) 20px 56px;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-radius: var(--radius-md);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    transition: background var(--duration-base);
  }
  .game.tiebreak .game-label {
    color: var(--red-500);
  }
  .game.won-a {
    background: var(--blue-50);
  }
  .game.won-b {
    background: #fff5f5;
  }
  .game.invalid {
    border-color: var(--red-500);
  }
  .game.locked {
    opacity: 0.45;
  }
  .game-label {
    font-size: 13px;
    font-weight: 700;
    color: var(--gray-500);
  }
  .serve {
    opacity: 0.12;
    filter: grayscale(1);
    text-align: center;
  }
  .serve.on {
    opacity: 1;
    filter: none;
  }
  .dash {
    text-align: center;
    font-weight: 700;
    color: var(--gray-400);
  }
  .stepper :deep(input) {
    text-align: center;
    font-family: var(--font-number);
    font-size: 18px;
    font-weight: 600;
  }
  .game-status {
    font-size: 12px;
    font-weight: 700;
    text-align: right;
    color: var(--gray-500);
  }
  .won-a .game-status {
    color: var(--blue-700);
  }
  .won-b .game-status {
    color: var(--red-600);
  }
  .invalid .game-status {
    color: var(--red-500);
  }
  .hint {
    margin: 12px 0 0;
    font-size: 12px;
    color: var(--color-text-muted);
  }
  @media (max-width: 640px) {
    .game {
      grid-template-columns: 44px 16px minmax(0, 1fr) 8px minmax(0, 1fr) 16px;
      gap: 4px;
    }
    .game-status {
      display: none;
    }
    .total-value .num {
      font-size: 44px;
    }
    .total-value {
      gap: 8px;
    }
  }
</style>
