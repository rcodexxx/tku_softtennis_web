<template>
  <div class="player-profile">
    <n-skeleton v-if="!data && loading" height="180px" />
    <n-result v-else-if="error" status="error" title="無法載入球員資料" :description="error" />

    <template v-else-if="data">
      <!-- 頭像、名字、本季分數 -->
      <header class="hero hud-frame">
        <span class="corner tl"></span>
        <span class="corner br"></span>
        <AvatarUploader
          v-if="editable"
          :member-id="member.id"
          :name="member.name"
          :src="member.avatar_url"
          :size="84"
          @updated="value => emit('avatar-updated', value)"
        />
        <PlayerAvatar v-else :id="member.id" :name="member.name" :src="member.avatar_url" :size="84" />

        <div class="identity">
          <span class="hud-label">{{ data.season_name ?? '全部比賽' }}</span>
          <h1 class="name">{{ member.name }}</h1>
          <div class="tags">
            <span v-for="tag in tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <slot name="actions"></slot>
        </div>

        <div class="score">
          <CountUp class="score-value num" :value="data.rating" :decimals="1" />
          <span class="score-meta num">{{ data.wins }}W {{ data.losses }}L · {{ winRate }}%</span>
          <n-select
            v-if="seasonOptions.length > 1"
            :value="seasonId ?? currentSeason?.id ?? null"
            :options="seasonOptions"
            size="small"
            class="season-select"
            @update:value="id => (seasonId = id === currentSeason?.id ? null : id)"
          />
        </div>
      </header>

      <section v-if="data.trend.length" class="panel">
        <h2 class="hud-label">分數走勢</h2>
        <RatingMeter
          :rating="data.rating"
          :total-matches="matches"
          :performances="data.trend.map(p => p.rating)"
          trend-only
        />
      </section>

      <div class="grid">
        <section class="panel">
          <h2 class="hud-label">搭檔</h2>
          <HeadToHeadList :entries="data.partners" :tags="partnerTags" empty-text="這個賽季還沒有雙打紀錄" />
        </section>
        <section class="panel">
          <h2 class="hud-label">對手</h2>
          <HeadToHeadList :entries="data.opponents" :tags="opponentTags" empty-text="這個賽季還沒有比賽" />
        </section>
      </div>

      <section v-if="data.seasons.length" class="panel">
        <h2 class="hud-label">歷屆賽季</h2>
        <ul class="seasons">
          <li v-for="season in data.seasons" :key="season.season_id" class="season-row">
            <span class="season-name">{{ season.season_name }}</span>
            <span class="num season-rating">{{ season.rating.toFixed(1) }}</span>
            <span class="num season-meta">{{ season.matches }} 場</span>
            <span class="num season-meta">
              {{ season.rank ? `#${season.rank} / ${season.ranked_count}` : '—' }}
            </span>
          </li>
        </ul>
      </section>

      <section class="panel">
        <h2 class="hud-label">最近比賽</h2>
        <div v-if="recent.length" class="recent">
          <MatchCard
            v-for="record in recent"
            :key="record.id"
            :record="record"
            @view="row => router.push({ name: 'ViewMatch', params: { id: row.id } })"
            @edit="row => router.push({ name: 'EditMatch', params: { id: row.id } })"
          />
        </div>
        <p v-else class="empty">還沒有比賽</p>
      </section>
    </template>
  </div>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { matchesApi, membersApi } from '@/api'
  import AvatarUploader from '@/components/base/AvatarUploader.vue'
  import CountUp from '@/components/base/CountUp.vue'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import MatchCard from '@/components/match/MatchCard.vue'
  import RatingMeter from '@/components/profile/RatingMeter.vue'
  import { useSeasons } from '@/composables/useSeasons'
  import { headToHeadHighlights } from '@/utils/insights'
  import { organizationLabel } from '@/utils/player'
  import HeadToHeadList from './HeadToHeadList.vue'

  /** 球員頁：本季分數、走勢、搭檔、對手、歷屆賽季與最近比賽。editable 時可以換頭像。 */
  const props = defineProps({
    memberId: { type: Number, required: true },
    editable: { type: Boolean, default: false }
  })
  const emit = defineEmits(['avatar-updated', 'loaded'])

  const router = useRouter()
  const { current: currentSeason, options: seasonOptions, load: loadSeasons } = useSeasons()
  const loading = ref(true)
  const error = ref(null)
  const data = ref(null)
  const recent = ref([])
  // null 為目前賽季
  const seasonId = ref(null)

  const member = computed(() => data.value.member)
  const matches = computed(() => data.value.wins + data.value.losses)
  const winRate = computed(() => (matches.value ? Math.round((data.value.wins / matches.value) * 100) : 0))
  const tags = computed(() => {
    const m = member.value
    return [
      m.is_guest ? '訪客' : null,
      m.identity_label,
      organizationLabel(m) || null,
      m.is_a_division ? '甲組' : null,
      m.has_left ? '已離隊' : null
    ].filter(Boolean)
  })

  const highlights = computed(() => headToHeadHighlights(data.value?.partners, data.value?.opponents))
  const tagFor = (entry, label) => (entry ? { [entry.player.id]: label } : {})
  const partnerTags = computed(() => tagFor(highlights.value.bestPartner, '最佳搭檔'))
  const opponentTags = computed(() => ({
    ...tagFor(highlights.value.nemesis, '剋星'),
    ...tagFor(highlights.value.favorite, '苦主')
  }))

  const load = async () => {
    loading.value = true
    error.value = null
    try {
      const [insights, list] = await Promise.all([
        membersApi.insights(props.memberId, { season_id: seasonId.value || undefined }),
        matchesApi.list({ player_id: props.memberId, per_page: 6, sort_by: 'match_date', sort_order: 'desc' })
      ])
      data.value = insights
      recent.value = list.items
      emit('loaded', insights.member)
    } catch (err) {
      error.value = err.response?.data?.message || '請稍後再試'
    } finally {
      loading.value = false
    }
  }

  watch(
    () => props.memberId,
    () => {
      seasonId.value = null
      load()
    }
  )
  watch(seasonId, load)
  loadSeasons()
  load()
