// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

// 導入組件
import LeaderboardView from '../views/leaderboard/LeaderboardView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import Dashboard from '../views/Dashboard.vue'
import ManagementCenterView from '@/views/team/ManagementCenterView.vue'
import AddMemberView from '../views/team/AddMemberView.vue'
import EditMemberView from '@/views/team/EditMemberView.vue'
import MatchManagementView from '@/views/match/MatchManagementView.vue'
import DetailLeaderboardView from '@/views/leaderboard/DetailLeaderboardView.vue'

// 🔧 新的統一比賽記錄組件
import MatchRecordFormView from '@/views/match/MatchRecordFormView.vue'

const routes = [
  {
    path: '/',
    name: 'Leaderboard',
    component: LeaderboardView
  },
  {
    path: '/detail-leaderboard',
    name: 'DetailLeaderboard',
    component: DetailLeaderboardView
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { guestOnly: true }
  },
  {
    path: '/profile/edit',
    name: 'EditProfile',
    component: Dashboard,
    meta: { requiresAuth: true }
  },

  // === 🔧 新的統一比賽記錄路由 ===
  {
    path: '/match-records/create',
    name: 'RecordMatch',
    component: MatchRecordFormView,
    props: { mode: 'add' },
    meta: { requiresAuth: true }
  },
  {
    path: '/match-records/view/:id',
    name: 'ViewMatch',
    component: MatchRecordFormView,
    props: route => ({
      mode: 'view',
      matchId: route.params.id
    }),
    meta: { requiresAuth: true }
  },
  {
    path: '/match-records/edit/:id',
    name: 'EditMatch',
    component: MatchRecordFormView,
    props: route => ({
      mode: 'edit',
      matchId: route.params.id
    }),
    meta: {
      requiresAuth: true,
      requiresManagement: true // 🔧 只有幹部以上可以編輯
    }
  },

  // === 比賽管理路由 ===
  {
    path: '/matches/management',
    name: 'MatchManagement',
    component: MatchManagementView,
    meta: { requiresAuth: true }
  },

  // === 團隊管理相關路由 ===
  {
    path: '/management',
    name: 'ManagementCenter',
    component: ManagementCenterView,
    meta: {
      requiresAuth: true,
      requiresManagement: true
    }
  },
  {
    path: '/members/add',
    name: 'AddMember',
    component: AddMemberView,
    meta: {
      requiresAuth: true,
      requiresManagement: true
    }
  },
  {
    path: '/members/edit/:id',
    name: 'EditMember',
    component: EditMemberView,
    props: true,
    meta: {
      requiresAuth: true,
      requiresManagement: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 🔧 路由守衛 - 權限檢查
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 檢查是否需要登入
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
    return
  }

  // 檢查是否需要管理權限
  if (to.meta.requiresManagement) {
    if (!authStore.isAuthenticated) {
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 🔧 檢查管理權限：幹部、教練、管理員
    if (!authStore.isCadre && !authStore.isAdmin && !authStore.isCoach) {
      // 沒有管理權限，顯示錯誤訊息並重定向到比賽管理頁面
      next({
        name: 'MatchManagement',
        query: { error: 'insufficient_permissions' }
      })
      return
    }
  }

  // 訪客專用頁面檢查
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    next({ name: 'Leaderboard' })
    return
  }

  next()
})

export default router
