<template>
  <article class="match-card" @click="emit('view', record)">
    <header class="meta">
      <span class="date num">{{ dateLabel }}</span>
      <span class="chip">{{ getMatchTypeDisplay(record.match_type) }}</span>
      <span class="chip">{{ getMatchFormatDisplay(record.match_format) }}</span>
      <span v-if="record.has_detailed_scores" class="chip detail">每局比分</span>
      <span class="actions" @click.stop>
        <n-button v-if="canEdit" quaternary circle size="small" title="編輯" @click="emit('edit', record)">
          <template #icon><n-icon :component="Edit" /></template>
        </n-button>
        <n-button
          v-if="canDelete"
          quaternary
          circle
          size="small"
          type="error"
          title="刪除"
          @click="emit('delete', record)"
        >
          <template #icon><n-icon :component="TrashCan" /></template>
        </n-button>
      </span>
    </header>

    <div class="board">
      <div v-for="side in sides" :key="side.key" class="team" :class="[side.key, { won: side.won }]">
        <div class="avatars">
          <PlayerAvatar
            v-for="player in side.players"
            :id="player.id"
            :key="player.id"
            :name="player.name"
            :src="player.avatar_url"
            :size="36"
          />
        </div>
        <div class="names">
          <span
            v-for="player in side.players"
            :key="player.id"
            :class="{ highlight: highlightIds.includes(player.id) }"
          >
            {{ player.name }}
          </span>
        </div>
      </div>

      <div class="score num">
        <span :class="{ won: aWon }">
          {{ record.a_games }}<sup v-if="tiebreak && !aWon">{{ tiebreak.aScore }}</sup>
        </span>
        <span class="colon">:</span>
        <span :class="{ won: !aWon }">
          {{ record.b_games }}<sup v-if="tiebreak && aWon">{{ tiebreak.bScore }}</sup>
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
  import { computed } from 'vue'
  import { Edit, TrashCan } from '@vicons/carbon'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { useOptions } from '@/composables/useOptions'
  import { tiebreakScore } from '@/utils/matchRules'

  const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

  const props = defineProps({
    record: { type: Object, required: true },
    canEdit: { type: Boolean, default: false },
    canDelete: { type: Boolean, default: false },
    highlightIds: { type: Array, default: () => [] }
  })
  const emit = defineEmits(['view', 'edit', 'delete'])

  const { getMatchTypeDisplay, getMatchFormatDisplay } = useOptions()

  const aWon = computed(() => props.record.side_a_outcome === 'win')
  const tiebreak = computed(() => tiebreakScore(props.record))
  const dateLabel = computed(() => {
    const [year, month, day] = props.record.match_date.split('-').map(Number)
    return `${year}/${String(month).padStart(2, '0')}/${String(day).padStart(2, '0')}（${WEEKDAYS[new Date(year, month - 1, day).getDay()]}）`
  })
  const sides = computed(() => [
    { key: 'a', won: aWon.value, players: [props.record.player1, props.record.player2].filter(Boolean) },
    { key: 'b', won: !aWon.value, players: [props.record.player3, props.record.player4].filter(Boolean) }
  ])
</script>

<style scoped>
  .match-card {
    padding: 14px 18px 16px;
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    cursor: pointer;
    transition:
      transform var(--duration-base) var(--ease-spring),
      box-shadow var(--duration-base);
  }
  .match-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
  .meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .date {
    font-size: 15px;
    font-weight: 600;
    color: var(--gray-700);
  }
  .chip {
    padding: 1px 9px;
    border-radius: var(--radius-full);
    background: var(--blue-50);
    color: var(--blue-700);
    font-weight: 600;
  }
  .chip.detail {
    background: var(--gold-100);
    color: var(--accent-text);
  }
  .actions {
    margin-left: auto;
    display: flex;
    gap: 2px;
  }
  .board {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    align-items: center;
    gap: 16px;
  }
  .team {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
    opacity: 0.6;
  }
  .team.won {
    opacity: 1;
  }
  .team.b {
    order: 3;
    flex-direction: row-reverse;
    text-align: right;
  }
  .score {
    order: 2;
  }
  .avatars {
    display: flex;
    flex-shrink: 0;
  }
  .avatars > * + * {
    margin-left: -10px;
  }
  .names {
    display: flex;
    flex-direction: column;
    min-width: 0;
    font-weight: 700;
    color: var(--blue-900);
  }
  .names span {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .highlight {
    background: linear-gradient(transparent 60%, var(--gold-300) 60%);
  }
  .score {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 40px;
    font-weight: 700;
    line-height: 1;
    color: var(--gray-400);
  }
  .score .won {
    color: var(--blue-700);
  }
  .score sup {
    font-size: 15px;
    margin-left: 1px;
    color: var(--gray-400);
  }
  .colon {
    font-size: 28px;
  }

  @media (max-width: 640px) {
    .board {
      gap: 8px;
    }
    .avatars {
      display: none;
    }
    .score {
      font-size: 32px;
    }
  }
</style>
