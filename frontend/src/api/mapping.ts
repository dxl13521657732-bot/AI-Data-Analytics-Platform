import http from './http'

export interface TableMappingOut {
  id: number; module_id: number; data_source: string; database_name: string; table_name: string; remark?: string
}
export interface FunctionModuleOut {
  id: number; system_id: number; name: string; description?: string; table_mappings: TableMappingOut[]
}
export interface BusinessSystemOut {
  id: number; name: string; description?: string; owner?: string; created_at: string; modules: FunctionModuleOut[]
}
export interface BusinessSystemListItem {
  id: number; name: string; description?: string; owner?: string; created_at: string; module_count: number
}

// 业务系统
export const apiListSystems = () => http.get<any, BusinessSystemListItem[]>('/mapping/systems')
export const apiGetSystem = (id: number) => http.get<any, BusinessSystemOut>(`/mapping/systems/${id}`)
export const apiCreateSystem = (data: { name: string; description?: string; owner?: string }) =>
  http.post<any, BusinessSystemOut>('/mapping/systems', data)
export const apiUpdateSystem = (id: number, data: Partial<{ name: string; description: string; owner: string }>) =>
  http.put<any, BusinessSystemOut>(`/mapping/systems/${id}`, data)
export const apiDeleteSystem = (id: number) => http.delete(`/mapping/systems/${id}`)

// 功能模块
export const apiCreateModule = (systemId: number, data: { name: string; description?: string }) =>
  http.post<any, FunctionModuleOut>(`/mapping/systems/${systemId}/modules`, data)
export const apiUpdateModule = (id: number, data: Partial<{ name: string; description: string }>) =>
  http.put<any, FunctionModuleOut>(`/mapping/modules/${id}`, data)
export const apiDeleteModule = (id: number) => http.delete(`/mapping/modules/${id}`)

// 底层表映射
export const apiCreateTableMapping = (moduleId: number, data: { data_source: string; database_name: string; table_name: string; remark?: string }) =>
  http.post<any, TableMappingOut>(`/mapping/modules/${moduleId}/tables`, data)
export const apiUpdateTableMapping = (id: number, data: Partial<{ data_source: string; database_name: string; table_name: string; remark: string }>) =>
  http.put<any, TableMappingOut>(`/mapping/tables/${id}`, data)
export const apiDeleteTableMapping = (id: number) => http.delete(`/mapping/tables/${id}`)
