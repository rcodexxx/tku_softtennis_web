<template>
  <section class="top-three" aria-label="前三名">
    <!-- 第一名：王座面板 -->
    <article
      v-if="champion"
      class="champion hud-frame lock-in"
      :class="{ me: champion.id === highlightId }"
      style="--delay: 260ms"
      tabindex="0"
      @click="emit('select', champion)"
      @keydown.enter="emit('select', champion)"
    >
      <span class="corner tl"></span>
      <span class="corner br"></span>
      <span class="ghost-rank num" aria-hidden="true">01</span>

      <div class="champion-head">
        <span class="hud-label crown">▲▲▲ 王座 / Champion</span>
      </div>

      <div class="champion-body">
        <span class="reticle">
          <svg class="reticle-ring" viewBox="0 0 100 100" aria-hidden="true">
            <circle cx="50" cy="50" r="46" />
            <path d="M50 0v8M50 92v8M0 50h8M92 50h8" class="ticks" />
          </svg>
          <PlayerAvatar :id="champion.id" :name="champion.name" :src="champion.avatar_url" :size="72" ring="gold" />
        </span>
        <div class="identity">
          <span class="name">{{ champion.name }}</span>
          <span class="hud-label">{{ champion.organization_name || '—' }}</span>
          <span class="readout num">
            {{ champion.wins }}W {{ champion.losses }}L · {{ Math.round(champion.win_rate) }}%
            <template v-if="streak(champion) >= 2"> · 連勝 {{ streak(champion) }}</template>
          </span>
          <RecentForm :form="champion.recent_form" />
        </div>
      </div>

      <div class="champion-score">
        <CountUp class="score num" :value="champion.rating" :decimals="1" :duration="1200" />
        <span class="score-meta num">
          / 10
          <template v-if="lead !== null"> · 領先 {{ lead.toFixed(1) }}</template>
        </span>
      </div>

      <div class="ruler" aria-hidden="true">
        <span class="ruler-fill" :style="{ width: `${ratingPercent(champion.rating)}%` }"></span>
        <span class="ruler-marker" :style="{ left: `${ratingPercent(champion.rating)}%` }"></span>
      </div>
      <div class="ruler-ticks num" aria-hidden="true">
        <span v-for="tick in TICKS" :key="tick">{{ tick }}</span>
      </div>
    </article>

    <!-- 第二、三名 -->
    <div class="runners">
      <template v-for="(player, index) in runners" :key="index">
        <article
          v-if="player"
          class="runner hud-frame lock-in"
          :class="{ me: player.id === highlightId }"
          :style="{ '--delay': `${index === 0 ? 120 : 0}ms` }"
          tabindex="0"
          @click="emit('select', player)"
          @keydown.enter="emit('select', player)"
        >
          <span class="corner tl"></span>
          <span class="ghost-rank num" aria-hidden="true">0{{ index + 2 }}</span>
          <span class="hud-label">{{ index === 0 ? '▲▲' : '▲' }} RK-0{{ index + 2 }}</span>
          <div class="runner-body">
            <PlayerAvatar
              :id="player.id"
              :name="player.name"
              :src="player.avatar_url"
              :size="46"
              :ring="index === 0 ? 'silver' : 'bronze'"
            />
            <div class="identity">
              <span class="runner-name">{{ player.name }}</span>
              <span class="readout num">{{ player.wins }}W {{ player.losses }}L</span>
            </div>
          </div>
          <CountUp class="runner-score num" :value="player.rating" :decimals="1" />
        </article>
        <div v-else class="runner vacant">
          <span class="hud-label">RK-0{{ index + 2 }}</span>
          <span class="vacant-text">待定</span>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
  import { computed } from 'vue'
  import CountUp from '@/components/base/CountUp.vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { ratingPercent } from '@/utils/rating'
  import RecentForm from './RecentForm.vue'

  const TICKS = [1, 4, 7, 10]

  /** players：已排名的前三名（可能少於三人）。 */
  const props = defineProps({
    players: { type: Array, required: true },
    highlightId: { type: Number, default: null }
  })
  const emit = defineEmits(['select'])

  const champion = computed(() => props.players[0] ?? null)
  const runners = computed(() => [props.players[1] ?? null, props.players[2] ?? null])
  // 第一名領先第二名幾分
  const lead = computed(() => (props.players[1] ? champion.value.rating - props.players[1].rating : null))

  /** 最近連勝幾場（recent_form 最新的在前）。 */
  const streak = player => {
    const form = player.recent_form ?? []
    const losing = form.indexOf('L')
    return losing === -1 ? form.length : losing
  }
</script>

