<template>
  <div class="boards">
    <div class="toolbar">
      <n-button type="primary" @click="openForm()">
        <template #icon><n-icon :component="Add" /></template>
        新增榜單
      </n-button>
    </div>

    <div v-if="loading" class="list">
      <n-skeleton v-for="n in 2" :key="n" height="72px" />
    </div>
    <n-empty v-else-if="!boards.length" description="還沒有自訂榜單" class="empty" />
    <ul v-else class="list">
      <li v-for="board in boards" :key="board.id" class="board">
        <div class="board-main">
          <span class="board-name">{{ board.name }}</span>
          <span class="board-members">{{ board.members.map(m => m.name).join('、') || '還沒有成員' }}</span>
        </div>
        <span class="count num">{{ board.members.length }} 人</span>
        <n-button quaternary circle size="small" title="編輯" @click="openForm(board)">
          <template #icon><n-icon :component="Edit" /></template>
        </n-button>
        <n-button quaternary circle size="small" type="error" title="刪除" @click="confirmDelete(board)">
          <template #icon><n-icon :component="TrashCan" /></template>
        </n-button>
      </li>
    </ul>

    <n-modal
      v-model:show="formOpen"
      preset="card"
      :title="editing ? '編輯榜單' : '新增榜單'"
      style="width: min(520px, 94vw)"
    >
      <n-form label-placement="top">
        <n-form-item label="榜單名稱">
          <n-input v-model:value="form.name" maxlength="50" placeholder="例如 打球嗎" />
        </n-form-item>
        <n-form-item label="成員">
          <n-select
            v-model:value="form.member_ids"
            :options="memberOptions"
            :loading="membersLoading"
            multiple
            filterable
            placeholder="搜尋並加入球員（也可以選訪客）"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="formOpen = false">取消</n-button>
          <n-button type="primary" :loading="saving" :disabled="!form.name?.trim()" @click="save">儲存</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useDialog, useMessage } from 'naive-ui'
  import { Add, Edit, TrashCan } from '@vicons/carbon'
  import { boardsApi, membersApi } from '@/api'

  const message = useMessage()
  const dialog = useDialog()

  const loading = ref(true)
  const boards = ref([])
  const members = ref([])
  const membersLoading = ref(false)
  const formOpen = ref(false)
  const saving = ref(false)
  const editing = ref(null)
  const form = reactive({ name: '', member_ids: [] })

  const memberOptions = computed(() =>
    members.value.map(member => ({
      label: member.is_guest ? `${member.name}（訪客）` : member.name,
      value: member.id
    }))
  )

  const load = async () => {
    loading.value = true
    try {
      boards.value = await boardsApi.list()
    } catch (error) {
      message.error(error.response?.data?.message || '載入榜單失敗')
    } finally {
      loading.value = false
    }
  }

  const loadMembers = async () => {
    if (members.value.length) return
    membersLoading.value = true
    try {
      members.value = await membersApi.list({ include_guests: true, sort_by: 'roster' })
    } finally {
      membersLoading.value = false
    }
  }

  const openForm = (board = null) => {
    editing.value = board
    Object.assign(form, { name: board?.name ?? '', member_ids: board?.members.map(m => m.id) ?? [] })
    formOpen.value = true
    loadMembers()
  }

  const save = async () => {
    saving.value = true
    const data = { name: form.name.trim(), member_ids: form.member_ids }
    try {
      if (editing.value) await boardsApi.update(editing.value.id, data)
      else await boardsApi.create(data)
      formOpen.value = false
      await load()
    } catch (error) {
      message.error(error.response?.data?.message || '儲存失敗')
    } finally {
      saving.value = false
    }
  }

  const confirmDelete = board => {
    dialog.warning({
      title: '刪除榜單',
      content: `確定要刪除「${board.name}」嗎？球員和比賽紀錄不會受影響。`,
      positiveText: '刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        await boardsApi.remove(board.id)
        await load()
      }
    })
  }

  onMounted(load)
</script>

<style scoped>
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
  }
  .list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .board {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    border: 1px solid var(--line-soft);
    border-left: 3px solid var(--accent);
    background: var(--surface);
  }
  .board-main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .board-name {
    font-size: 18px;
    font-weight: 700;
    color: var(--ink);
  }
  .board-members {
    font-size: 14px;
    color: var(--ink-3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .count {
    color: var(--ink-2);
  }
  .empty {
    padding: 48px 0;
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>
