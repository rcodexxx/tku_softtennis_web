// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LeaderboardView from '../views/LeaderboardView.vue'
import AddMemberView from "../views/AddMemberView.vue";
// import RecordMatchView from '../views/RecordMatchView.vue'

const routes = [
  {
    path: '/',
    name: 'Leaderboard',
    component: LeaderboardView
  },
  {
    path: '/members/add',
    name: 'AddMember',
    component: AddMemberView
  }
  // {
  //   path: '/match/record',
  //   name: 'RecordMatch',
  //   component: RecordMatchView
  // }
  // 您可以加入其他路由
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router