<template>
  <div class="practice-list">
    <PageHeader eyebrow="Practice" title="練習日">
      <template #actions>
        <n-button type="primary" @click="startOpen = true">
          <template #icon><n-icon :component="Add" /></template>
          開始練習日
        </n-button>
      </template>
    </PageHeader>

    <div v-if="loading" class="rows">
      <n-skeleton v-for="n in 4" :key="n" height="60px" />
    </div>
    <n-empty v-else-if="!sessions.length" description="還沒有練習日" class="empty" />
    <ul v-else class="rows">
      <li
        v-for="(session, index) in sessions"
        :key="session.id"
        class="row stagger-in"
        :style="{ '--i': Math.min(index, 20) }"
        tabindex="0"
        @click="open(session)"
        @keydown.enter="open(session)"
      >
        <span class="date num">{{ session.session_date }}</span>
        <span class="weekday">{{ weekday(session.session_date) }}</span>
        <span class="location">{{ session.location || '—' }}</span>
        <span class="meta num">{{ session.attendees.length }} 人</span>
        <span class="meta num">{{ session.match_count }} 場</span>
      </li>
    </ul>

    <n-modal v-model:show="startOpen" preset="card" title="開始練習日" style="width: min(720px, 96vw)">
      <n-form label-placement="top">
        <n-grid :cols="2" :x-gap="12">
          <n-form-item-gi label="日期">
            <n-date-picker v-model:value="draft.date" type="date" class="full" :clearable="false" />
          </n-form-item-gi>
          <n-form-item-gi label="地點">
            <n-input v-model:value="draft.location" maxlength="100" />
          </n-form-item-gi>
        </n-grid>
        <n-form-item label="到場">
          <AttendeePicker v-model="draft.player_ids" :players="players" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="startOpen = false">取消</n-button>
          <n-button type="primary" :loading="saving" :disabled="draft.player_ids.length < 4" @click="start">
            開始（{{ draft.player_ids.length }} 人）
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
  import { onMounted, reactive, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { Add } from '@vicons/carbon'
  import { membersApi, practiceApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import AttendeePicker from '@/components/practice/AttendeePicker.vue'
  import { formatDate } from '@/utils/format'

  const WEEKDAYS = '日一二三四五六'

  const router = useRouter()
  const message = useMessage()
  const loading = ref(true)
  const saving = ref(false)
  const startOpen = ref(false)
  const sessions = ref([])
  const players = ref([])
  const draft = reactive({ date: Date.now(), location: '', player_ids: [] })

  const weekday = value => `週${WEEKDAYS[new Date(`${value}T00:00:00`).getDay()]}`
  const open = session => router.push({ name: 'PracticeSession', params: { id: session.id } })

  watch(startOpen, async show => {
    if (!show) return
    // 預設帶入上一次的地點
    draft.location = draft.location || sessions.value[0]?.location || ''
    if (!players.value.length) players.value = await membersApi.list({ include_guests: true, sort_by: 'roster' })
  })

  const start = async () => {
    saving.value = true
    try {
      const session = await practiceApi.create({
        session_date: formatDate(draft.date),
        location: draft.location || null,
        player_ids: draft.player_ids
      })
      open(session)
    } catch (error) {
      message.error(error.response?.data?.message || '建立失敗')
    } finally {
      saving.value = false
    }
  }

  onMounted(async () => {
    try {
      sessions.value = await practiceApi.list()
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .rows {
    display: flex;
    flex-direction: column;
    margin: 0;
    padding: 0;
    list-style: none;
    border: 1px solid var(--line-soft);
  }
  .row {
    display: grid;
    grid-template-columns: 110px 40px minmax(0, 1fr) 60px 60px;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-top: 1px solid var(--line-soft);
    background: var(--surface);
    cursor: pointer;
    outline: none;
  }
  .row:first-child {
    border-top: 0;
  }
  .row:hover,
  .row:focus-visible {
    background: var(--surface-sunk);
  }
  .date {
    font-size: 17px;
    color: var(--ink);
  }
  .weekday,
  .meta {
    font-size: 14px;
    color: var(--ink-3);
  }
  .meta {
    text-align: right;
  }
  .location {
    color: var(--ink-2);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
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
