<template>
  <ol class="timeline">
    <li
      v-for="(game, index) in games"
      :key="game.game"
      class="game stagger-in"
      :class="{ tiebreak: isTiebreak(game.game) }"
      :style="{ '--i': index }"
    >
      <span class="label">{{ isTiebreak(game.game) ? '決勝' : `第 ${game.game} 局` }}</span>
      <span class="serve" :class="{ active: game.serve_side === 'side_a' }" title="A 方發球">🎾</span>
      <div class="bars">
        <div class="bar a" :class="{ won: game.winner === 'A' }" :style="{ '--w': width(game.a_score, game) }">
          <span class="num">{{ game.a_score }}</span>
        </div>
        <div class="bar b" :class="{ won: game.winner === 'B' }" :style="{ '--w': width(game.b_score, game) }">
          <span class="num">{{ game.b_score }}</span>
        </div>
      </div>
      <span class="serve" :class="{ active: game.serve_side === 'side_b' }" title="B 方發球">🎾</span>
    </li>
  </ol>
</template>

<script setup>
  import { isTiebreakGame } from '@/utils/matchRules'

  /** 每局比分：左邊 A 方、右邊 B 方，長條長度依該局得分比例。 */
  const props = defineProps({
    games: { type: Array, required: true },
    matchFormat: { type: String, default: '' }
  })

  const isTiebreak = gameNumber => isTiebreakGame(props.matchFormat, gameNumber)
  const width = (score, game) => `${Math.max(12, (score / Math.max(game.a_score, game.b_score, 1)) * 100)}%`
</script>

<style scoped>
  .timeline {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .game {
    display: grid;
    grid-template-columns: 64px 22px minmax(0, 1fr) 22px;
    align-items: center;
    gap: 8px;
  }
  .label {
    font-size: 13px;
    font-weight: 700;
    color: var(--gray-500);
  }
  .tiebreak .label {
    color: var(--red-500);
  }
  .serve {
    font-size: 15px;
    opacity: 0.12;
    filter: grayscale(1);
    text-align: center;
  }
  .serve.active {
    opacity: 1;
    filter: none;
  }
  .bars {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px;
  }
  .bar {
    display: flex;
    align-items: center;
    height: 30px;
  }
  .bar.a {
    justify-content: flex-end;
  }
  .bar span {
    height: 100%;
    width: var(--w);
    display: flex;
    align-items: center;
    padding: 0 10px;
    font-size: 18px;
    font-weight: 700;
    color: var(--gray-500);
    background: var(--gray-100);
    transform-origin: var(--origin);
    animation: grow 700ms var(--ease-out) both;
  }
  .bar.a span {
    --origin: right;
    justify-content: flex-start;
    border-radius: var(--radius-sm) 0 0 var(--radius-sm);
  }
  .bar.b span {
    --origin: left;
    justify-content: flex-end;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  }
  .bar.won span {
    color: #fff;
  }
  .bar.a.won span {
    background: linear-gradient(90deg, var(--blue-400), var(--blue-700));
  }
  .bar.b.won span {
    background: linear-gradient(90deg, var(--red-600), var(--red-500));
  }
  @keyframes grow {
    from {
      transform: scaleX(0);
    }
  }
</style>
