<template>
  <div class="dashboard">
    <n-skeleton v-if="loading" height="180px" :sharp="false" class="block" />
    <n-result v-else-if="error" status="error" title="無法載入個人資料" :description="error">
      <template #footer><n-button @click="load">重試</n-button></template>
    </n-result>

    <template v-else-if="profile">
      <ProfileHero
        :profile="profile"
        @edit="showEdit = true"
        @change-password="showPassword = true"
        @avatar-updated="handleAvatarUpdated"
      />

      <n-alert v-if="!member" type="info" title="這個帳號沒有對應的球員資料" class="block">
        需要由幹部建立球員資料後，才能記錄比賽與上排行榜。
      </n-alert>

      <template v-else>
        <div class="stats-grid">
          <div class="rank-card">
            <span class="rank-label">排行榜名次</span>
            <template v-if="rank">
              <span class="rank-value num">#<CountUp :value="rank" /></span>
              <span class="rank-sub">共 {{ rankedCount }} 位上榜</span>
            </template>
            <template v-else>
              <span class="rank-value unranked">未上榜</span>
              <span class="rank-sub">再打 {{ matchesToQualify }} 場就能上榜</span>
            </template>
          </div>
          <StatCard
            label="排名分數"
            :value="Math.round(member.conservative_score * 100)"
            :icon="TrophyOutline"
            accent="var(--gold-500)"
          />
          <StatCard
            label="勝率"
            :value="stats.win_rate"
            :decimals="1"
            suffix="%"
            :icon="PieChartOutline"
            accent="var(--green-600)"
          />
          <StatCard label="比賽場次" :value="stats.total_matches" :icon="TennisballOutline" accent="var(--red-500)" />
        </div>

        <div class="content-grid">
          <n-card class="panel" title="能力指標">
            <AbilityBars :member="member" />
            <div class="form-row">
              <span class="form-label">最近 5 場</span>
              <RecentForm :form="stats.recent_form" />
            </div>
          </n-card>

          <n-card class="panel" title="最近比賽">
            <RecentMatchList :matches="recentMatches" />
          </n-card>

          <n-card class="panel" title="球員檔案">
            <dl class="profile-list">
              <div v-for="item in profileItems" :key="item.label">
                <dt>{{ item.label }}</dt>
                <dd>{{ item.value || '—' }}</dd>
              </div>
            </dl>
          </n-card>
        </div>
      </template>

      <ProfileEditDrawer v-model:show="showEdit" :profile="profile" @saved="handleSaved" />
      <n-modal v-model:show="showPassword" preset="card" title="修改密碼" style="width: min(420px, 92vw)">
        <ChangePasswordForm @changed="showPassword = false" />
      </n-modal>
    </template>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { PieChartOutline, TennisballOutline, TrophyOutline } from '@vicons/ionicons5'
  import { leaderboardApi, membersApi, profileApi } from '@/api'
  import ChangePasswordForm from '@/components/auth/ChangePasswordForm.vue'
  import CountUp from '@/components/base/CountUp.vue'
  import StatCard from '@/components/base/StatCard.vue'
  import RecentForm from '@/components/leaderboard/RecentForm.vue'
  import AbilityBars from '@/components/profile/AbilityBars.vue'
  import ProfileEditDrawer from '@/components/profile/ProfileEditDrawer.vue'
  import ProfileHero from '@/components/profile/ProfileHero.vue'
  import RecentMatchList from '@/components/profile/RecentMatchList.vue'
  import { useOptions } from '@/composables/useOptions'
  import { useAuthStore } from '@/stores/authStore'
  import { formatDate } from '@/utils/format'

  // 與首頁排行榜相同的上榜門檻
  const MIN_MATCHES = 5

  const authStore = useAuthStore()
  const { getGenderDisplay, getPositionDisplay } = useOptions()

  const loading = ref(true)
  const error = ref(null)
  const profile = ref(null)
  const stats = ref({ win_rate: 0, total_matches: 0, recent_form: [] })
  const ranking = ref([])
  const recentMatches = ref([])
  const showEdit = ref(false)
  const showPassword = ref(false)

  const member = computed(() => profile.value?.member)
  const rankedCount = computed(() => ranking.value.length)
  const rank = computed(() => {
    const index = ranking.value.findIndex(entry => entry.id === member.value?.id)
    return index >= 0 ? index + 1 : null
  })
  const matchesToQualify = computed(() => Math.max(0, MIN_MATCHES - stats.value.total_matches))

  const profileItems = computed(() => [
    { label: '真實姓名', value: member.value.name },
    { label: '帳號', value: profile.value.username },
    { label: '學號', value: member.value.student_id },
    { label: '性別', value: member.value.gender && getGenderDisplay(member.value.gender) },
    { label: '擅長位置', value: member.value.position && getPositionDisplay(member.value.position) },
    { label: '所屬組織', value: member.value.organization?.name },
    { label: '入隊日期', value: formatDate(member.value.joined_date) },
    { label: '電子郵件', value: profile.value.email }
  ])

  const load = async () => {
    loading.value = true
    error.value = null
    try {
      profile.value = await profileApi.get()
      if (member.value) {
        const [memberStats, board, matches] = await Promise.all([
          membersApi.stats(member.value.id),
          leaderboardApi.list({ include_guests: false, min_matches: MIN_MATCHES, per_page: 500 }),
          profileApi.matches({ per_page: 5 })
        ])
        stats.value = memberStats
        ranking.value = board.items
        recentMatches.value = matches.items
      }
    } catch (err) {
      error.value = err.response?.data?.message || '請稍後再試'
    } finally {
      loading.value = false
    }
  }

  const syncAuthUser = () => {
    authStore.setUser({
      ...authStore.user,
      display_name: profile.value.display_name,
      avatar_url: member.value?.avatar_url
    })
  }

  const handleSaved = updated => {
    profile.value = updated
    syncAuthUser()
  }

  const handleAvatarUpdated = updatedMember => {
    profile.value = { ...profile.value, member: updatedMember }
    syncAuthUser()
  }

  onMounted(load)
</script>

<style scoped>
  .block {
    margin-bottom: 24px;
  }
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }
  .rank-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 16px 20px;
    border-radius: var(--radius-lg);
    background: linear-gradient(135deg, var(--gold-300), var(--gold-500));
    color: var(--blue-950);
    box-shadow: var(--shadow-md);
  }
  .rank-label {
    font-size: 13px;
    font-weight: 700;
  }
  .rank-value {
    font-size: 40px;
    font-weight: 700;
    line-height: 1.05;
  }
  .rank-value.unranked {
    font-size: 26px;
    font-weight: 800;
  }
  .rank-sub {
    font-size: 12px;
    font-weight: 600;
    opacity: 0.75;
  }
  .content-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr);
    gap: 20px;
  }
  .panel :deep(.n-card-header__main) {
    font-weight: 800;
    color: var(--blue-900);
  }
  .content-grid > .panel:last-child {
    grid-column: 1 / -1;
  }
  .form-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 22px;
    padding-top: 16px;
    border-top: 1px dashed var(--color-border);
  }
  .form-label {
    font-weight: 700;
    color: var(--gray-700);
  }
  .profile-list {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px 24px;
    margin: 0;
  }
  .profile-list dt {
    font-size: 12px;
    color: var(--color-text-muted);
  }
  .profile-list dd {
    margin: 2px 0 0;
    font-weight: 700;
    color: var(--blue-900);
    word-break: break-all;
  }

  @media (max-width: 900px) {
    .stats-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .content-grid {
      grid-template-columns: minmax(0, 1fr);
    }
    .profile-list {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
</style>
