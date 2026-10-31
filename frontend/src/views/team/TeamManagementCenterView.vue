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
          新增球員
        </n-button>
      </template>
    </PageHeader>

    <n-tabs v-model:value="tab" type="line" size="large" animated>
      <n-tab-pane name="members" tab="球員">
        <PlayerDirectory />
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
  import { organizationsApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import PlayerDirectory from '@/components/team/PlayerDirectory.vue'
  import OrganizationList from '@/components/team/OrganizationList.vue'
  import BoardList from '@/components/team/BoardList.vue'
  import SeasonList from '@/components/team/SeasonList.vue'

  const router = useRouter()
  const route = useRoute()
  const message = useMessage()

  const TABS = ['members', 'organizations', 'boards', 'seasons']
  const tab = ref(TABS.includes(route.query.tab) ? route.query.tab : 'members')
  const loading = ref(true)
  const organizations = ref([])

  const load = async () => {
    loading.value = true
    try {
      organizations.value = await organizationsApi.list()
    } catch (error) {
      message.error(error.response?.data?.message || '載入資料失敗')
    } finally {
      loading.value = false
    }
  }

  onMounted(load)
</script>
