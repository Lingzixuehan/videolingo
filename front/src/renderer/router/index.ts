import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router';
import AppLayout from '../layouts/AppLayout.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../pages/Login.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../pages/Home.vue'),
        meta: { title: '概览' },
      },
      {
        path: 'videos',
        name: 'videos',
        component: () => import('../pages/Videos.vue'),
        meta: { title: '我的视频' },
      },
      {
        path: 'player/:id',
        name: 'player',
        component: () => import('../pages/Player.vue'),
        meta: { title: '视频学习' },
      },
      {
        path: 'study/review',
        name: 'study-review',
        component: () => import('../pages/Review.vue'),
        meta: { title: '学习复习' },
      },
      {
        path: 'study/cards',
        name: 'study-cards',
        component: () => import('../pages/Analyze.vue'), // 先临时占位，后面再换成真正的卡片管理页
        meta: { title: '卡片管理' },
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('../pages/Settings.vue'),
        meta: { title: '设置' },
      },
      {
        path: 'settings/profile',
        name: 'settings-profile',
        component: () => import('../pages/Settings.vue'), // 先共用 Settings 页，后面再拆
        meta: { title: '个人资料' },
      },
      {
        path: 'settings/plan',
        name: 'settings-plan',
        component: () => import('../pages/Tasks.vue'), // 先复用 Tasks 页面当作计划页骨架
        meta: { title: '学习计划' },
      },
      {
        path: 'settings/privacy',
        name: 'settings-privacy',
        component: () => import('../pages/Downloads.vue'), // 临时当隐私/数据导出占位
        meta: { title: '数据与隐私' },
      },
      {
        path: 'subtitles',
        name: 'subtitles',
        component: () => import('../pages/Subtitles.vue'),
        meta: { title: '字幕管理' },
      },
      {
        path: 'analyze',
        name: 'analyze',
        component: () => import('../pages/Analyze.vue'),
        meta: { title: '学习分析' },
      },
      {
        path: 'review',
        redirect: { name: 'study-review' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../pages/NotFound.vue'),
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// 这里可以后续加路由守卫（如未登录跳转登录）

export default router;
