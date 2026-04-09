<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  DatabaseOutlined,
  RobotOutlined,
  ApartmentOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

onMounted(() => auth.fetchMe())

const selectedKeys = computed(() => {
  const path = route.path
  if (path.startsWith('/metadata')) return ['metadata']
  if (path.startsWith('/analytics')) return ['analytics']
  if (path.startsWith('/mapping')) return ['mapping']
  if (path.startsWith('/admin')) return ['admin-users']
  return ['metadata']
})

function navigate(key: string) {
  const paths: Record<string, string> = {
    metadata: '/metadata',
    analytics: '/analytics',
    mapping: '/mapping',
    'admin-users': '/admin/users',
  }
  router.push(paths[key] ?? '/')
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider theme="dark" :collapsed-width="64" collapsible>
      <div class="logo">
        <span class="logo-text">AI 数据平台</span>
      </div>
      <a-menu
        theme="dark"
        mode="inline"
        :selected-keys="selectedKeys"
        @click="(info: { key: string }) => navigate(info.key)"
      >
        <a-menu-item key="metadata">
          <database-outlined />
          <span>元数据查询</span>
        </a-menu-item>
        <a-menu-item key="analytics">
          <robot-outlined />
          <span>AI 指标提取</span>
        </a-menu-item>
        <a-menu-item key="mapping">
          <apartment-outlined />
          <span>系统表映射</span>
        </a-menu-item>
        <a-menu-item v-if="auth.isAdmin" key="admin-users">
          <user-outlined />
          <span>用户管理</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <a-layout>
      <a-layout-header class="header">
        <div class="header-right">
          <a-space>
            <span class="username">{{ auth.user?.username }}</span>
            <a-tag :color="auth.user?.role === 'admin' ? 'gold' : auth.user?.role === 'editor' ? 'blue' : 'default'">
              {{ auth.user?.role }}
            </a-tag>
            <a-button type="text" @click="logout">
              <logout-outlined /> 退出
            </a-button>
          </a-space>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
}
.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
}
.header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}
.header-right { display: flex; align-items: center; }
.username { color: #555; font-size: 14px; }
.content {
  margin: 24px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  min-height: calc(100vh - 112px);
}
</style>
