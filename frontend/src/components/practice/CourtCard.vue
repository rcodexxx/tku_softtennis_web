<template>
  <article class="court hud-frame" :class="{ saved: court.saved }">
    <span class="corner tl"></span>
    <span class="corner br"></span>
    <header class="court-head">
      <span class="hud-label">Court {{ String(number).padStart(2, '0') }}</span>
      <span v-if="court.saved" class="saved-tag">已記錄 {{ court.a_games }}:{{ court.b_games }}</span>
    </header>

    <div class="teams">
      <div v-for="side in SIDES" :key="side.key" class="team" :class="{ won: winner === side.key }">
        <button
          v-for="pid in court[side.ids]"
          :key="pid"
          type="button"
          class="player"
          :class="{ front: court[side.front] === pid }"
          :disabled="court.saved"
          :title="court[side.front] === pid ? '前衛（再點一下取消）' : '點一下設為前衛'"
          @click="toggleFront(side, pid)"
        >
          <PlayerAvatar :id="pid" :name="players[pid]?.name" :src="players[pid]?.avatar_url" :size="28" />
          <span class="player-name">{{ players[pid]?.name ?? `#${pid}` }}</span>
          <span v-if="court[side.front] === pid" class="front-tag">前</span>
        </button>
      </div>
    </div>

    <div v-if="!court.saved" class="scores">
      <div v-for="side in SIDES" :key="side.key" class="score-row">
        <button
          v-for="result in quick[side.key]"
          :key="`${result.a}-${result.b}`"
          type="button"
          class="score num"
          :class="{ active: court.a_games === result.a && court.b_games === result.b }"
          @click="emit('update', { a_games: result.a, b_games: result.b })"
        >
          {{ result.a }}:{{ result.b }}
        </button>
      </div>
      <n-button type="primary" block :disabled="court.a_games == null" :loading="saving" @click="emit('save')">
        記錄
      </n-button>
    </div>
  </article>
</template>

<script setup>
  import { computed } from 'vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { quickResults } from '@/utils/matchRules'

  const SIDES = [
    { key: 'a', ids: 'side_a', front: 'a_front_id' },
    { key: 'b', ids: 'side_b', front: 'b_front_id' }
  ]

  /** 練習日的一面場地：點名字標記前衛、點比分後按記錄。 */
  const props = defineProps({
    court: { type: Object, required: true },
    number: { type: Number, required: true },
    players: { type: Object, required: true },
    format: { type: String, default: 'games_7' },
    saving: { type: Boolean, default: false }
  })
  const emit = defineEmits(['update', 'save'])

  const quick = computed(() => quickResults(props.format))
  const winner = computed(() => {
    const { a_games: a, b_games: b } = props.court
    if (a == null) return null
    return a > b ? 'a' : 'b'
  })

  const toggleFront = (side, pid) => emit('update', { [side.front]: props.court[side.front] === pid ? null : pid })
</script>

<style scoped>
  .court {
    --corner-color: var(--ink);
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 14px;
    border: 1px solid var(--line);
    background: var(--surface-2);
    transition: opacity var(--duration-base);
  }
  .court.saved {
    --corner-color: var(--line);
    opacity: 0.6;
  }
  .court-head {
    display: flex;
    justify-content: space-between;
  }
  .saved-tag {
    font-size: 14px;
    color: var(--win);
  }
  .teams {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .team {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-top: 8px;
    border-top: 2px solid var(--line);
  }
  .team.won {
    border-top-color: var(--accent);
  }
  .player {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px;
    border: 1px solid transparent;
    background: transparent;
    color: var(--ink);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  .player:hover:not(:disabled) {
    border-color: var(--line);
  }
  .player.front {
    border-color: var(--accent-soft);
    background: var(--accent-tint);
  }
  .player:disabled {
    cursor: default;
  }
  .player-name {
    flex: 1;
    min-width: 0;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .front-tag {
    padding: 0 5px;
    background: var(--accent);
    color: var(--on-accent);
    font-size: 12px;
    font-weight: 700;
  }
  .scores {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .score-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(48px, 1fr));
    gap: 4px;
  }
  .score {
    padding: 7px 0;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--ink);
    font-size: 16px;
    cursor: pointer;
  }
  .score.active {
    border-color: var(--ink);
    background: var(--ink);
    color: var(--bg);
  }
</style>
