import { computed, ref } from 'vue'
import { seasonsApi } from '@/api'
import { seasonOptions } from '@/utils/season'

/** 賽季清單（最新的在前）。載入失敗時當作沒有賽季，頁面照常顯示目前的資料。 */
export function useSeasons() {
  const seasons = ref([])
  const current = computed(() => seasons.value.find(season => season.is_current) ?? null)
  const options = computed(() => seasonOptions(seasons.value))
  const byId = id => seasons.value.find(season => season.id === id) ?? null

  const load = async () => {
    try {
      seasons.value = await seasonsApi.list()
    } catch {
      seasons.value = []
    }
  }

  return { seasons, current, options, byId, load }
}
