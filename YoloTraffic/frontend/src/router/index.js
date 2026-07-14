import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('@/views/LoginView.vue') },
  {
    path: '/app',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/app/chat',
    children: [
      { path: 'chat',      component: () => import('@/views/ChatPage.vue') },
      { path: 'training',  component: () => import('@/views/TrainingPage.vue') },
      { path: 'detection', component: () => import('@/views/DetectionPage.vue') },
      { path: 'dashboard', component: () => import('@/views/DashboardPage.vue') },
      { path: 'history',   component: () => import('@/views/HistoryPage.vue') },
      { path: 'settings',  component: () => import('@/views/SettingsPage.vue') }
    ]
  }
]

export default createRouter({ history: createWebHashHistory(), routes })
