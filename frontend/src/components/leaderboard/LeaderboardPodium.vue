<template>
  <section class="podium" aria-label="前三名">
    <article
      v-for="(entry, index) in ordered"
      :key="entry.player.id"
      class="place"
      :class="`place-${entry.place}`"
      :style="{ '--delay': `${index * 140 + (entry.place === 1 ? 260 : 0)}ms` }"
    >
      <div class="player">
        <span v-if="entry.place === 1" class="crown" aria-hidden="true">👑</span>
        <PlayerAvatar
          :id="entry.player.id"
          :name="entry.player.name"
          :src="entry.player.avatar_url"
          :size="entry.place === 1 ? 88 : 68"
          :ring="RINGS[entry.place]"
        />
        <h3 class="name">{{ entry.player.name }}</h3>
        <p v-if="entry.player.organization_name" class="org">{{ entry.player.organization_name }}</p>
        <div class="score">
          <CountUp :value="entry.player.rating" :decimals="1" :duration="1200" />
          <ScoreChange :change="entry.player.score_change" />
        </div>
        <div class="meta">
          <span class="num">{{ entry.player.wins }}勝 {{ entry.player.losses }}敗</span>
          <span class="dot-sep">·</span>
          <span class="num">勝率 {{ entry.player.win_rate }}%</span>
        </div>
        <RecentForm :form="entry.player.recent_form" />
      </div>
      <div class="block">
        <span class="block-rank num">{{ entry.place }}</span>
      </div>
    </article>
  </section>
</template>

<script setup>
  import { computed, onMounted } from 'vue'
  import CountUp from '@/components/base/CountUp.vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import RecentForm from './RecentForm.vue'
  import ScoreChange from './ScoreChange.vue'
  import { celebrate } from '@/utils/celebrate'

  const RINGS = { 1: 'gold', 2: 'silver', 3: 'bronze' }
  const CONFETTI_KEY = 'tku:podium-confetti'

  /** 前三名頒獎台；顯示順序為 2、1、3。 */
  const props = defineProps({ players: { type: Array, required: true } })

  const ordered = computed(() =>
    [1, 0, 2].filter(index => props.players[index]).map(index => ({ player: props.players[index], place: index + 1 }))
  )

  onMounted(() => {
    // 每個工作階段只灑一次彩帶
    try {
      if (sessionStorage.getItem(CONFETTI_KEY)) return
      sessionStorage.setItem(CONFETTI_KEY, '1')
    } catch {
      return
    }
    setTimeout(() => celebrate(), 700)
  })
</script>

<style scoped>
  .podium {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    align-items: end;
    gap: 16px;
    margin-bottom: 28px;
  }
  .place {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    animation: rise 900ms var(--ease-spring) both;
    animation-delay: var(--delay);
  }
  @keyframes rise {
    from {
      opacity: 0;
      transform: translateY(60px) scale(0.92);
    }
    to {
      opacity: 1;
      transform: none;
    }
  }
  .player {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 22px 14px 18px;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-bottom: none;
    box-shadow: var(--shadow-md);
    text-align: center;
  }
  .place-1 .player {
    padding-top: 30px;
    background: linear-gradient(180deg, var(--gold-100) 0%, #fff 70%);
  }
  .crown {
    position: absolute;
    top: -22px;
    font-size: 34px;
    animation: crown-bob 2.6s ease-in-out infinite;
    filter: drop-shadow(0 4px 6px rgba(242, 183, 5, 0.45));
  }
  @keyframes crown-bob {
    0%,
    100% {
      transform: translateY(0) rotate(-6deg);
    }
    50% {
      transform: translateY(-5px) rotate(6deg);
    }
  }
  .name {
    margin: 8px 0 0;
    font-size: 18px;
    font-weight: 800;
    color: var(--blue-900);
  }
  .place-1 .name {
    font-size: 21px;
  }
  .org {
    margin: 0;
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .score {
    display: flex;
    align-items: baseline;
    gap: 8px;
    font-size: 34px;
    font-weight: 700;
    color: var(--blue-700);
  }
  .place-1 .score {
    font-size: 44px;
  }
  .meta {
    display: flex;
    gap: 6px;
    font-size: 15px;
    color: var(--gray-700);
  }
  .dot-sep {
    color: var(--gray-300);
  }
  .block {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0 0 var(--radius-md) var(--radius-md);
    color: rgba(255, 255, 255, 0.95);
    box-shadow: var(--shadow-md);
  }
  .block-rank {
    font-size: 40px;
    font-weight: 700;
  }
  .place-1 .block {
    height: 96px;
    background: linear-gradient(180deg, var(--gold-300), var(--gold-500));
  }
  .place-2 .block {
    height: 68px;
    background: linear-gradient(180deg, #c3ccd9, var(--silver-500));
  }
  .place-3 .block {
    height: 52px;
    background: linear-gradient(180deg, #dda46d, var(--bronze-500));
  }

  @media (max-width: 640px) {
    .podium {
      gap: 8px;
    }
    .player {
      padding: 16px 6px 12px;
    }
    .name {
      font-size: 15px;
    }
    .place-1 .name {
      font-size: 16px;
    }
    .score {
      font-size: 26px;
      flex-direction: column;
      align-items: center;
      gap: 0;
    }
    .place-1 .score {
      font-size: 32px;
    }
    .meta {
      flex-direction: column;
      gap: 0;
      font-size: 13px;
    }
    .dot-sep,
    .recent-form {
      display: none;
    }
  }
</style>
