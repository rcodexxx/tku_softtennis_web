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
      >
        <span class="col-rank">
          <span class="rank-badge num" :class="rankClass(startRank + index)">{{ startRank + index }}</span>
        </span>
        <span class="col-player">
          <PlayerAvatar :id="player.id" :name="player.name" :src="player.avatar_url" :size="40" />
          <span class="player-text">
            <span class="player-name">{{ player.name }}</span>
            <span class="player-sub">{{ player.organization_name || player.experience_level }}</span>
          </span>
        </span>
        <span class="col-form"><RecentForm :form="player.recent_form" /></span>
        <span class="col-rate">
          <span class="rate-bar"><span class="rate-fill" :style="{ width: `${player.win_rate}%` }"></span></span>
          <span class="num rate-text">{{ Math.round(player.win_rate) }}%</span>
        </span>
        <span class="col-matches num">{{ player.total_matches }}</span>
        <span class="col-score">
          <span class="score num">{{ displayScore(player) }}</span>
          <ScoreChange :change="player.score_change" />
        </span>
      </li>
    </TransitionGroup>
  </section>
</template>

<script setup>
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import RecentForm from './RecentForm.vue'
  import ScoreChange from './ScoreChange.vue'

  defineProps({
    players: { type: Array, required: true },
    startRank: { type: Number, default: 1 },
    highlightId: { type: Number, default: null }
  })

  const displayScore = player => Math.round(player.conservative_score * 100)
  const rankClass = rank => (rank <= 10 ? 'top10' : rank <= 20 ? 'top20' : '')
</script>

<style scoped>
  .ranking {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
  }
  .ranking-head,
  .row {
    display: grid;
    grid-template-columns: 56px minmax(0, 2.4fr) 150px minmax(110px, 1.2fr) 64px 130px;
    align-items: center;
    gap: 12px;
    padding: 0 20px;
  }
  .ranking-head {
    height: 44px;
    background: var(--blue-50);
    color: var(--gray-500);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.06em;
  }
  .rows {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .row {
    min-height: 68px;
    border-top: 1px solid var(--gray-100);
    transition: background var(--duration-fast);
  }
  .row:hover {
    background: var(--blue-50);
  }
  .row.me {
    background: var(--gold-100);
  }
  .row-move {
    transition: transform var(--duration-slow) var(--ease-out);
  }
  .rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 34px;
    height: 34px;
    border-radius: var(--radius-sm);
    font-size: 19px;
    font-weight: 700;
    color: var(--gray-500);
    background: var(--gray-100);
  }
  .rank-badge.top10 {
    color: var(--blue-700);
    background: var(--blue-100);
  }
  .rank-badge.top20 {
    color: var(--blue-500);
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
    font-weight: 700;
    color: var(--blue-900);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .player-sub {
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .col-rate {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .rate-bar {
    flex: 1;
    height: 8px;
    border-radius: var(--radius-full);
    background: var(--gray-100);
    overflow: hidden;
  }
  .rate-fill {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, var(--blue-400), var(--blue-600));
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
    font-size: 16px;
    font-weight: 600;
    color: var(--gray-700);
  }
  .col-matches {
    font-size: 18px;
    color: var(--gray-700);
    text-align: center;
  }
  .col-score {
    display: flex;
    align-items: baseline;
    justify-content: flex-end;
    gap: 8px;
  }
  .score {
    font-size: 26px;
    font-weight: 700;
    color: var(--blue-700);
  }
  .ranking-head .col-score {
    text-align: right;
  }
  .ranking-head .col-matches {
    font-size: 12px;
    color: inherit;
  }

  @media (max-width: 900px) {
    .ranking-head,
    .row {
      grid-template-columns: 44px minmax(0, 1fr) 96px;
      padding: 0 12px;
    }
    .col-form,
    .col-rate,
    .col-matches {
      display: none !important;
    }
  }
</style>
