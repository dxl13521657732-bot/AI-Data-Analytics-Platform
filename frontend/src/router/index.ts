import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        {
          path: '',
          redirect: '/metadata',
        },
        {
          path: 'metadata',
          name: 'Metadata',
          component: () => import('@/views/metadata/MetadataExplorer.vue'),
        },
        {
          path: 'analytics',
          name: 'Analytics',
          component: () => import('@/views/analytics/AnalyticsWorkbench.vue'),
        },
        {
          path: 'mapping',
          name: 'Mapping',
          component: () => import('@/views/mapping/MappingPage.vue'),
        },
        {
          path: 'admin/users',
          name: 'UserManage',
          component: () => import('@/views/admin/UserManage.vue'),
          meta: { requireRole: 'admin' },
        },
      ],
    },
  ],
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    next()
    return
  }
  if (!auth.token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  if (to.meta.requireRole && auth.user?.role !== to.meta.requireRole) {
    next({ path: '/' })
    return
  }
  next()
})

export default router
