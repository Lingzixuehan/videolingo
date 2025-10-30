import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router';
import { useUserStore } from '../store/user';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/home' },
  { path: '/login', name: 'login', component: () => import('../pages/Login.vue') },
  {
    path: '/',
    component: () => import('../layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '/home', name: 'home', component: () => import('../pages/Home.vue') },
      { path: '/player', name: 'player', component: () => import('../pages/Player.vue') },
      { path: '/downloads', name: 'downloads', component: () => import('../pages/Downloads.vue') },
      { path: '/settings', name: 'settings', component: () => import('../pages/Settings.vue') }
    ]
  },
  { path: '/:pathMatch(.*)*', name: '404', component: () => import('../pages/NotFound.vue') }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

router.beforeEach((to) => {
  const user = useUserStore();
  if (to.meta?.requiresAuth && !user.token) {
    return { path: '/login', query: { redirect: to.fullPath } };
  }
  if (to.path === '/login' && user.token) {
    return { path: '/home' };
  }
  return true;
});

export default router;