<style scoped>
  .top-three {
    display: grid;
    grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr);
    gap: 14px;
  }
  article {
    cursor: pointer;
    outline: none;
  }
  .ghost-rank {
    position: absolute;
    right: 10px;
    top: -6px;
    font-size: 150px;
    font-weight: 500;
    line-height: 1;
    color: transparent;
    -webkit-text-stroke: 1px var(--line);
    pointer-events: none;
    user-select: none;
  }

  /* 第一名 */
  .champion {
    --corner-color: var(--accent);
    --corner-width: 3px;
    overflow: hidden;
    padding: 18px 20px 16px;
    border: 1px solid var(--ink);
    background: var(--surface-2);
  }
  .champion .corner {
    width: 18px;
    height: 18px;
  }
  .champion-head {
    position: relative;
    display: flex;
    justify-content: space-between;
  }
  .crown {
    color: var(--accent-text);
  }
  .champion-body {
    position: relative;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-top: 18px;
  }
  .reticle {
    position: relative;
    display: grid;
    place-items: center;
    width: 124px;
    height: 124px;
    flex-shrink: 0;
  }
  .reticle-ring {
    position: absolute;
    inset: 0;
    fill: none;
    stroke: var(--accent);
    stroke-width: 1.5;
    stroke-dasharray: 2 5;
    animation: spin 16s linear infinite;
  }
  .reticle-ring .ticks {
    stroke-dasharray: none;
    stroke-width: 2;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  .identity {
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 0;
  }
  .name {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--ink);
  }
  .readout {
    font-size: 12px;
    color: var(--ink-2);
  }
  .champion-score {
    position: relative;
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-top: 16px;
  }
  .score {
    font-size: 64px;
    font-weight: 500;
    line-height: 1;
    color: var(--ink);
  }
  .score-meta {
    font-size: 13px;
    color: var(--ink-3);
  }
  .ruler {
    position: relative;
    height: 2px;
    margin-top: 14px;
    background: var(--line);
  }
  .ruler-fill {
    position: absolute;
    inset: 0 auto 0 0;
    background: var(--accent);
    transform-origin: left;
    animation: grow 1.1s var(--ease-out) both 0.5s;
  }
  .ruler-marker {
    position: absolute;
    top: -7px;
    width: 0;
    height: 0;
    border: 5px solid transparent;
    border-top: 6px solid var(--accent);
    transform: translateX(-50%);
  }
  .ruler-ticks {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    font-size: 11px;
    color: var(--ink-4);
  }
  @keyframes grow {
    from {
      transform: scaleX(0);
    }
  }

  /* 第二、三名 */
  .runners {
    display: grid;
    grid-template-rows: 1fr 1fr;
    gap: 14px;
  }
  .runner {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 14px 16px;
    border: 1px solid var(--line);
    background: var(--surface);
  }
  .runner .ghost-rank {
    font-size: 84px;
    top: -4px;
  }
  .runner-body {
    position: relative;
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .runner-name {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--ink);
  }
  .runner-score {
    position: relative;
    font-size: 32px;
    font-weight: 500;
    line-height: 1;
    color: var(--ink);
  }
  .vacant {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 6px;
    padding: 14px 16px;
    border: 1px dashed var(--line);
    color: var(--ink-4);
  }
  .vacant-text {
    font-size: 15px;
    letter-spacing: 0.2em;
  }

  /* 滑過：括號往外張開，像在瞄準 */
  .champion:hover .corner.tl,
  .runner:hover .corner.tl,
  .champion:focus-visible .corner.tl,
  .runner:focus-visible .corner.tl {
    transform: translate(-4px, -4px);
  }
  .champion:hover .corner.br,
  .champion:focus-visible .corner.br {
    transform: translate(4px, 4px);
  }
  .runner:hover,
  .runner:focus-visible {
    border-color: var(--ink);
  }
  .me .name,
  .me .runner-name {
    color: var(--accent-text);
  }

  /* 進場：依序「鎖定」——框先淡入，四角從外面收進來 */
  .lock-in {
    animation: lock-panel 520ms var(--ease-out) backwards;
    animation-delay: var(--delay, 0ms);
  }
  .lock-in > .corner {
    animation: lock-corner 520ms var(--ease-out) backwards;
    animation-delay: calc(var(--delay, 0ms) + 120ms);
  }
  .lock-in > .corner.tl {
    --from: translate(-14px, -14px);
  }
  .lock-in > .corner.br {
    --from: translate(14px, 14px);
  }
  @keyframes lock-panel {
    from {
      opacity: 0;
      transform: scale(0.985);
    }
  }
  @keyframes lock-corner {
    from {
      opacity: 0;
      transform: var(--from);
    }
  }

  @media (max-width: 760px) {
    .top-three {
      grid-template-columns: minmax(0, 1fr);
    }
    .runners {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      grid-template-rows: none;
    }
    .champion {
      padding: 16px;
    }
    .champion-body {
      gap: 14px;
    }
    .reticle {
      width: 104px;
      height: 104px;
    }
    .name {
      font-size: 22px;
    }
    .score {
      font-size: 52px;
    }
    .ghost-rank {
      font-size: 120px;
    }
    .runner .ghost-rank {
      font-size: 64px;
    }
    .runner-body {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }
  }
</style>
