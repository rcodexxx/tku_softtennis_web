<template>
  <n-modal
    :show="Boolean(player)"
    preset="card"
    style="width: min(560px, 94vw)"
    :title="player?.name"
    @update:show="close"
  >
    <template v-if="player">
      <div class="head">
        <PlayerAvatar :id="player.id" :name="player.name" :src="player.avatar_url" :size="72" :ring="ring" />
        <div class="head-text">
          <div class="rank num">#{{ player.rank }}</div>
          <div class="sub">{{ player.organization_name || '—' }} · {{ player.is_guest ? '訪客' : '隊員' }}</div>
          <RecentForm :form="player.recent_form" />
        </div>
        <div class="head-score">
          <span class="num score">{{ formatRating(player.rating) }}</span>
          <ScoreChange :change="player.score_change" />
        </div>
      </div>

      <div class="record">
        <div>
          <span class="num big win">{{ player.wins }}</span
          >勝
        </div>
        <div>
          <span class="num big loss">{{ player.losses }}</span
          >敗
        </div>
        <div>
          <span class="num big">{{ player.win_rate }}%</span>勝率
        </div>
        <div>
          <span class="num big">{{ formatDate(player.last_match_date) || '—' }}</span
          >最近比賽
        </div>
      </div>

      <RatingMeter :rating="player.rating" :total-matches="player.total_matches" />

      <div v-if="canCompare" class="compare">
        <n-button v-if="!comparison" secondary block :loading="comparing" @click="compare">與我比較</n-button>
        <div v-else class="compare-result">
          <p class="compare-title">如果你們搭配實力相同的搭檔對打，預期拿下的局數</p>
          <div class="probability">
            <span class="side me"
              >我 <b class="num">{{ myWinRate }}%</b></span
            >
            <div class="bar">
              <span class="bar-me" :style="{ width: `${myWinRate}%` }"></span>
            </div>
            <span class="side them"
              ><b class="num">{{ 100 - myWinRate }}%</b> {{ player.name }}</span
            >
          </div>
          <p class="compare-note">依雙方目前分數預測：差 1 分，強的一方預期拿下 7 成局數。</p>
        </div>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'
  import { useMessage } from 'naive-ui'
  import { leaderboardApi } from '@/api'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import RatingMeter from '@/components/profile/RatingMeter.vue'
  import { formatDate } from '@/utils/format'
  import { formatRating } from '@/utils/rating'
  import RecentForm from './RecentForm.vue'
  import ScoreChange from './ScoreChange.vue'

  const props = defineProps({
    player: { type: Object, default: null },
    myMemberId: { type: Number, default: null }
  })
  const emit = defineEmits(['close'])

  const message = useMessage()
  const comparing = ref(false)
  const comparison = ref(null)

  const ring = computed(() => ({ 1: 'gold', 2: 'silver', 3: 'bronze' })[props.player?.rank] || 'none')
  const canCompare = computed(() => props.myMemberId && props.player && props.myMemberId !== props.player.id)
  const myWinRate = computed(() => Math.round((1 - comparison.value.expected_games_share) * 100))

  watch(
    () => props.player,
    () => (comparison.value = null)
  )

  const close = () => emit('close')

  const compare = async () => {
    comparing.value = true
    try {
      // member1 是對方，所以 expected_games_share 是對方預期拿下的局數比例
      comparison.value = (await leaderboardApi.compare(props.player.id, props.myMemberId)).comparison
    } catch (error) {
      message.error(error.response?.data?.message || '比較失敗')
    } finally {
      comparing.value = false
    }
  }
</script>

<style scoped>
  .head {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
  }
  .head-text {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .rank {
    font-size: 22px;
    font-weight: 700;
    color: var(--blue-700);
  }
  .sub {
    font-size: 15px;
    color: var(--color-text-muted);
  }
  .head-score {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }
  .score {
    font-size: 44px;
    font-weight: 700;
    line-height: 1;
    color: var(--blue-900);
  }
  .record {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 22px;
    padding: 14px;
    border-radius: var(--radius-md);
    background: var(--blue-50);
    text-align: center;
    font-size: 14px;
    color: var(--color-text-muted);
  }
  .big {
    display: block;
    font-size: 24px;
    font-weight: 700;
    color: var(--gray-900);
  }
  .big.win {
    color: var(--color-win);
  }
  .big.loss {
    color: var(--color-loss);
  }
  .compare {
    margin-top: 22px;
  }
  .compare-result {
    padding: 16px;
    border-radius: var(--radius-md);
    background: linear-gradient(135deg, var(--blue-50), var(--gold-100));
    animation: stagger-in var(--duration-slow) var(--ease-out) both;
  }
  .compare-title {
    margin: 0 0 10px;
    font-weight: 800;
    color: var(--blue-900);
  }
  .probability {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .side {
    white-space: nowrap;
    font-size: 15px;
  }
  .side b {
    font-size: 22px;
  }
  .me b {
    color: var(--blue-700);
  }
  .them b {
    color: var(--red-500);
  }
  .bar {
    flex: 1;
    height: 12px;
    border-radius: var(--radius-full);
    background: var(--red-500);
    overflow: hidden;
  }
  .bar-me {
    display: block;
    height: 100%;
    background: var(--blue-600);
    transform-origin: left;
    animation: grow 900ms var(--ease-out) both;
  }
  @keyframes grow {
    from {
      transform: scaleX(0);
    }
  }
  .compare-note {
    margin: 8px 0 0;
    font-size: 14px;
    color: var(--color-text-muted);
  }
</style>
