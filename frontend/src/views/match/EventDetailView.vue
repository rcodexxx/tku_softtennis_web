<template>
  <div class="event-page">
    <n-button text class="back" @click="router.push({ name: 'Events' })">
      <template #icon><n-icon :component="ArrowLeft" /></template>
      賽事
    </n-button>

    <PageHeader v-if="event" eyebrow="Event" :title="event.name" :subtitle="subtitle" />
    <n-skeleton v-else-if="loading" height="64px" />

    <div class="section-head">
      <span class="hud-label">{{ records.length }} 場比賽</span>
      <span class="rule"></span>
      <n-button
        size="small"
        type="primary"
        @click="router.push({ name: 'BatchRecordMatch', query: { event: event?.id } })"
      >
        <template #icon><n-icon :component="Add" /></template>
        補登這個賽事
      </n-button>
    </div>

    <div v-if="loading" class="list">
      <n-skeleton v-for="n in 3" :key="n" height="112px" />
    </div>
    <n-empty v-else-if="!records.length" description="這個賽事還沒有比賽" class="empty" />
    <div v-else class="list">
      <MatchCard
        v-for="record in records"
        :key="record.id"
        :record="record"
        @view="row => router.push({ name: 'ViewMatch', params: { id: row.id } })"
        @edit="row => router.push({ name: 'EditMatch', params: { id: row.id } })"
      />
    </div>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'
  import { Add, ArrowLeft } from '@vicons/carbon'
  import { eventsApi, matchesApi } from '@/api'
  import PageHeader from '@/components/base/PageHeader.vue'
  import MatchCard from '@/components/match/MatchCard.vue'
  import { eventDateLabel } from '@/utils/matchCategory'

  const props = defineProps({ eventId: { type: [String, Number], required: true } })

  const router = useRouter()
  const message = useMessage()
  const loading = ref(true)
  const event = ref(null)
  const records = ref([])

  const subtitle = computed(() =>
    [eventDateLabel(event.value), event.value?.location, event.value?.counts_toward_rating ? null : '不計入分數']
      .filter(Boolean)
      .join(' · ')
  )

  onMounted(async () => {
    try {
      const [detail, list] = await Promise.all([
        eventsApi.get(props.eventId),
        matchesApi.list({ event_id: props.eventId, per_page: 200, sort_by: 'match_date', sort_order: 'desc' })
      ])
      event.value = detail
      records.value = list.items
    } catch (error) {
      message.error(error.response?.data?.message || '載入賽事失敗')
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .back {
    margin-bottom: 12px;
  }
  .section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 8px 0 12px;
  }
  .rule {
    flex: 1;
    height: 1px;
    background: var(--line);
  }
  .list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .empty {
    padding: 48px 0;
  }
</style>
