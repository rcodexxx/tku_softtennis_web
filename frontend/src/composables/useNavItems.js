import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Edit, Settings, Trophy } from '@vicons/carbon'
import { usePermissions } from './usePermissions'

/**
 * 導覽只有三個入口：排行榜、記錄、管理；「我的」放在右上角頭像的選單裡。
 * routes 列出屬於這個入口的頁面，在這些頁面時入口會顯示為目前位置。
 */
const ITEMS = [
  {
    name: 'Leaderboard',
    code: '01',
    label: '排行榜',
    icon: Trophy,
    routes: ['Leaderboard', 'DetailLeaderboard']
  },
  {
    name: 'MatchManagement',
    code: '02',
    label: '記錄',
    icon: Edit,
    staff: true,
    routes: ['MatchManagement', 'RecordMatch', 'BatchRecordMatch', 'ViewMatch', 'EditMatch', 'Events', 'EventDetail']
  },
  {
    name: 'ManagementCenter',
    code: '03',
    label: '管理',
    icon: Settings,
    staff: true,
    routes: ['ManagementCenter', 'AddMember', 'EditMember', 'NewSeason', 'Roster']
  }
]

/** 側邊欄與手機底部分頁列的導覽項目（依角色過濾）。 */
export function useNavItems() {
  const route = useRoute()
  const { hasManagementAccess } = usePermissions()

  const items = computed(() => ITEMS.filter(item => !item.staff || hasManagementAccess.value))
  const isActive = item => item.routes.includes(route.name)

  return { items, isActive }
}
