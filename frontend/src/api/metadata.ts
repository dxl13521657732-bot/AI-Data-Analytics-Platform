import http from './http'

export interface DataSourceItem { key: string; label: string }
export interface DatabaseItem { name: string }
export interface TableItem { database: string; name: string; comment?: string }
export interface ColumnItem { name: string; type: string; comment?: string; nullable?: boolean }
export interface TableDetail { database: string; table: string; ddl?: string; columns: ColumnItem[] }

export const apiGetSources = () => http.get<any, DataSourceItem[]>('/metadata/sources')
export const apiGetDatabases = (source: string) =>
  http.get<any, DatabaseItem[]>('/metadata/databases', { params: { source } })
export const apiSearchTables = (source: string, db: string, keyword?: string) =>
  http.get<any, TableItem[]>('/metadata/tables', { params: { source, db, keyword } })
export const apiGetColumns = (source: string, db: string, table: string) =>
  http.get<any, TableDetail>('/metadata/columns', { params: { source, db, table } })
