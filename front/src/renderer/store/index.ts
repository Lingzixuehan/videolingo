const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('../pages/Login.vue') },
    {
      path: '/',
      component: () => import('../layouts/AppLayout.vue'),
      children: [
        { path: '', name: 'Home', component: () => import('../pages/Home.vue') },
        { path: 'videos', name: 'Videos', component: () => import('../pages/Videos.vue') },
        { path: 'tasks', name: 'Tasks', component: () => import('../pages/Tasks.vue') },
        { path: 'subtitles', name: 'Subtitles', component: () => import('../pages/Subtitles.vue') },
        { path: 'player', name: 'Player', component: () => import('../pages/Player.vue') },
        { path: 'review', name: 'Review', component: () => import('../pages/Review.vue') },
        { path: 'analyze', name: 'Analyze', component: () => import('../pages/Analyze.vue') },
        { path: 'settings', name: 'Settings', component: () => import('../pages/Settings.vue') }
      ]
    },
    { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('../pages/NotFound.vue') }
  ]
});

import { useUserStore } from '../store/user';
const publicPaths = new Set(['/login', '/404']);
router.beforeEach((to) => {
  const user = useUserStore();
  if (!user.isAuthed && !publicPaths.has(to.path)) return '/login';
});
export default router;