import { computed } from 'vue'
import {
  AddCircleOutline,
  ListOutline,
  PeopleOutline,
  PersonCircleOutline,
  PodiumOutline,
  StatsChartOutline,
  StopwatchOutline
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/authStore'
import { usePermissions } from './usePermissions'

/** 側邊欄與手機底部分頁列的導覽項目（依登入狀態與角色過濾）。 */
export function useNavItems() {
  const authStore = useAuthStore()
  const { hasManagementAccess } = usePermissions()

  const items = computed(() => {
    const loggedIn = authStore.isAuthenticated
    const staff = hasManagementAccess.value
    return [
      { name: 'Leaderboard', label: '排行榜', icon: PodiumOutline, show: true },
      { name: 'DetailLeaderboard', label: '詳細數據', icon: StatsChartOutline, show: loggedIn },
      { name: 'RecordMatch', label: '記錄比賽', icon: AddCircleOutline, show: staff },
      { name: 'RefereeMode', label: '裁判模式', icon: StopwatchOutline, show: staff, beta: true },
      { name: 'MatchManagement', label: '比賽管理', icon: ListOutline, show: staff },
      { name: 'ManagementCenter', label: '團隊管理', icon: PeopleOutline, show: staff },
      { name: 'EditProfile', label: '我的', icon: PersonCircleOutline, show: loggedIn, mobileOnly: true }
    ].filter(item => item.show)
  })

  const sidebarItems = computed(() => items.value.filter(item => !item.mobileOnly))

  /** 手機最多 5 個分頁；「記錄比賽」放中間當主要按鈕。 */
  const bottomItems = computed(() => {
    const pick = ['Leaderboard', 'MatchManagement', 'RecordMatch', 'ManagementCenter', 'EditProfile']
    const fallback = ['Leaderboard', 'DetailLeaderboard', 'EditProfile']
    const order = hasManagementAccess.value ? pick : fallback
    return order.map(name => items.value.find(item => item.name === name)).filter(Boolean)
  })

  return { sidebarItems, bottomItems }
}
