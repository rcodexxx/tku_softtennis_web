<template>
  <div class="category-picker">
    <div class="segments" role="radiogroup" aria-label="比賽分類">
      <button
        v-for="option in MATCH_CATEGORIES"
        :key="option.value"
        type="button"
        role="radio"
        class="segment"
        :class="{ active: category === option.value }"
        :aria-checked="category === option.value"
        @click="category = option.value"
      >
        {{ option.label }}
      </button>
    </div>

    <div v-if="category === 'event'" class="event-row">
      <n-select
        v-model:value="eventId"
        :options="eventOptions"
        :loading="loading"
        placeholder="選擇賽事"
        filterable
        class="event-select"
      />
      <n-button @click="creating = true">
        <template #icon><n-icon :component="Add" /></template>
        新增賽事
      </n-button>
    </div>

    <n-modal v-model:show="creating" preset="card" title="新增賽事" style="width: min(440px, 94vw)">
      <n-form label-placement="top">
        <n-form-item label="賽事名稱">
          <n-input v-model:value="draft.name" maxlength="100" placeholder="例如 淡江盃" />
        </n-form-item>
        <n-form-item label="日期">
          <n-date-picker v-model:value="draft.date" type="date" clearable class="full" />
        </n-form-item>
        <n-form-item label="地點">
          <n-input v-model:value="draft.location" maxlength="100" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="creating = false">取消</n-button>
          <n-button type="primary" :loading="saving" :disabled="!draft.name?.trim()" @click="createEvent"
            >建立</n-button
          >
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useMessage } from 'naive-ui'
  import { Add } from '@vicons/carbon'
  import { eventsApi } from '@/api'
  import { formatDate } from '@/utils/format'
  import { MATCH_CATEGORIES } from '@/utils/matchCategory'

  /** 比賽分類（隊內／校外友誼／賽事）；選賽事時挑一個賽事，也可以直接新增。 */
  const category = defineModel('category', { type: String, default: 'internal' })
  const eventId = defineModel('eventId', { type: Number, default: null })

  const message = useMessage()
  const events = ref([])
  const loading = ref(false)
  const creating = ref(false)
  const saving = ref(false)
  const draft = reactive({ name: '', date: Date.now(), location: '' })

  const eventOptions = computed(() =>
    events.value.map(event => ({
      label: event.start_date ? `${event.name}（${event.start_date}）` : event.name,
      value: event.id
    }))
  )

  const load = async () => {
    loading.value = true
    try {
      events.value = await eventsApi.list()
    } catch {
      events.value = []
    } finally {
      loading.value = false
    }
  }

  const createEvent = async () => {
    saving.value = true
    try {
      const event = await eventsApi.create({
        name: draft.name.trim(),
        start_date: formatDate(draft.date),
        location: draft.location || null
      })
      events.value = [event, ...events.value]
      eventId.value = event.id
      creating.value = false
      Object.assign(draft, { name: '', location: '' })
    } catch (error) {
      message.error(error.response?.data?.message || '建立賽事失敗')
    } finally {
      saving.value = false
    }
  }

  onMounted(load)
</script>

<style scoped>
  .category-picker {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }
  .segments {
    display: flex;
    border: 1px solid var(--line);
    align-self: flex-start;
  }
  .segment {
    min-width: 96px;
    padding: 8px 16px;
    border: 0;
    border-left: 1px solid var(--line);
    background: transparent;
    color: var(--ink-3);
    font: inherit;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition:
      background var(--duration-fast),
      color var(--duration-fast);
  }
  .segment:first-child {
    border-left: 0;
  }
  .segment:hover {
    color: var(--ink);
  }
  .segment.active {
    background: var(--ink);
    color: var(--bg);
  }
  .event-row {
    display: flex;
    gap: 8px;
  }
  .event-select {
    flex: 1;
    min-width: 0;
  }
  .full {
    width: 100%;
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
  @media (max-width: 640px) {
    .segments {
      align-self: stretch;
    }
    .segment {
      flex: 1;
      min-width: 0;
    }
  }
</style>
