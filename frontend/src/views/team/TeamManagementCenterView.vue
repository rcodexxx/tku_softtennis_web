<template>
  <div class="team-page">
    <PageHeader eyebrow="TEAM" title="團隊管理" subtitle="管理隊員、訪客、合作組織與賽季。">
      <template #actions>
        <n-button type="primary" @click="router.push({ name: 'AddMember' })">
          <template #icon><n-icon :component="UserFollow" /></template>
          新增成員
        </n-button>
      </template>
    </PageHeader>

    <div class="stats">
      <StatCard label="在隊隊員" :value="counts.active" :icon="UserMultiple" />
      <StatCard label="訪客" :value="counts.guests" :icon="User" accent="var(--gold-500)" />
      <StatCard label="組織" :value="organizations.length" :icon="Building" accent="var(--red-500)" />
    </div>

    <n-tabs v-model:value="tab" type="line" size="large" animated>
      <n-tab-pane name="members" tab="成員">
        <MemberDirectory :members="members" :organizations="organizations" :loading="loading" @changed="load" />
      </n-tab-pane>
      <n-tab-pane name="organizations" tab="組織">
        <OrganizationList :organizations="organizations" :loading="loading" @changed="load" />
      </n-tab-pane>
      <n-tab-pane name="seasons" tab="賽季" display-directive="show:lazy">
        <SeasonList />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { Building, User, UserFollow, UserMultiple } from '@vicons/carbon'
  import { membersApi, organizationsApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import StatCard from '@/components/base/StatCard.vue'
  import MemberDirectory from '@/components/team/MemberDirectory.vue'
  import OrganizationList from '@/components/team/OrganizationList.vue'
  import SeasonList from '@/components/team/SeasonList.vue'

  const router = useRouter()
  const route = useRoute()
  const message = useMessage()

  const TABS = ['members', 'organizations', 'seasons']
  const tab = ref(TABS.includes(route.query.tab) ? route.query.tab : 'members')
  const loading = ref(true)
  const members = ref([])
  const organizations = ref([])

  const counts = computed(() => ({
    active: members.value.filter(m => !m.is_guest && m.is_active).length,
    guests: members.value.filter(m => m.is_guest).length
  }))

  const load = async () => {
    loading.value = true
    try {
      const [memberList, orgList] = await Promise.all([
        membersApi.list({ include_guests: true, include_inactive: true, sort_by: 'name', sort_order: 'asc' }),
        organizationsApi.list()
      ])
      members.value = memberList
      organizations.value = orgList
    } catch (error) {
      message.error(error.response?.data?.message || '載入資料失敗')
    } finally {
      loading.value = false
    }
  }

  onMounted(load)
</script>

<style scoped>
  .stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 20px;
  }
  @media (max-width: 640px) {
    .stats {
      gap: 8px;
    }
    .stats :deep(.stat-card) {
      flex-direction: column;
      align-items: flex-start;
      padding: 12px;
    }
  }
</style>
