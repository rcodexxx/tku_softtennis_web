<template>
  <div class="events-page">
    <PageHeader eyebrow="Events" title="賽事">
      <template #actions>
        <n-button type="primary" @click="openForm()">
          <template #icon><n-icon :component="Add" /></template>
          新增賽事
        </n-button>
      </template>
    </PageHeader>

    <div v-if="loading" class="list">
      <n-skeleton v-for="n in 3" :key="n" height="76px" />
    </div>
    <n-empty v-else-if="!events.length" description="還沒有賽事" class="empty" />
    <ul v-else class="list">
      <li
        v-for="(event, index) in events"
        :key="event.id"
        class="event stagger-in"
        :style="{ '--i': index }"
        tabindex="0"
        @click="router.push({ name: 'EventDetail', params: { id: event.id } })"
        @keydown.enter="router.push({ name: 'EventDetail', params: { id: event.id } })"
      >
        <div class="event-main">
          <span class="event-name">{{ event.name }}</span>
          <span class="event-meta num">
            {{ eventDateLabel(event) || '未填日期' }}<template v-if="event.location"> · {{ event.location }}</template>
          </span>
        </div>
        <span v-if="!event.counts_toward_rating" class="no-rating">不計分</span>
        <span class="count num">{{ event.match_count }} 場</span>
        <span class="actions" @click.stop>
          <n-button quaternary circle size="small" title="編輯" @click="openForm(event)">
            <template #icon><n-icon :component="Edit" /></template>
          </n-button>
          <n-button quaternary circle size="small" type="error" title="刪除" @click="confirmDelete(event)">
            <template #icon><n-icon :component="TrashCan" /></template>
          </n-button>
        </span>
      </li>
    </ul>

    <n-modal
      v-model:show="formOpen"
      preset="card"
      :title="editing ? '編輯賽事' : '新增賽事'"
      style="width: min(480px, 94vw)"
    >
      <n-form label-placement="top">
        <n-form-item label="賽事名稱">
          <n-input v-model:value="form.name" maxlength="100" placeholder="例如 淡江盃" />
        </n-form-item>
        <n-form-item label="日期">
          <n-date-picker v-model:value="form.range" type="daterange" clearable class="full" />
        </n-form-item>
        <n-form-item label="地點">
          <n-input v-model:value="form.location" maxlength="100" />
        </n-form-item>
        <n-form-item label="計入分數">
          <n-switch v-model:value="form.counts_toward_rating" />
        </n-form-item>
        <n-form-item label="備註">
          <n-input v-model:value="form.notes" type="textarea" :rows="2" maxlength="500" />
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
  import { onMounted, reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog, useMessage } from 'naive-ui'
  import { Add, Edit, TrashCan } from '@vicons/carbon'
  import { eventsApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import { dateToTimestamp, formatDate } from '@/utils/format'
  import { eventDateLabel } from '@/utils/matchCategory'

  const router = useRouter()
  const message = useMessage()
  const dialog = useDialog()

  const loading = ref(true)
  const events = ref([])
  const formOpen = ref(false)
  const saving = ref(false)
  const editing = ref(null)
  const form = reactive({ name: '', range: null, location: '', notes: '', counts_toward_rating: true })

  const load = async () => {
    loading.value = true
    try {
      events.value = await eventsApi.list()
    } catch (error) {
      message.error(error.response?.data?.message || '載入賽事失敗')
    } finally {
      loading.value = false
    }
  }

  const openForm = (event = null) => {
    editing.value = event
    Object.assign(form, {
      name: event?.name ?? '',
      range: event?.start_date
        ? [dateToTimestamp(event.start_date), dateToTimestamp(event.end_date || event.start_date)]
        : null,
      location: event?.location ?? '',
      notes: event?.notes ?? '',
      counts_toward_rating: event?.counts_toward_rating ?? true
    })
    formOpen.value = true
  }

  const save = async () => {
    saving.value = true
    const data = {
      name: form.name.trim(),
      start_date: form.range ? formatDate(form.range[0]) : null,
      end_date: form.range ? formatDate(form.range[1]) : null,
      location: form.location || null,
      notes: form.notes || null,
      counts_toward_rating: form.counts_toward_rating
    }
    try {
      if (editing.value) await eventsApi.update(editing.value.id, data)
      else await eventsApi.create(data)
      formOpen.value = false
      await load()
    } catch (error) {
      message.error(error.response?.data?.message || '儲存失敗')
    } finally {
      saving.value = false
    }
  }

  const confirmDelete = event => {
    dialog.warning({
      title: '刪除賽事',
      content: `確定要刪除「${event.name}」嗎？`,
      positiveText: '刪除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await eventsApi.remove(event.id)
          await load()
        } catch (error) {
          message.error(error.response?.data?.message || '刪除失敗')
        }
      }
    })
  }

  onMounted(load)
</script>

<style scoped>
  .list {
    display: flex;
    flex-direction: column;
    margin: 0;
    padding: 0;
    list-style: none;
    gap: 8px;
  }
  .event {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    border: 1px solid var(--line-soft);
    border-left: 3px solid var(--ink);
    background: var(--surface);
    cursor: pointer;
    outline: none;
    transition:
      border-color var(--duration-fast),
      background var(--duration-fast);
  }
  .event:hover,
  .event:focus-visible {
    border-left-color: var(--accent);
    background: var(--surface-sunk);
  }
  .event-main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .event-name {
    font-size: 18px;
    font-weight: 700;
    color: var(--ink);
  }
  .event-meta {
    font-size: 14px;
    color: var(--ink-3);
  }
  .no-rating {
    padding: 0 6px;
    border: 1px solid var(--line);
    font-size: 13px;
    color: var(--ink-3);
  }
  .count {
    font-size: 16px;
    color: var(--ink-2);
  }
  .actions {
    display: flex;
    gap: 2px;
  }
  .empty {
    padding: 48px 0;
  }
  .full {
    width: 100%;
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>
