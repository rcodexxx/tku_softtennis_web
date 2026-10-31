<template>
  <div class="player-page">
    <n-button text class="back" @click="router.back()">
      <template #icon><n-icon :component="ArrowLeft" /></template>
      返回
    </n-button>

    <PlayerProfile :member-id="Number(id)" @loaded="member = $event">
      <template v-if="hasManagementAccess && member" #actions>
        <div class="actions">
          <n-button size="small" @click="router.push({ name: 'EditMember', params: { id: member.id } })">
            <template #icon><n-icon :component="Edit" /></template>
            編輯
          </n-button>
          <n-button v-if="!member.user" size="small" @click="mergeOpen = true">
            <template #icon><n-icon :component="GroupObjects" /></template>
            合併到…
          </n-button>
          <n-button v-if="canDeleteMember" size="small" type="error" quaternary @click="confirmDelete">
            <template #icon><n-icon :component="TrashCan" /></template>
            刪除
          </n-button>
        </div>
      </template>
    </PlayerProfile>

    <n-modal v-model:show="mergeOpen" preset="card" title="合併重複的球員" style="width: min(440px, 94vw)">
      <p class="merge-note">
        把「{{ member?.name }}」的所有比賽併到另一位球員身上，然後刪除「{{ member?.name }}」。同一個人被建了兩次時使用。
      </p>
      <n-select
        v-model:value="mergeTarget"
        :options="mergeOptions"
        :loading="playersLoading"
        filterable
        placeholder="選擇要保留的球員"
      />
      <template #footer>
        <div class="modal-footer">
          <n-button @click="mergeOpen = false">取消</n-button>
          <n-button type="primary" :disabled="!mergeTarget" :loading="merging" @click="merge">合併</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog, useMessage } from 'naive-ui'
  import { ArrowLeft, Edit, GroupObjects, TrashCan } from '@vicons/carbon'
  import { guestsApi, membersApi } from '@/api'
  import PlayerProfile from '@/components/player/PlayerProfile.vue'
  import { usePermissions } from '@/composables/usePermissions'
  import { organizationLabel } from '@/utils/player'

  const props = defineProps({ id: { type: [String, Number], required: true } })

  const router = useRouter()
  const message = useMessage()
  const dialog = useDialog()
  const { hasManagementAccess, canDeleteMember } = usePermissions()

  const member = ref(null)
  const mergeOpen = ref(false)
  const mergeTarget = ref(null)
  const merging = ref(false)
  const players = ref([])
  const playersLoading = ref(false)

  const mergeOptions = computed(() =>
    players.value
      .filter(player => player.id !== member.value?.id)
      .map(player => ({
        label: [player.name, player.is_guest ? '訪客' : null, organizationLabel(player)].filter(Boolean).join(' · '),
        value: player.id
      }))
  )

  watch(mergeOpen, async open => {
    if (!open || players.value.length) return
    playersLoading.value = true
    try {
      players.value = await membersApi.list({ include_guests: true, sort_by: 'roster' })
    } finally {
      playersLoading.value = false
    }
  })

  const merge = async () => {
    merging.value = true
    try {
      const target = await membersApi.merge(member.value.id, mergeTarget.value)
      message.success(`已合併到「${target.name}」`)
      mergeOpen.value = false
      router.replace({ name: 'Player', params: { id: target.id } })
    } catch (error) {
      message.error(error.response?.data?.message || '合併失敗')
    } finally {
      merging.value = false
    }
  }

  const confirmDelete = () => {
    dialog.warning({
      title: '刪除球員',
      content: `確定要刪除「${member.value.name}」嗎？已經有比賽紀錄的球員不能刪除。`,
      positiveText: '刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          if (member.value.is_guest) await guestsApi.remove(member.value.id)
          else await membersApi.remove(member.value.id)
          message.success('已刪除')
          router.push({ name: 'ManagementCenter' })
        } catch (error) {
          message.error(error.response?.data?.message || '刪除失敗')
        }
      }
    })
  }

  watch(
    () => props.id,
    () => (member.value = null)
  )
</script>

<style scoped>
  .player-page {
    max-width: 960px;
    margin: 0 auto;
  }
  .back {
    margin-bottom: 12px;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 6px;
  }
  .merge-note {
    margin: 0 0 12px;
    color: var(--ink-2);
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>
