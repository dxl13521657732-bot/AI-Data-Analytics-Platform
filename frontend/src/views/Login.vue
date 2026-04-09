<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const loading = ref(false)

const form = reactive({ username: '', password: '' })

async function handleLogin() {
  if (!form.username || !form.password) {
    message.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err: any) {
    // 错误已由 axios 拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>AI 数据分析平台</h1>
        <p>智能元数据查询 · 自然语言生成 SQL · 业务系统表映射</p>
      </div>
      <a-form layout="vertical" @finish="handleLogin">
        <a-form-item label="用户名">
          <a-input v-model:value="form.username" size="large" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="密码">
          <a-input-password v-model:value="form.password" size="large" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" size="large" block :loading="loading" @click="handleLogin">
            登录
          </a-button>
        </a-form-item>
      </a-form>
      <div class="login-footer">
        还没有账号？<a @click="$router.push('/register')">立即注册</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 420px;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.login-header h1 {
  font-size: 22px;
  color: #1a1a1a;
  margin-bottom: 8px;
}
.login-header p {
  font-size: 13px;
  color: #888;
}
.login-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #666;
}
.login-footer a {
  color: #1677ff;
  cursor: pointer;
}
</style>
