import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore.js'

const STAFF = ['admin', 'coach', 'cadre']

/**
 * meta：
 * - requiresAuth：需要登入
 * - roles：只有這些角色能進入（隱含 requiresAuth）
 * - guestOnly：已登入時導回首頁
 * - fullscreen：不顯示側邊欄與底部分頁列
 * - beta：開發中的功能
 */
const routes = [
  {
    path: '/',
    name: 'Leaderboard',
    component: () => import('@/views/leaderboard/LeaderboardView.vue')
  },
  {
    path: '/detail-leaderboard',
    name: 'DetailLeaderboard',
    component: () => import('@/views/leaderboard/DetailLeaderboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true, fullscreen: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { guestOnly: true, fullscreen: true }
  },
  {
    path: '/profile/edit',
    name: 'EditProfile',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/match-records/create',
    name: 'RecordMatch',
    component: () => import('@/views/match/MatchWizardView.vue'),
    props: { mode: 'add' },
    meta: { roles: STAFF }
  },
  {
    path: '/match-records/batch',
    name: 'BatchRecordMatch',
    component: () => import('@/views/match/BatchRecordView.vue'),
    meta: { roles: STAFF }
  },
  {
    path: '/match-records/view/:id',
    name: 'ViewMatch',
    component: () => import('@/views/match/MatchDetailView.vue'),
    props: route => ({ matchId: route.params.id }),
    meta: { requiresAuth: true }
  },
  {
    path: '/match-records/edit/:id',
    name: 'EditMatch',
    component: () => import('@/views/match/MatchWizardView.vue'),
    props: route => ({ mode: 'edit', matchId: route.params.id }),
    meta: { roles: STAFF }
  },
  {
    path: '/referee',
    name: 'RefereeMode',
    component: () => import('@/views/match/RefereeModeView.vue'),
    meta: { roles: STAFF, fullscreen: true, beta: true }
  },
  {
    path: '/matches/management',
    name: 'MatchManagement',
    component: () => import('@/views/match/MatchManagementCenterView.vue'),
    meta: { roles: STAFF }
  },
  {
    path: '/management',
    name: 'ManagementCenter',
    component: () => import('@/views/team/TeamManagementCenterView.vue'),
    meta: { roles: STAFF }
  },
  {
    path: '/management/members/add',
    name: 'AddMember',
    component: () => import('@/views/team/MemberFormView.vue'),
    props: { mode: 'add' },
    meta: { roles: STAFF }
  },
  {
    path: '/management/seasons/new',
    name: 'NewSeason',
    component: () => import('@/views/team/NewSeasonView.vue'),
    meta: { roles: ['admin'] }
  },
  {
    path: '/management/members/edit/:id',
    name: 'EditMember',
    component: () => import('@/views/team/MemberFormView.vue'),
    props: route => ({ mode: 'edit', id: route.params.id }),
    meta: { roles: STAFF }
  },
  { path: '/:pathMatch(.*)*', redirect: { name: 'Leaderboard' } }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach(to => {
  const authStore = useAuthStore()
  const roles = to.meta.roles
  const needsLogin = to.meta.requiresAuth || Boolean(roles)

  if (needsLogin && !authStore.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
  if (roles && !roles.includes(authStore.userRole)) {
    return { name: 'Leaderboard' }
  }
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { name: 'Leaderboard' }
  }
})

export default router
