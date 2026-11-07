import {createRouter, createWebHistory} from 'vue-router'

const routes = [
    {path: '/', redirect: '/chat'},
    {
        path: '/chat',
        name: 'Chat',
        component: () => import('../views/ChatView.vue'),
    },
    // 后续 Tasks / Approvals / Traces 预留
    // { path: '/tasks', component: () => import('../views/TasksView.vue') },
]

export default createRouter({
    history: createWebHistory(),
    routes,
})