</script>

<style scoped>
  .hero {
    --corner-color: var(--accent);
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    align-items: center;
    gap: 20px;
    margin-bottom: 16px;
    padding: 20px;
    border: 1px solid var(--ink);
    background: var(--surface-2);
  }
  .identity {
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-width: 0;
  }
  .name {
    margin: 0;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--ink);
  }
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .tag {
    padding: 0 8px;
    border: 1px solid var(--line);
    font-size: 14px;
    color: var(--ink-2);
  }
  .score {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
  }
  .score-value {
    font-size: 56px;
    line-height: 1;
    color: var(--ink);
  }
  .score-meta {
    font-size: 14px;
    color: var(--ink-3);
  }
  .season-select {
    width: 150px;
  }
  .panel {
    margin-bottom: 16px;
    padding: 16px 18px;
    border: 1px solid var(--line-soft);
    background: var(--surface);
  }
  .panel h2 {
    margin: 0 0 12px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }
  .seasons {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .season-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 60px 70px 90px;
    align-items: baseline;
    gap: 10px;
    padding: 8px 0;
    border-top: 1px solid var(--line-soft);
  }
  .season-row:first-child {
    border-top: 0;
  }
  .season-name {
    font-weight: 600;
    color: var(--ink);
  }
  .season-rating {
    font-size: 20px;
    color: var(--ink);
  }
  .season-meta {
    color: var(--ink-3);
    text-align: right;
  }
  .recent {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .empty {
    margin: 0;
    color: var(--ink-3);
  }
  @media (max-width: 760px) {
    .hero {
      grid-template-columns: auto minmax(0, 1fr);
    }
    .score {
      grid-column: 1 / -1;
      flex-direction: row;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 12px;
    }
    .season-select {
      margin-left: auto;
    }
    .grid {
      grid-template-columns: minmax(0, 1fr);
    }
  }
</style>
