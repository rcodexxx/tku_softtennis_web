<template>
  <div class="roster-page">
    <PageHeader eyebrow="Roster" title="名單整理" />

    <n-spin :show="loading">
      <RosterEditor :rows="rows" />
    </n-spin>

    <footer class="footer">
      <n-button size="large" @click="router.back()">返回</n-button>
      <span class="hud-label">{{ changes.length ? `${changes.length} 人有變動` : '沒有變動' }}</span>
      <n-button type="primary" size="large" :disabled="!changes.length" :loading="saving" @click="save">
        儲存
      </n-button>
    </footer>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { membersApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import RosterEditor from '@/components/team/RosterEditor.vue'
  import { rosterPayload } from '@/utils/season'

  const router = useRouter()
  const message = useMessage()

  const loading = ref(true)
  const saving = ref(false)
  const rows = ref([])
  const changes = computed(() => rosterPayload(rows.value))

  const load = async () => {
    loading.value = true
    try {
      rows.value = (await membersApi.roster()).map(row => ({ ...row, choice: row.status }))
    } catch (error) {
      message.error(error.response?.data?.message || '載入名單失敗')
    } finally {
      loading.value = false
    }
  }

  const save = async () => {
    saving.value = true
    try {
      await membersApi.updateRoster(changes.value)
      message.success(`已更新 ${changes.value.length} 位隊員`)
      await load()
    } catch (error) {
      message.error(error.response?.data?.message || '儲存失敗')
    } finally {
      saving.value = false
    }
  }

  onMounted(load)
</script>

<style scoped>
  .roster-page {
    max-width: 860px;
    margin: 0 auto;
  }
  .footer {
    position: sticky;
    bottom: 0;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 16px;
    padding: 12px 0;
    background: linear-gradient(transparent, var(--bg) 30%);
  }
  .footer .hud-label {
    flex: 1;
    text-align: right;
  }
  @media (max-width: 900px) {
    .footer {
      bottom: calc(var(--bottom-nav-height) + env(safe-area-inset-bottom));
    }
  }
</style>
