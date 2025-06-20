// src/router/index.js - 添加裁判模式路由
import { createRouter, createWebHistory } from 'vue-router'

// 導入您的所有視圖組件
import LeaderboardView from '../views/LeaderboardView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import EditProfileView from '../views/EditProfileView.vue'
import ManagementCenterView from '@/views/team/ManagementCenterView.vue'
import AddMemberView from '../views/team/AddMemberView.vue'
import EditMemberView from '@/views/team/EditMemberView.vue'
import AddMatchRecordView from '../views/match/AddMatchRecordView.vue'
import MatchManagementView from '@/views/match/MatchManagementView.vue'
import EditMatchRecordView from '../views/match/EditMatchRecordView.vue'
import DetailLeaderboardView from '@/views/DetailLeaderboardView.vue'
import RefereeModeView from '../views/match/RefereeModeView.vue' // 🎾 新增裁判模式

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
    component: EditProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/match-records/create',
    name: 'RecordMatch',
    component: AddMatchRecordView,
    meta: { requiresAuth: true }
  },
  {
    path: '/match-records/edit/:id',
    name: 'EditMatch',
    component: EditMatchRecordView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/matches/management',
    name: 'MatchManagement',
    component: MatchManagementView,
    meta: { requiresAuth: true }
  },
  // 🎾 新增裁判模式路由
  // {
  //   path: '/referee-mode',
  //   name: 'RefereeMode',
  //   component: RefereeModeView,
  //   meta: {
  //     requiresAuth: true,
  //     mobileOptimized: true
  //   },
  //   beforeEnter: (to, from, next) => {
  //     // 檢查裝置支援 - 僅在非開發環境檢查
  //     if (import.meta.env.PROD) {
  //       const isDesktop = window.innerWidth > 1024 && !('ontouchstart' in window)
  //       if (isDesktop) {
  //         alert('裁判模式專為行動裝置設計，請使用手機或平板訪問')
  //         next({ name: 'Leaderboard' })
  //         return
  //       }
  //     }
  //     next()
  //   }
  // },
  // --- 管理相關路由 ---
  {
    path: '/management',
    name: 'ManagementCenter',
    component: ManagementCenterView,
    meta: { requiresAuth: true }
  },
  {
    path: '/members/add',
    name: 'AddMember',
    component: AddMemberView,
    meta: { requiresAuth: true }
  },
  {
    path: '/members/edit/:id',
    name: 'EditMember',
    component: EditMemberView,
    props: true,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
