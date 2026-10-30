<template>
  <section class="ranking">
    <div class="ranking-head">
      <span class="col-rank">#</span>
      <span class="col-player">球員</span>
      <span class="col-form">近況</span>
      <span class="col-rate">勝率</span>
      <span class="col-matches">場次</span>
      <span class="col-score">分數</span>
    </div>

    <TransitionGroup name="row" tag="ol" class="rows">
      <li
        v-for="(player, index) in players"
        :key="player.id"
        class="row stagger-in"
        :class="{ me: player.id === highlightId }"
        :style="{ '--i': Math.min(index, 20) }"
        tabindex="0"
        @click="emit('select', player)"
        @keydown.enter="emit('select', player)"
      >
        <span class="col-rank">
          <span class="rank num" :class="rankClass(player.rank)">{{ formatRank(player.rank) }}</span>
        </span>
        <span class="col-player">
          <PlayerAvatar :id="player.id" :name="player.name" :src="player.avatar_url" :size="34" />
          <span class="player-text">
            <span class="player-name">{{ player.name }}</span>
            <span class="player-sub">{{ player.organization_name || (player.is_guest ? '訪客' : '隊員') }}</span>
          </span>
        </span>
        <span class="col-form"><RecentForm :form="player.recent_form" /></span>
        <span class="col-rate">
          <span class="rate-bar"><span class="rate-fill" :style="{ width: `${player.win_rate}%` }"></span></span>
          <span class="num rate-text">{{ Math.round(player.win_rate) }}%</span>
        </span>
        <span class="col-matches num">{{ player.total_matches }}</span>
        <span class="col-score">
          <template v-if="player.total_matches">
            <span class="score num">{{ formatRating(player.rating) }}</span>
            <span v-if="!isRated(player.total_matches)" class="provisional">評估中</span>
            <ScoreChange v-else :change="player.score_change" />
          </template>
          <span v-else class="score num muted">—</span>
        </span>
      </li>
    </TransitionGroup>
  </section>
</template>

<script setup>
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import RecentForm from './RecentForm.vue'
  import ScoreChange from './ScoreChange.vue'
  import { formatRating, isRated } from '@/utils/rating'

  /** players 需帶 rank（沒有名次時為 null，顯示「—」）。 */
  defineProps({
    players: { type: Array, required: true },
    highlightId: { type: Number, default: null }
  })
  const emit = defineEmits(['select'])

  const rankClass = rank => (!rank ? 'unranked' : rank <= 10 ? 'top10' : '')
  const formatRank = rank => (rank ? String(rank).padStart(2, '0') : '—')
</script>

<style scoped>
  .ranking {
    background: var(--surface);
    border: 1px solid var(--line-soft);
  }
  .ranking-head,
  .row {
    display: grid;
    grid-template-columns: 52px minmax(0, 2.4fr) 90px minmax(110px, 1.2fr) 56px 120px;
    align-items: center;
    gap: 12px;
    padding: 0 18px;
  }
  .ranking-head {
    height: 36px;
    border-bottom: 1px solid var(--line);
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: 0.1em;
    color: var(--ink-3);
  }
  .rows {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .row {
    position: relative;
    min-height: 58px;
    border-top: 1px solid var(--line-soft);
    cursor: pointer;
    outline: none;
    transition: background var(--duration-fast);
  }
  .rows > .row:first-child {
    border-top: 0;
  }
  /* 滑過：左邊出現重點色游標，像選單選取 */
  .row::before {
    content: '';
    position: absolute;
    left: 0;
    top: 10px;
    bottom: 10px;
    width: 3px;
    background: var(--accent);
    transform: scaleY(0);
    transition: transform var(--duration-fast) var(--ease-out);
  }
  .row:hover,
  .row:focus-visible {
    background: var(--surface-sunk);
  }
  .row:hover::before,
  .row:focus-visible::before {
    transform: scaleY(1);
  }
  .row.me {
    background: var(--accent-tint);
  }
  .row-move {
    transition: transform var(--duration-slow) var(--ease-out);
  }
  .rank {
    font-size: 17px;
    font-weight: 500;
    color: var(--ink-3);
  }
  .rank.top10 {
    color: var(--ink);
  }
  .rank.unranked {
    color: var(--ink-4);
  }
  .col-player {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }
  .player-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .player-name {
    font-weight: 600;
    letter-spacing: 0.03em;
    color: var(--ink);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .player-sub {
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: 0.06em;
    color: var(--ink-3);
  }
  .col-rate {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .rate-bar {
    flex: 1;
    height: 2px;
    background: var(--line);
  }
  .rate-fill {
    display: block;
    height: 100%;
    background: var(--ink);
    animation: grow 900ms var(--ease-out) both;
    animation-delay: 200ms;
    transform-origin: left;
  }
  @keyframes grow {
    from {
      transform: scaleX(0);
    }
  }
  .rate-text {
    width: 38px;
    text-align: right;
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--ink-2);
  }
  .col-matches {
    font-family: var(--font-mono);
    font-size: 14px;
    color: var(--ink-2);
    text-align: center;
  }
  .col-score {
    display: flex;
    align-items: baseline;
    justify-content: flex-end;
    gap: 8px;
  }
  .score {
    font-size: 22px;
    font-weight: 500;
    color: var(--ink);
  }
  .score.muted {
    color: var(--ink-4);
  }
  .provisional {
    padding: 1px 6px;
    border: 1px solid var(--accent-soft);
    color: var(--accent-text);
    font-family: var(--font-mono);
    font-size: 11px;
  }
  .ranking-head .col-score {
    text-align: right;
  }
  .ranking-head .col-matches {
    font-size: 11px;
    color: inherit;
  }

  @media (max-width: 900px) {
    .ranking-head,
    .row {
      grid-template-columns: 36px minmax(0, 1fr) 96px;
      padding: 0 12px;
    }
    .col-form,
    .col-rate,
    .col-matches {
      display: none !important;
    }
  }
</style>
