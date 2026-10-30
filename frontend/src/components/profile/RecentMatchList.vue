<template>
  <n-empty v-if="!matches.length" description="還沒有比賽紀錄" class="empty" />
  <ol v-else class="match-list">
    <li
      v-for="(match, index) in matches"
      :key="match.id"
      class="match stagger-in"
      :class="match.perspective?.is_winner ? 'win' : 'loss'"
      :style="{ '--i': index }"
      @click="router.push({ name: 'ViewMatch', params: { id: match.id } })"
    >
      <span class="result">{{ match.perspective?.is_winner ? '勝' : '敗' }}</span>
      <div class="match-body">
        <div class="match-meta">
          <span>{{ formatDate(match.match_date) }}</span>
          <span class="type">{{ getMatchTypeDisplay(match.match_type) }}</span>
        </div>
        <div class="opponents">vs {{ match.perspective?.opponent_names.join(' / ') || '對手' }}</div>
      </div>
      <div class="match-score">
        <span class="num games">{{ match.perspective?.my_games }} : {{ match.perspective?.opponent_games }}</span>
        <span v-if="match.perspective?.performance != null" class="performance">
          本場表現 <b class="num">{{ formatRating(match.perspective.performance) }}</b>
          <ScoreChange :change="match.perspective.score_change" />
        </span>
      </div>
    </li>
  </ol>
</template>

<script setup>
  import { useRouter } from 'vue-router'
  import ScoreChange from '@/components/leaderboard/ScoreChange.vue'
  import { useOptions } from '@/composables/useOptions'
  import { formatDate } from '@/utils/format'
  import { formatRating } from '@/utils/rating'

  /** 從某位球員角度看的比賽列表（profile/me/matches 的資料）。 */
  defineProps({ matches: { type: Array, required: true } })

  const router = useRouter()
  const { getMatchTypeDisplay } = useOptions()
</script>

<style scoped>
  .empty {
    padding: 32px 0;
  }
  .match-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .match {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 14px;
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
    border-left-width: 4px;
    cursor: pointer;
    transition:
      transform var(--duration-fast),
      box-shadow var(--duration-fast);
  }
  .match:hover {
    transform: translateX(3px);
    box-shadow: var(--shadow-sm);
  }
  .match.win {
    border-left-color: var(--color-win);
  }
  .match.loss {
    border-left-color: var(--color-loss);
  }
  .result {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: var(--on-accent);
  }
  .win .result {
    background: var(--color-win);
  }
  .loss .result {
    background: var(--color-loss);
  }
  .match-body {
    flex: 1;
    min-width: 0;
  }
  .match-meta {
    display: flex;
    gap: 8px;
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .type {
    padding: 0 8px;
    border-radius: var(--radius-full);
    background: var(--blue-50);
    color: var(--blue-700);
    font-weight: 600;
  }
  .opponents {
    margin-top: 2px;
    font-weight: 700;
    color: var(--blue-900);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .match-score {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }
  .games {
    font-size: 24px;
    font-weight: 700;
    color: var(--gray-900);
  }
  .performance {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .performance b {
    font-size: 15px;
    color: var(--blue-900);
  }
</style>
