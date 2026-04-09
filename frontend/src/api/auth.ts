import http from './http'

export interface UserInfo {
  id: number
  username: string
  email: string | null
  role: string
  is_approved: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export const apiLogin = (username: string, password: string) =>
  http.post<any, TokenResponse>('/auth/login', { username, password })

export const apiRegister = (data: { username: string; password: string; email?: string }) =>
  http.post<any, { message: string }>('/auth/register', data)

export const apiGetMe = () => http.get<any, UserInfo>('/auth/me')

export const apiListUsers = (approved?: boolean) =>
  http.get<any, UserInfo[]>('/admin/users', { params: approved !== undefined ? { approved } : {} })

export const apiApproveUser = (userId: number) =>
  http.post<any, { message: string }>(`/admin/users/${userId}/approve`)

export const apiUpdateRole = (userId: number, role: string) =>
  http.put<any, { message: string }>(`/admin/users/${userId}/role`, { role })
