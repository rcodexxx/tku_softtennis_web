<template>
  <div class="filters">
    <n-select
      :value="filters.player_ids"
      :options="playerOptions"
      :loading="playersLoading"
      multiple
      filterable
      clearable
      :max-tag-count="2"
      placeholder="球員（可多選）"
      class="filter players"
      @search="query => emit('player-search', query)"
      @update:value="value => set('player_ids', value)"
    />
    <n-select
      :value="filters.result"
      :options="winLossOptions"
      :disabled="!filters.player_ids.length"
      clearable
      placeholder="勝負"
      class="filter small"
      @update:value="value => set('result', value)"
    />
    <n-select
      :value="filters.category"
      :options="MATCH_CATEGORIES"
      clearable
      placeholder="分類"
      class="filter small"
      @update:value="value => set('category', value)"
    />
    <n-select
      :value="filters.match_type"
      :options="matchTypeOptions"
      clearable
      placeholder="類型"
      class="filter small"
      @update:value="value => set('match_type', value)"
    />
    <n-select
      :value="filters.match_format"
      :options="matchFormatOptions"
      clearable
      placeholder="賽制"
      class="filter small"
      @update:value="value => set('match_format', value)"
    />
    <n-date-picker
      :value="filters.date_range"
      type="daterange"
      clearable
      class="filter dates"
      @update:value="value => set('date_range', value)"
    />
    <n-button v-if="active" text type="primary" @click="emit('reset')">清除篩選</n-button>
  </div>
</template>

<script setup>
  import { MATCH_CATEGORIES } from '@/utils/matchCategory'
  import { computed } from 'vue'
  import { useOptions } from '@/composables/useOptions'

  /** 比賽列表的篩選列；filters 由父元件持有。勝負篩選以第一位選擇的球員為準。 */
  const props = defineProps({
    filters: { type: Object, required: true },
    playerOptions: { type: Array, default: () => [] },
    playersLoading: { type: Boolean, default: false }
  })
  const emit = defineEmits(['update:filters', 'reset', 'player-search'])

  const { matchTypeOptions, matchFormatOptions, winLossOptions } = useOptions()

  const active = computed(() => {
    const f = props.filters
    return Boolean(f.player_ids.length || f.result || f.category || f.match_type || f.match_format || f.date_range)
  })

  const set = (key, value) => {
    const next = { ...props.filters, [key]: value ?? (key === 'player_ids' ? [] : null) }
    if (key === 'player_ids' && !next.player_ids.length) next.result = null
    emit('update:filters', next)
  }
</script>

<style scoped>
  .filters {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    padding: 14px;
    border-radius: var(--radius-lg);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
  }
  .players {
    width: 260px;
  }
  .small {
    width: 110px;
  }
  .dates {
    width: 260px;
  }
  @media (max-width: 640px) {
    .filter {
      width: 100% !important;
    }
    .small {
      width: calc(33% - 7px) !important;
    }
  }
</style>
