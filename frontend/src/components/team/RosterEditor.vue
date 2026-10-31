<template>
  <div class="roster-editor">
    <div class="toolbar">
      <div class="tally">
        <span v-for="choice in ROSTER_CHOICES" :key="choice.value" class="tally-item" :class="choice.value">
          {{ choice.label }} <b class="num">{{ summary[choice.value].count }}</b>
        </span>
      </div>
      <n-input v-model:value="keyword" placeholder="搜尋隊員" clearable size="small" class="search">
        <template #prefix><n-icon :component="Search" /></template>
      </n-input>
    </div>

    <n-empty v-if="!rows.length" description="校隊和校友會目前沒有隊員" class="empty" />
    <ul v-else class="roster">
      <li
        v-for="(row, index) in visibleRows"
        :key="row.member.id"
        class="roster-row stagger-in"
        :class="{ changed: row.choice !== row.status, [row.choice]: true }"
        :style="{ '--i': Math.min(index, 20) }"
      >
        <PlayerAvatar :id="row.member.id" :name="row.member.name" :src="row.member.avatar_url" :size="40" />
        <div class="who">
          <span class="name">
            {{ row.member.name }}
            <span v-if="row.is_a_division" class="division">甲組</span>
          </span>
          <span class="meta">
            {{ STATUS_LABELS[row.status] }} · 本季 {{ row.total_matches }} 場
            <template v-if="row.last_match_date"> · 最後 {{ row.last_match_date }}</template>
          </span>
        </div>
        <n-radio-group v-model:value="row.choice" size="small" class="choice">
          <n-radio-button v-for="choice in ROSTER_CHOICES" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </n-radio-button>
        </n-radio-group>
      </li>
    </ul>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { Search } from '@vicons/carbon'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { ROSTER_CHOICES, rosterSummary } from '@/utils/season'

  const STATUS_LABELS = { team: '校隊', alumni: '已畢業', left: '已離隊' }

  /** rows：{ member, status, choice, ... }，直接修改 row.choice。 */
  const props = defineProps({ rows: { type: Array, required: true } })

  const keyword = ref('')
  const summary = computed(() => rosterSummary(props.rows))
  const visibleRows = computed(() => {
    const term = keyword.value.trim().toLowerCase()
    return term ? props.rows.filter(row => row.member.name.toLowerCase().includes(term)) : props.rows
  })
</script>

<style scoped>
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
  }
  .tally {
    display: flex;
    gap: 8px;
  }
  .tally-item {
    padding: 4px 12px;
    border: 1px solid var(--line);
    font-size: 14px;
    font-weight: 600;
    color: var(--ink-2);
  }
  .tally-item b {
    margin-left: 4px;
    color: var(--ink);
  }
  .search {
    width: 200px;
  }
  .roster {
    display: flex;
    flex-direction: column;
    margin: 0;
    padding: 0;
    list-style: none;
    border: 1px solid var(--line-soft);
  }
  .roster-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-top: 1px solid var(--line-soft);
    border-left: 3px solid var(--accent-color);
    background: var(--surface);
    transition: background var(--duration-fast) var(--ease-out);
  }
  .roster-row:first-child {
    border-top: 0;
  }
  .roster-row.changed {
    background: var(--tint);
  }
  .who {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 17px;
    font-weight: 600;
    color: var(--ink);
  }
  .division {
    padding: 0 6px;
    border: 1px solid var(--ink);
    font-size: 13px;
    font-weight: 600;
  }
  .meta {
    font-size: 14px;
    color: var(--ink-3);
  }
  .empty {
    padding: 40px 0;
  }

  /* 三種去向：校隊墨色、畢業重點色、離隊灰色 */
  .team {
    --accent-color: var(--ink);
    --tint: var(--surface-sunk);
  }
  .alumni {
    --accent-color: var(--accent);
    --tint: var(--accent-tint);
  }
  .left {
    --accent-color: var(--ink-4);
    --tint: var(--surface-sunk);
  }

  @media (max-width: 640px) {
    .roster-row {
      flex-wrap: wrap;
    }
    .choice {
      width: 100%;
      display: flex;
    }
    .choice :deep(.n-radio-button) {
      flex: 1;
      text-align: center;
    }
    .search {
      width: 100%;
    }
  }
</style>
