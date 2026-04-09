import http from './http'

export interface TableRef { db: string; table: string }
export interface SQLResult {
  columns: string[]
  rows: any[][]
  row_count: number
  elapsed_ms: number
}

export const apiExecuteSQL = (sql: string, database: string, limit = 5000) =>
  http.post<any, SQLResult>('/analytics/execute', { sql, database, limit })

export async function* streamGenerateSQL(
  tables: TableRef[],
  user_request: string,
  history?: Array<{ role: string; content: string }>
): AsyncGenerator<{ type: string; content?: string }> {
  const token = localStorage.getItem('token')
  const response = await fetch('/api/analytics/generate-sql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ tables, user_request, history }),
  })

  if (!response.ok) {
    throw new Error(`AI 请求失败：${response.status}`)
  }

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          yield JSON.parse(line.slice(6))
        } catch {
          // ignore malformed lines
        }
      }
    }
  }
}
