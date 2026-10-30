<template>
  <div class="match-detail">
    <div class="topbar">
      <n-button quaternary @click="router.push({ name: canManage ? 'MatchManagement' : 'Leaderboard' })">
        <template #icon><n-icon :component="ArrowLeft" /></template>
        返回
      </n-button>
      <div v-if="record" class="actions">
        <n-button v-if="canManage" secondary @click="router.push({ name: 'EditMatch', params: { id: record.id } })">
          <template #icon><n-icon :component="Edit" /></template>
          編輯
        </n-button>
        <n-button v-if="canDeleteMatch" secondary type="error" @click="confirmDelete">
          <template #icon><n-icon :component="TrashCan" /></template>
          刪除
        </n-button>
      </div>
    </div>

    <n-skeleton v-if="loading" height="240px" :sharp="false" />
    <n-result v-else-if="!record" status="404" title="找不到這場比賽" />

    <template v-else>
      <MatchScoreboard
        :team-a="[record.player1, record.player2].filter(Boolean)"
        :team-b="[record.player3, record.player4].filter(Boolean)"
        :a-games="record.a_games"
        :b-games="record.b_games"
        :match-date="record.match_date"
        :match-type="record.match_type"
        :match-format="record.match_format"
        :games="record.games"
      />

      <div class="grid">
        <n-card title="每局比分" class="panel">
          <template v-if="record.has_detailed_scores">
            <GameTimeline :games="record.games" :match-format="record.match_format" />
            <div v-if="record.serve_advantage" class="serve-stats">
              <div v-for="side in serveSides" :key="side.key" class="serve-stat">
                <span class="serve-title">{{ side.label }}發球局</span>
                <span class="num serve-value">{{ side.stats.serve_wins }} / {{ side.stats.serve_games }}</span>
                <n-progress
                  type="line"
                  :percentage="side.stats.serve_win_rate"
                  :color="side.color"
                  :show-indicator="false"
                />
                <span class="serve-rate">保發率 {{ side.stats.serve_win_rate }}%</span>
              </div>
            </div>
          </template>
          <n-empty v-else description="這場比賽只記錄了總局數" />
        </n-card>

        <n-card title="比賽資訊" class="panel">
          <dl class="info">
            <div v-for="item in infoItems" :key="item.label">
              <dt>{{ item.label }}</dt>
              <dd>{{ item.value || '—' }}</dd>
            </div>
          </dl>
          <a v-if="record.youtube_url" :href="record.youtube_url" target="_blank" rel="noopener" class="video-link">
            <n-icon :component="Video" size="20" />
            觀看比賽影片
          </a>
          <p v-if="record.notes" class="notes">{{ record.notes }}</p>
        </n-card>
      </div>
    </template>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog, useMessage } from 'naive-ui'
  import { ArrowLeft, Edit, TrashCan, Video } from '@vicons/carbon'
  import { matchesApi } from '@/api'
  import GameTimeline from '@/components/match/GameTimeline.vue'
  import MatchScoreboard from '@/components/match/MatchScoreboard.vue'
  import { useOptions } from '@/composables/useOptions'
  import { usePermissions } from '@/composables/usePermissions'

  const props = defineProps({ matchId: { type: [String, Number], required: true } })

  const router = useRouter()
  const dialog = useDialog()
  const message = useMessage()
  const { hasManagementAccess: canManage, canDeleteMatch } = usePermissions()
  const { courtSurfaceOptions, courtEnvironmentOptions, timeSlotOptions, getOptionLabel } = useOptions()

  const loading = ref(true)
  const record = ref(null)

  const serveSides = computed(() => [
    { key: 'side_a', label: 'A 方', color: 'var(--blue-600)', stats: record.value.serve_advantage.side_a },
    { key: 'side_b', label: 'B 方', color: 'var(--red-500)', stats: record.value.serve_advantage.side_b }
  ])

  const infoItems = computed(() => {
    const r = record.value
    const label = (options, value) => value && getOptionLabel(options, value)
    return [
      { label: '比賽日期', value: r.match_date },
      { label: '時段', value: label(timeSlotOptions, r.time_slot) },
      { label: '場地', value: label(courtSurfaceOptions, r.court_surface) },
      { label: '環境', value: label(courtEnvironmentOptions, r.court_environment) },
      { label: '比賽時長', value: r.duration_minutes && `${r.duration_minutes} 分鐘` },
      { label: '先發球', value: r.first_serve_side && (r.first_serve_side === 'side_a' ? 'A 方' : 'B 方') }
    ]
  })

  const confirmDelete = () => {
    dialog.error({
      title: '刪除比賽紀錄',
      content: '確定要刪除這場比賽嗎？球員的分數會重新計算，且無法復原。',
      positiveText: '刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await matchesApi.remove(record.value.id)
          message.success('比賽紀錄已刪除')
          router.push({ name: 'MatchManagement' })
        } catch (err) {
          message.error(err.response?.data?.message || '刪除失敗')
        }
      }
    })
  }

  onMounted(async () => {
    try {
      record.value = await matchesApi.get(props.matchId)
    } catch {
      record.value = null
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .actions {
    display: flex;
    gap: 8px;
  }
  .grid {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
    gap: 20px;
    margin-top: 24px;
  }
  .panel :deep(.n-card-header__main) {
    font-weight: 800;
    color: var(--blue-900);
  }
  .serve-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 22px;
    padding-top: 18px;
    border-top: 1px dashed var(--color-border);
  }
  .serve-stat {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .serve-title {
    font-weight: 700;
    color: var(--gray-700);
  }
  .serve-value {
    font-size: 26px;
    font-weight: 700;
    color: var(--blue-900);
  }
  .serve-rate {
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px 18px;
    margin: 0;
  }
  .info dt {
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .info dd {
    margin: 2px 0 0;
    font-weight: 700;
    color: var(--blue-900);
  }
  .video-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 18px;
    padding: 8px 14px;
    border-radius: var(--radius-md);
    background: var(--red-100);
    color: var(--red-600);
    font-weight: 700;
  }
  .notes {
    margin: 16px 0 0;
    padding: 12px;
    border-radius: var(--radius-md);
    background: var(--gray-100);
    white-space: pre-wrap;
  }
  @media (max-width: 900px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }
</style>
