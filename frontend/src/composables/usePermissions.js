import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

/** 與後端 staff_required / admin_required 對應的前端權限判斷。 */
export function usePermissions() {
  const authStore = useAuthStore()

  // 幹部、教練、管理員可以管理隊員與比賽紀錄
  const hasManagementAccess = computed(
    () => authStore.isAuthenticated && (authStore.isAdmin || authStore.isCoach || authStore.isCadre)
  )
  const isAdmin = computed(() => authStore.isAuthenticated && authStore.isAdmin)

  return {
    hasManagementAccess,
    canEditMember: hasManagementAccess,
    canDeleteMember: isAdmin,
    canDeleteMatch: isAdmin,
    canManageOrganization: isAdmin
  }
}
