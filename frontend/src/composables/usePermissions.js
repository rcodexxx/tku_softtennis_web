// src/composables/usePermissions.js
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

/**
 * 權限管理 Composable
 * 統一處理應用中的權限檢查邏輯
 */
export function usePermissions() {
  const authStore = useAuthStore()

  // 基礎權限檢查
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const userRole = computed(() => authStore.userRole)

  // 角色權限
  const isAdmin = computed(() => authStore.isAdmin)
  const isCoach = computed(() => authStore.isCoach)
  const isCadre = computed(() => authStore.isCadre)
  const isMember = computed(() => userRole.value === 'member')

  // 管理權限 (在多個組件中重複出現的邏輯)
  const hasManagementAccess = computed(() => isAuthenticated.value && (isCadre.value || isAdmin.value || isCoach.value))

  // 功能特定權限
  const canViewManagement = computed(() => hasManagementAccess.value)
  const canEditMember = computed(() => hasManagementAccess.value)
  const canDeleteMember = computed(() => isAdmin.value)
  const canEditMatch = computed(() => hasManagementAccess.value)
  const canDeleteMatch = computed(() => isAdmin.value)
  const canViewPrivateData = computed(() => hasManagementAccess.value)
  const canManageOrganization = computed(() => isAdmin.value)

  // 比賽相關權限
  const canRecordMatch = computed(() => hasManagementAccess.value)
  const canEditMatchScore = computed(() => hasManagementAccess.value)
  const canUseRefereeMode = computed(() => hasManagementAccess.value)

  // 權限檢查輔助函數
  const checkRole = requiredRole => {
    if (!isAuthenticated.value) return false

    const roleHierarchy = {
      member: 1,
      cadre: 2,
      coach: 3,
      admin: 4
    }

    const userLevel = roleHierarchy[userRole.value] || 0
    const requiredLevel = roleHierarchy[requiredRole] || 0

    return userLevel >= requiredLevel
  }

  const checkPermission = permission => {
    const permissions = {
      view_management: canViewManagement.value,
      edit_member: canEditMember.value,
      delete_member: canDeleteMember.value,
      edit_match: canEditMatch.value,
      delete_match: canDeleteMatch.value,
      record_match: canRecordMatch.value,
      referee_mode: canUseRefereeMode.value,
      manage_organization: canManageOrganization.value
    }

    return permissions[permission] || false
  }

  return {
    // 基礎狀態
    isAuthenticated,
    userRole,

    // 角色檢查
    isAdmin,
    isCoach,
    isCadre,
    isMember,

    // 管理權限
    hasManagementAccess,

    // 功能權限
    canViewManagement,
    canEditMember,
    canDeleteMember,
    canEditMatch,
    canDeleteMatch,
    canViewPrivateData,
    canManageOrganization,
    canRecordMatch,
    canEditMatchScore,
    canUseRefereeMode,

    // 輔助函數
    checkRole,
    checkPermission
  }
}
