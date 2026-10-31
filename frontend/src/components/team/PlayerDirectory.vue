<template>
  <div class="directory">
    <div class="toolbar">
      <div class="chips" role="tablist" aria-label="球員分類">
        <button
          v-for="option in CATEGORIES"
          :key="option.value"
          type="button"
          role="tab"
          class="chip"
          :class="{ active: category === option.value }"
          :aria-selected="category === option.value"
          @click="category = option.value"
        >
          {{ option.label }} <span class="num count">{{ counts[option.value] }}</span>
        </button>
      </div>
      <n-input v-model:value="keyword" placeholder="搜尋姓名、學校" clearable size="small" class="search">
        <template #prefix><n-icon :component="Search" /></template>
      </n-input>
    </div>

    <div v-if="loading" class="rows">
      <n-skeleton v-for="n in 6" :key="n" height="56px" />
    </div>
    <n-empty v-else-if="!visible.length" description="沒有符合的球員" class="empty" />
    <ul v-else class="rows">
      <li
        v-for="(player, index) in visible"
        :key="player.id"
        class="row stagger-in"
        :style="{ '--i': Math.min(index, 20) }"
        tabindex="0"
        @click="open(player)"
        @keydown.enter="open(player)"
      >
        <PlayerAvatar :id="player.id" :name="player.name" :src="player.avatar_url" :size="38" />
        <span class="who">
          <span class="name">
            {{ player.name }}
            <span v-if="player.is_a_division" class="tag">甲組</span>
            <span v-if="!player.user && !player.is_guest" class="tag muted">無帳號</span>
          </span>
          <span class="sub">{{ subline(player) }}</span>
        </span>
        <span class="score num">{{ player.total_matches ? formatRating(player.rating) : '—' }}</span>
        <span class="meta num">{{ player.total_matches }} 場</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { Search } from '@vicons/carbon'
  import { leaderboardApi } from '@/api'
  import PlayerAvatar from '@/components/base/PlayerAvatar.vue'
  import { organizationLabel } from '@/utils/player'
  import { formatRating } from '@/utils/rating'

  const CATEGORIES = [
    { value: 'team', label: '校隊' },
    { value: 'alumni', label: '校友會' },
    { value: 'left', label: '離隊' },
    { value: 'guest', label: '對手' },
    { value: 'all', label: '全部' }
  ]

  /** 所有球員（隊員與訪客）一份名單，依分類切換；點一下進球員頁。分數與場數是目前賽季。 */
  const router = useRouter()
  const loading = ref(true)
  const players = ref([])
  const category = ref('team')
  const keyword = ref('')

  // 「對手」包含訪客與其他學校的正式成員
  const categoryOf = player => (player.roster_category === 'other' ? 'guest' : player.roster_category)
  const counts = computed(() => {
    const result = { all: players.value.length }
    for (const option of CATEGORIES.slice(0, -1)) {
      result[option.value] = players.value.filter(p => categoryOf(p) === option.value).length
    }
    return result
  })
  const visible = computed(() => {
    const term = keyword.value.trim().toLowerCase()
    return players.value
      .filter(p => category.value === 'all' || categoryOf(p) === category.value)
      .filter(p => !term || [p.name, organizationLabel(p)].some(text => (text || '').toLowerCase().includes(term)))
      .sort((a, b) => b.total_matches - a.total_matches || a.name.localeCompare(b.name, 'zh-Hant'))
  })

  const subline = player =>
    [organizationLabel(player), player.last_match_date ? `最後 ${player.last_match_date}` : null]
      .filter(Boolean)
      .join(' · ') || '—'

  const open = player => router.push({ name: 'Player', params: { id: player.id } })

  onMounted(async () => {
    try {
      const { items } = await leaderboardApi.list({
        scope: 'all',
        include_guests: true,
        include_inactive: true,
        min_matches: 0,
        per_page: 500
      })
      players.value = items
    } finally {
      loading.value = false
    }
  })
</script>

<style scoped>
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 14px;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    border: 1px solid var(--line);
  }
  .chip {
    padding: 7px 14px;
    border: 0;
    border-left: 1px solid var(--line);
    background: transparent;
    color: var(--ink-3);
    font: inherit;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }
  .chip:first-child {
    border-left: 0;
  }
  .chip.active {
    background: var(--ink);
    color: var(--bg);
  }
  .count {
    margin-left: 4px;
    font-size: 13px;
    opacity: 0.7;
  }
  .search {
    width: 220px;
  }
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
    grid-template-columns: 38px minmax(0, 1fr) 64px 60px;
    align-items: center;
    gap: 12px;
    padding: 9px 14px;
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
  .who {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }
  .name {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    color: var(--ink);
  }
  .tag {
    padding: 0 6px;
    border: 1px solid var(--ink-2);
    font-size: 12px;
    color: var(--ink-2);
  }
  .tag.muted {
    border-color: var(--line);
    color: var(--ink-4);
  }
  .sub {
    font-size: 14px;
    color: var(--ink-3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .score {
    font-size: 20px;
    text-align: right;
    color: var(--ink);
  }
  .meta {
    font-size: 14px;
    text-align: right;
    color: var(--ink-3);
  }
  .empty {
    padding: 48px 0;
  }
  @media (max-width: 640px) {
    .search {
      width: 100%;
    }
    .chips {
      width: 100%;
    }
    .chip {
      flex: 1;
      padding: 7px 4px;
    }
  }
</style>
