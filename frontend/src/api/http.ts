import axios from 'axios'
import { message } from 'ant-design-vue'

const http = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// 请求拦截：注入 JWT
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一错误处理
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err.response?.status
    const detail = err.response?.data?.detail || err.message

    if (status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    } else if (status === 403) {
      message.error(detail || '权限不足')
    } else {
      message.error(detail || '请求失败')
    }
    return Promise.reject(err)
  }
)

export default http
