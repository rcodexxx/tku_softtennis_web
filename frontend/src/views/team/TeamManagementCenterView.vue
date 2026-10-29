<template>
  <div class="team-page">
    <PageHeader eyebrow="TEAM" title="團隊管理" subtitle="管理隊員、訪客與合作組織。">
      <template #actions>
        <n-button type="primary" @click="router.push({ name: 'AddMember' })">
          <template #icon><n-icon :component="PersonAddOutline" /></template>
          新增成員
        </n-button>
      </template>
    </PageHeader>

    <div class="stats">
      <StatCard label="在隊隊員" :value="counts.active" :icon="PeopleOutline" />
      <StatCard label="訪客" :value="counts.guests" :icon="PersonOutline" accent="var(--gold-500)" />
      <StatCard label="組織" :value="organizations.length" :icon="BusinessOutline" accent="var(--red-500)" />
    </div>

    <n-tabs v-model:value="tab" type="line" size="large" animated>
      <n-tab-pane name="members" tab="成員">
        <MemberDirectory :members="members" :organizations="organizations" :loading="loading" @changed="load" />
      </n-tab-pane>
      <n-tab-pane name="organizations" tab="組織">
        <OrganizationList :organizations="organizations" :loading="loading" @changed="load" />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { BusinessOutline, PeopleOutline, PersonAddOutline, PersonOutline } from '@vicons/ionicons5'
  import { membersApi, organizationsApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import StatCard from '@/components/base/StatCard.vue'
  import MemberDirectory from '@/components/team/MemberDirectory.vue'
  import OrganizationList from '@/components/team/OrganizationList.vue'

  const router = useRouter()
  const message = useMessage()

  const tab = ref('members')
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
