<template>
  <div class="team-page">
    <PageHeader eyebrow="Manage" title="管理">
      <template #actions>
        <n-button @click="router.push({ name: 'Roster' })">
          <template #icon><n-icon :component="ListChecked" /></template>
          名單整理
        </n-button>
        <n-button type="primary" @click="router.push({ name: 'AddMember' })">
          <template #icon><n-icon :component="UserFollow" /></template>
          新增成員
        </n-button>
      </template>
    </PageHeader>

    <n-tabs v-model:value="tab" type="line" size="large" animated>
      <n-tab-pane name="members" tab="成員">
        <MemberDirectory :members="members" :organizations="organizations" :loading="loading" @changed="load" />
      </n-tab-pane>
      <n-tab-pane name="organizations" tab="組織">
        <OrganizationList :organizations="organizations" :loading="loading" @changed="load" />
      </n-tab-pane>
      <n-tab-pane name="boards" tab="榜單" display-directive="show:lazy">
        <BoardList />
      </n-tab-pane>
      <n-tab-pane name="seasons" tab="賽季" display-directive="show:lazy">
        <SeasonList />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup>
  import { onMounted, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { ListChecked, UserFollow } from '@vicons/carbon'
  import { membersApi, organizationsApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import MemberDirectory from '@/components/team/MemberDirectory.vue'
  import OrganizationList from '@/components/team/OrganizationList.vue'
  import BoardList from '@/components/team/BoardList.vue'
  import SeasonList from '@/components/team/SeasonList.vue'

  const router = useRouter()
  const route = useRoute()
  const message = useMessage()

  const TABS = ['members', 'organizations', 'boards', 'seasons']
  const tab = ref(TABS.includes(route.query.tab) ? route.query.tab : 'members')
  const loading = ref(true)
  const members = ref([])
  const organizations = ref([])

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
