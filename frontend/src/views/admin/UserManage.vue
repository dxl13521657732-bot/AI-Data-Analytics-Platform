<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { apiListUsers, apiApproveUser, apiUpdateRole } from '@/api/auth'
import type { UserInfo } from '@/api/auth'
import dayjs from 'dayjs'

const activeTab = ref('pending')
const pendingUsers = ref<UserInfo[]>([])
const allUsers = ref<UserInfo[]>([])
const loading = ref(false)

async function loadUsers() {
  loading.value = true
  try {
    const [pending, all] = await Promise.all([
      apiListUsers(false),
      apiListUsers(),
    ])
    pendingUsers.value = pending
    allUsers.value = all
  } finally {
    loading.value = false
  }
}

async function approve(userId: number) {
  await apiApproveUser(userId)
  message.success('已审批通过')
  await loadUsers()
}

async function changeRole(userId: number, role: string) {
  await apiUpdateRole(userId, role)
  message.success('角色已更新')
  await loadUsers()
}

const pendingColumns = [
  { title: '用户名', dataIndex: 'username' },
  { title: '邮箱', dataIndex: 'email' },
  { title: '注册时间', dataIndex: 'created_at', customRender: ({ text }: any) => dayjs(text).format('YYYY-MM-DD HH:mm') },
  { title: '操作', key: 'action', width: 100 },
]

const allColumns = [
  { title: '用户名', dataIndex: 'username' },
  { title: '邮箱', dataIndex: 'email' },
  { title: '角色', dataIndex: 'role', key: 'role' },
  { title: '状态', dataIndex: 'is_approved', key: 'status' },
  { title: '注册时间', dataIndex: 'created_at', customRender: ({ text }: any) => dayjs(text).format('YYYY-MM-DD HH:mm') },
  { title: '操作', key: 'action', width: 200 },
]

onMounted(loadUsers)
</script>

<template>
  <div>
    <h2 style="margin-bottom:16px">用户管理</h2>

    <a-tabs v-model:activeKey="activeTab">
      <a-tab-pane key="pending" :tab="`待审批 (${pendingUsers.length})`">
        <a-table
          :columns="pendingColumns"
          :data-source="pendingUsers"
          :loading="loading"
          row-key="id"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-button type="primary" size="small" @click="approve(record.id)">审批通过</a-button>
            </template>
          </template>
        </a-table>
      </a-tab-pane>

      <a-tab-pane key="all" tab="全部用户">
        <a-table
          :columns="allColumns"
          :data-source="allUsers"
          :loading="loading"
          row-key="id"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'role'">
              <a-tag :color="record.role === 'admin' ? 'gold' : record.role === 'editor' ? 'blue' : 'default'">
                {{ record.role }}
              </a-tag>
            </template>
            <template v-else-if="column.key === 'status'">
              <a-tag :color="record.is_approved ? 'success' : 'warning'">
                {{ record.is_approved ? '已审批' : '待审批' }}
              </a-tag>
            </template>
            <template v-else-if="column.key === 'action'">
              <a-space>
                <a-select
                  :value="record.role"
                  size="small"
                  style="width:100px"
                  @change="(v: string) => changeRole(record.id, v)"
                >
                  <a-select-option value="admin">admin</a-select-option>
                  <a-select-option value="editor">editor</a-select-option>
                  <a-select-option value="viewer">viewer</a-select-option>
                </a-select>
                <a-button v-if="!record.is_approved" type="link" size="small" @click="approve(record.id)">
                  审批
                </a-button>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>
