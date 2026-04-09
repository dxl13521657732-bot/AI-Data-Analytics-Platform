<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { apiRegister } from '@/api/auth'

const router = useRouter()
const loading = ref(false)
const registered = ref(false)
const form = reactive({ username: '', password: '', confirmPassword: '', email: '' })

async function handleRegister() {
  if (!form.username || !form.password) {
    message.warning('请填写用户名和密码')
    return
  }
  if (form.password !== form.confirmPassword) {
    message.error('两次密码不一致')
    return
  }
  loading.value = true
  try {
    const res = await apiRegister({
      username: form.username,
      password: form.password,
      email: form.email || undefined,
    })
    message.success(res.message)
    registered.value = true
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <div class="register-header">
        <h1>注册账号</h1>
        <p>AI 数据分析平台</p>
      </div>

      <template v-if="!registered">
        <a-form layout="vertical" @finish="handleRegister">
          <a-form-item label="用户名" required>
            <a-input v-model:value="form.username" size="large" placeholder="3-50 个字符" />
          </a-form-item>
          <a-form-item label="邮箱（选填）">
            <a-input v-model:value="form.email" size="large" placeholder="your@email.com" />
          </a-form-item>
          <a-form-item label="密码" required>
            <a-input-password v-model:value="form.password" size="large" placeholder="至少 6 位" />
          </a-form-item>
          <a-form-item label="确认密码" required>
            <a-input-password v-model:value="form.confirmPassword" size="large" placeholder="再次输入密码" />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" html-type="submit" size="large" block :loading="loading">
              注册
            </a-button>
          </a-form-item>
        </a-form>
      </template>

      <template v-else>
        <a-result status="success" title="注册成功" sub-title="请等待管理员审批，审批通过后即可登录">
          <template #extra>
            <a-button type="primary" @click="$router.push('/login')">返回登录</a-button>
          </template>
        </a-result>
      </template>

      <div class="register-footer" v-if="!registered">
        已有账号？<a @click="$router.push('/login')">立即登录</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.register-card {
  width: 440px;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.register-header {
  text-align: center;
  margin-bottom: 28px;
}
.register-header h1 { font-size: 22px; color: #1a1a1a; margin-bottom: 4px; }
.register-header p { font-size: 13px; color: #888; }
.register-footer { text-align: center; margin-top: 16px; font-size: 14px; color: #666; }
.register-footer a { color: #1677ff; cursor: pointer; }
</style>
