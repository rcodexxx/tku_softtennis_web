<template>
  <ul v-if="entries.length" class="h2h">
    <li
      v-for="entry in visible"
      :key="entry.player.id"
      class="h2h-row"
      :class="{ 'with-chemistry': showChemistry }"
      tabindex="0"
      @click="open(entry)"
      @keydown.enter="open(entry)"
    >
      <PlayerAvatar :id="entry.player.id" :name="entry.player.name" :src="entry.player.avatar_url" :size="32" />
      <span class="who">
        <span class="name">{{ entry.player.name }}</span>
        <span v-if="tags[entry.player.id]" class="tag">{{ tags[entry.player.id] }}</span>
      </span>
      <span class="record num">{{ entry.wins }}W {{ entry.losses }}L</span>
      <span v-if="showChemistry" class="chemistry num" :class="tone(entry.chemistry)" title="默契">
        {{ formatChemistry(entry.chemistry) }}
      </span>
      <span class="rate">
        <span class="bar"><span class="fill" :style="{ width: `${entry.win_rate}%` }"></span></span>
        <span class="num">{{ Math.round(entry.win_rate) }}%</span>
      </span>
    </li>
    <li v-if="entries.length > limit && !expanded" class="more">
      <n-button text size="small" @click="expanded = true">再顯示 {{ entries.length - limit }} 位</n-button>
    </li>
  </ul>
  <p v-else class="empty">{{ emptyText }}</p>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { formatChemistry } from '@/utils/pairs'

  /** 搭檔或對手的戰績列表；tags 以球員 id 標示亮點（例如「最佳搭檔」）。 */
  const props = defineProps({
    entries: { type: Array, required: true },
    tags: { type: Object, default: () => ({}) },
    limit: { type: Number, default: 6 },
    emptyText: { type: String, default: '還沒有資料' },
    // 搭檔列表多一欄默契值
    showChemistry: { type: Boolean, default: false }
  })

  const router = useRouter()
  const expanded = ref(false)
  const visible = computed(() => (expanded.value ? props.entries : props.entries.slice(0, props.limit)))

  const tone = value => (value >= 0.15 ? 'up' : value <= -0.15 ? 'down' : '')
  const open = entry => router.push({ name: 'Player', params: { id: entry.player.id } })
</script>

<style scoped>
  .h2h {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .h2h-row {
    display: grid;
    grid-template-columns: 32px minmax(0, 1fr) 72px 110px;
    align-items: center;
    gap: 10px;
    padding: 8px 4px;
    border-top: 1px solid var(--line-soft);
    cursor: pointer;
    outline: none;
  }
  .h2h-row.with-chemistry {
    grid-template-columns: 32px minmax(0, 1fr) 72px 44px 110px;
  }
  .h2h-row:first-child {
    border-top: 0;
  }
  .h2h-row:hover,
  .h2h-row:focus-visible {
    background: var(--surface-sunk);
  }
  .who {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
  }
  .name {
    font-weight: 600;
    color: var(--ink);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .tag {
    flex-shrink: 0;
    padding: 0 6px;
    border: 1px solid var(--accent-soft);
    color: var(--accent-text);
    font-size: 13px;
    font-weight: 600;
  }
  .record {
    font-size: 14px;
    color: var(--ink-2);
  }
  .chemistry {
    font-size: 14px;
    color: var(--ink-3);
  }
  .up {
    color: var(--win);
  }
  .down {
    color: var(--loss);
  }
  .rate {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--ink-2);
  }
  .bar {
    flex: 1;
    height: 2px;
    background: var(--line);
  }
  .fill {
    display: block;
    height: 100%;
    background: var(--ink);
  }
  .more {
    padding-top: 6px;
    text-align: center;
  }
  .empty {
    margin: 0;
    padding: 12px 0;
    color: var(--ink-3);
  }
  @media (max-width: 520px) {
    .h2h-row {
      grid-template-columns: 32px minmax(0, 1fr) 64px 44px;
    }
    .h2h-row.with-chemistry {
      grid-template-columns: 32px minmax(0, 1fr) 64px 40px 40px;
    }
    .bar {
      display: none;
    }
  }
</style>
