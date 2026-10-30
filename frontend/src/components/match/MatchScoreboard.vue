<template>
  <section class="scoreboard">
    <div class="meta">
      <span v-for="item in metaItems" :key="item" class="chip">{{ item }}</span>
    </div>
    <div class="board">
      <div v-for="team in teams" :key="team.key" class="team" :class="[team.key, { won: team.won, decided }]">
        <span v-if="decided && team.won" class="trophy" aria-label="勝方">🏆</span>
        <div class="avatars">
          <PlayerAvatar
            v-for="player in team.players"
            :id="player.id"
            :key="player.id"
            :name="player.name"
            :src="player.avatar_url"
            :size="64"
          />
          <span v-if="!team.players.length" class="empty-avatar">?</span>
        </div>
        <div class="names">
          <span v-for="player in team.players" :key="player.id">{{ player.name }}</span>
          <span v-if="!team.players.length" class="placeholder">尚未選擇球員</span>
        </div>
      </div>

      <div class="score num">
        <span :class="{ won: decided && aWon }">
          <CountUp :value="aGames" :duration="700" /><sup v-if="tiebreak && !aWon">{{ tiebreak.aScore }}</sup>
        </span>
        <span class="colon">:</span>
        <span :class="{ won: decided && !aWon }">
          <CountUp :value="bGames" :duration="700" /><sup v-if="tiebreak && aWon">{{ tiebreak.bScore }}</sup>
        </span>
      </div>
    </div>
  </section>
</template>

<script setup>
  import { computed } from 'vue'
  import CountUp from '@/components/base/CountUp.vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { useOptions } from '@/composables/useOptions'
  import { tiebreakScore } from '@/utils/matchRules'

  /**
   * 比賽計分板。teamA / teamB 為球員物件陣列（需要 id、name、avatar_url）；
   * games 為後端格式的每局比分，用來顯示決勝局分數。
   */
  const props = defineProps({
    teamA: { type: Array, default: () => [] },
    teamB: { type: Array, default: () => [] },
    aGames: { type: Number, default: 0 },
    bGames: { type: Number, default: 0 },
    matchDate: { type: String, default: '' },
    matchType: { type: String, default: '' },
    matchFormat: { type: String, default: '' },
    games: { type: Array, default: () => [] }
  })

  const { getMatchTypeDisplay, getMatchFormatDisplay } = useOptions()

  const aWon = computed(() => props.aGames > props.bGames)
  const decided = computed(() => props.aGames !== props.bGames)
  const tiebreak = computed(() =>
    tiebreakScore({ match_format: props.matchFormat, a_games: props.aGames, b_games: props.bGames, games: props.games })
  )
  const metaItems = computed(() =>
    [
      props.matchDate,
      props.matchType && getMatchTypeDisplay(props.matchType),
      props.matchFormat && getMatchFormatDisplay(props.matchFormat)
    ].filter(Boolean)
  )
  const teams = computed(() => [
    { key: 'a', players: props.teamA, won: aWon.value },
    { key: 'b', players: props.teamB, won: !aWon.value }
  ])
</script>

<style scoped>
  .scoreboard {
    position: relative;
    overflow: hidden;
    padding: 22px 28px 30px;
    border-radius: var(--radius-xl);
    background: var(--ink);
    color: var(--bg);
    box-shadow: var(--shadow-lg);
  }
  .meta {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 18px;
  }
  .chip {
    padding: 2px 12px;
    border-radius: var(--radius-full);
    background: color-mix(in srgb, var(--bg) 14%, transparent);
    font-size: 15px;
    font-weight: 600;
  }
  .board {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    align-items: center;
    gap: 20px;
  }
  .team {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    text-align: center;
    transition: opacity var(--duration-base);
  }
  .team.decided:not(.won) {
    opacity: 0.55;
  }
  .team.b {
    order: 3;
  }
  .score {
    order: 2;
  }
  .trophy {
    position: absolute;
    top: -16px;
    right: calc(50% - 64px);
    font-size: 26px;
    animation: pop 600ms var(--ease-spring) both;
  }
  @keyframes pop {
    from {
      transform: scale(0) rotate(-30deg);
    }
  }
  .avatars {
    display: flex;
  }
  .avatars > * + * {
    margin-left: -14px;
  }
  .empty-avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 2px dashed color-mix(in srgb, var(--bg) 40%, transparent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: color-mix(in srgb, var(--bg) 60%, transparent);
  }
  .names {
    display: flex;
    flex-direction: column;
    font-size: 18px;
    font-weight: 800;
  }
  .placeholder {
    font-weight: 500;
    color: var(--blue-200);
  }
  .score {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 76px;
    font-weight: 700;
    line-height: 1;
    color: color-mix(in srgb, var(--bg) 55%, transparent);
  }
  .score .won {
    color: var(--gold-300);
    text-shadow: 0 0 24px rgba(242, 183, 5, 0.45);
  }
  .score sup {
    font-size: 24px;
    margin-left: 2px;
  }
  .colon {
    font-size: 48px;
  }

  @media (max-width: 640px) {
    .scoreboard {
      padding: 18px 12px 22px;
    }
    .board {
      gap: 8px;
    }
    .names {
      font-size: 16px;
    }
    .score {
      font-size: 48px;
    }
    .colon {
      font-size: 32px;
    }
    .avatars :deep(.player-avatar) {
      width: 44px !important;
      height: 44px !important;
    }
  }
</style>
