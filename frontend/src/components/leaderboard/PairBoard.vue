<template>
  <div class="pair-board">
    <div class="toolbar">
      <div class="segments" role="radiogroup" aria-label="排序">
        <button
          v-for="option in SORTS"
          :key="option.value"
          type="button"
          class="segment"
          :class="{ active: sortBy === option.value }"
          @click="sortBy = option.value"
        >
          {{ option.label }}
        </button>
      </div>
      <div class="segments" role="radiogroup" aria-label="最少場數">
        <button
          v-for="value in MIN_OPTIONS"
          :key="value"
          type="button"
          class="segment num"
          :class="{ active: minMatches === value }"
          @click="minMatches = value"
        >
          ≥{{ value }} 場
        </button>
      </div>
    </div>

    <n-skeleton v-if="loading" height="160px" />
    <n-empty v-else-if="!pairs.length" description="還沒有符合的組合" class="empty" />
    <template v-else>
      <!-- 第一名：最佳組合 -->
      <article class="best hud-frame lock-in">
        <span class="corner tl"></span>
        <span class="corner br"></span>
        <span class="hud-label crown">{{ sortBy === 'chemistry' ? '▲▲▲ 默契最佳' : '▲▲▲ 最佳組合' }}</span>
        <div class="best-body">
          <div class="duo">
            <span v-for="player in best.players" :key="player.id" class="duo-player" @click="openPlayer(player)">
              <PlayerAvatar :id="player.id" :name="player.name" :src="player.avatar_url" :size="56" ring="gold" />
              <span class="duo-name">{{ player.name }}</span>
              <span v-if="formation(best)?.front.id === player.id" class="position">前衛</span>
              <span v-else-if="formation(best)" class="position back">後衛</span>
            </span>
          </div>
          <div class="best-stats">
            <span class="stat">
              <span class="hud-label">默契</span>
              <span class="num stat-value" :class="tone(best.chemistry)">{{ formatChemistry(best.chemistry) }}</span>
            </span>
            <span class="stat">
              <span class="hud-label">組合分</span>
              <span class="num stat-value">{{ best.rating.toFixed(1) }}</span>
            </span>
            <span class="stat">
              <span class="hud-label">戰績</span>
              <span class="num stat-value small">{{ best.wins }}W {{ best.losses }}L</span>
            </span>
          </div>
        </div>
      </article>

      <ol class="rows">
        <li
          v-for="(pair, index) in pairs.slice(1)"
          :key="keyOf(pair)"
          class="row stagger-in"
          :style="{ '--i': Math.min(index, 20) }"
        >
          <span class="num rank">{{ String(index + 2).padStart(2, '0') }}</span>
          <span class="avatars">
            <PlayerAvatar
              v-for="player in pair.players"
              :id="player.id"
              :key="player.id"
              :name="player.name"
              :src="player.avatar_url"
              :size="30"
            />
          </span>
          <span class="names">
            <span v-for="player in pair.players" :key="player.id" class="name" @click="openPlayer(player)">
              {{ player.name
              }}<small v-if="formation(pair)">{{ formation(pair).front.id === player.id ? '前' : '後' }}</small>
            </span>
          </span>
          <span class="num record">{{ pair.wins }}W {{ pair.losses }}L</span>
          <span class="num rating">{{ pair.rating.toFixed(1) }}</span>
          <span class="num chemistry" :class="tone(pair.chemistry)">{{ formatChemistry(pair.chemistry) }}</span>
        </li>
      </ol>
    </template>
  </div>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { leaderboardApi } from '@/api'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { formatChemistry, usualFormation } from '@/utils/pairs'

  const SORTS = [
    { value: 'rating', label: '組合分' },
    { value: 'chemistry', label: '默契' }
  ]
  const MIN_OPTIONS = [3, 5, 10]

  /** 組合榜：雙打搭檔的組合分（同隊時的平均表現）與默契值。 */
  const props = defineProps({ seasonId: { type: Number, default: null } })

  const router = useRouter()
  const loading = ref(true)
  const pairs = ref([])
  const sortBy = ref('rating')
  const minMatches = ref(3)
  const best = computed(() => pairs.value[0])

  const keyOf = pair => pair.players.map(player => player.id).join('-')
  const formation = pair => usualFormation(pair)
  const tone = value => (value >= 0.15 ? 'up' : value <= -0.15 ? 'down' : '')
  const openPlayer = player => router.push({ name: 'Player', params: { id: player.id } })

  const load = async () => {
    loading.value = true
    try {
      const { items } = await leaderboardApi.pairs({
        season_id: props.seasonId || undefined,
        min_matches: minMatches.value,
        sort_by: sortBy.value
      })
      pairs.value = items
    } finally {
      loading.value = false
    }
  }

  watch([sortBy, minMatches, () => props.seasonId], load, { immediate: true })
</script>

<style scoped>
  .toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 16px;
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
  .best {
    --corner-color: var(--accent);
    --corner-width: 3px;
    margin-bottom: 14px;
    padding: 18px 20px;
    border: 1px solid var(--ink);
    background: var(--surface-2);
  }
  .crown {
    color: var(--accent-text);
  }
  .best-body {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 14px;
  }
  .duo {
    display: flex;
    gap: 24px;
  }
  .duo-player {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    cursor: pointer;
  }
  .duo-name {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--ink);
  }
  .position {
    padding: 0 6px;
    background: var(--accent);
    color: var(--on-accent);
    font-size: 13px;
    font-weight: 700;
  }
  .position.back {
    background: var(--ink);
    color: var(--bg);
  }
  .best-stats {
    display: flex;
    gap: 24px;
  }
  .stat {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .stat-value {
    font-size: 40px;
    line-height: 1;
    color: var(--ink);
  }
  .stat-value.small {
    font-size: 22px;
    line-height: 40px;
  }
  .rows {
    margin: 0;
    padding: 0;
    list-style: none;
    border: 1px solid var(--line-soft);
  }
  .row {
    display: grid;
    grid-template-columns: 30px 66px minmax(0, 1fr) 76px 48px 56px;
    align-items: center;
    gap: 10px;
    padding: 9px 14px;
    border-top: 1px solid var(--line-soft);
    background: var(--surface);
  }
  .row:first-child {
    border-top: 0;
  }
  .rank {
    color: var(--ink-3);
  }
  .avatars {
    display: flex;
    gap: 4px;
  }
  .names {
    display: flex;
    flex-wrap: wrap;
    gap: 2px 10px;
    min-width: 0;
  }
  .name {
    font-weight: 600;
    color: var(--ink);
    cursor: pointer;
  }
  .name small {
    margin-left: 3px;
    font-size: 12px;
    color: var(--accent-text);
  }
  .record {
    color: var(--ink-2);
    font-size: 14px;
  }
  .rating {
    font-size: 18px;
    color: var(--ink);
    text-align: right;
  }
  .chemistry {
    font-size: 16px;
    text-align: right;
    color: var(--ink-3);
  }
  .up {
    color: var(--win);
  }
  .down {
    color: var(--loss);
  }
  .empty {
    padding: 48px 0;
  }
  .lock-in {
    animation: lock 520ms var(--ease-out) backwards;
  }
  @keyframes lock {
    from {
      opacity: 0;
      transform: scale(0.985);
    }
  }
  @media (max-width: 640px) {
    .row {
      grid-template-columns: 26px 62px minmax(0, 1fr) 48px;
    }
    .record,
    .rating {
      display: none;
    }
    .stat-value {
      font-size: 32px;
    }
  }
</style>
