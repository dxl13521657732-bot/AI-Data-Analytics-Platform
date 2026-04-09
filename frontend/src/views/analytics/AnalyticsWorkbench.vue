<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import * as XLSX from 'xlsx'
import dayjs from 'dayjs'
import { apiGetDatabases, apiSearchTables } from '@/api/metadata'
import type { TableItem } from '@/api/metadata'
import { streamGenerateSQL, apiExecuteSQL } from '@/api/analytics'
import type { TableRef, SQLResult } from '@/api/analytics'

// ─── 表选择 ──────────────────────────────────────────────────────────
const databases = ref<string[]>([])
const selectedDb = ref('')
const tableList = ref<TableItem[]>([])
const selectedTables = ref<TableRef[]>([])
const loadingTables = ref(false)

async function loadDatabases() {
  const dbs = await apiGetDatabases('starrocks')
  databases.value = dbs.map(d => d.name)
}

async function onDbChange(db: string) {
  loadingTables.value = true
  try {
    tableList.value = await apiSearchTables('starrocks', db)
  } finally {
    loadingTables.value = false
  }
}

function addTable(tableName: string) {
  if (selectedTables.value.find(t => t.db === selectedDb.value && t.table === tableName)) {
    message.warning('该表已添加')
    return
  }
  selectedTables.value.push({ db: selectedDb.value, table: tableName })
}

function removeTable(idx: number) {
  selectedTables.value.splice(idx, 1)
}

loadDatabases()

// ─── AI 生成 SQL ─────────────────────────────────────────────────────
const userRequest = ref('')
const generatedSQL = ref('')
const isGenerating = ref(false)
const history = ref<Array<{ role: string; content: string }>>([])

async function generateSQL() {
  if (!userRequest.value.trim()) { message.warning('请输入需求描述'); return }
  if (selectedTables.value.length === 0) { message.warning('请至少选择一张数据表'); return }

  isGenerating.value = true
  generatedSQL.value = ''

  try {
    const stream = streamGenerateSQL(selectedTables.value, userRequest.value, history.value.length ? history.value : undefined)
    for await (const chunk of stream) {
      if (chunk.type === 'text') {
        generatedSQL.value += chunk.content ?? ''
      } else if (chunk.type === 'done') {
        // 保存到对话历史
        history.value.push({ role: 'user', content: userRequest.value })
        history.value.push({ role: 'assistant', content: generatedSQL.value })
      }
    }
  } catch (err: any) {
    message.error('AI 生成失败：' + err.message)
  } finally {
    isGenerating.value = false
  }
}

function clearHistory() {
  history.value = []
  message.success('对话历史已清除')
}

// ─── 执行 SQL ────────────────────────────────────────────────────────
const sqlToExecute = computed({
  get: () => generatedSQL.value,
  set: (v) => (generatedSQL.value = v),
})
const queryResult = ref<SQLResult | null>(null)
const isExecuting = ref(false)

async function executeSQL() {
  if (!generatedSQL.value.trim()) { message.warning('SQL 为空'); return }
  if (!selectedDb.value) { message.warning('请选择数据库'); return }
  isExecuting.value = true
  try {
    queryResult.value = await apiExecuteSQL(generatedSQL.value, selectedDb.value)
    message.success(`查询完成，共 ${queryResult.value.row_count} 行，耗时 ${queryResult.value.elapsed_ms}ms`)
  } finally {
    isExecuting.value = false
  }
}

// ─── 列定义 ──────────────────────────────────────────────────────────
const tableColumns = computed(() =>
  (queryResult.value?.columns ?? []).map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true,
  }))
)

const tableData = computed(() =>
  (queryResult.value?.rows ?? []).map((row, i) => {
    const obj: Record<string, any> = { _key: i }
    queryResult.value!.columns.forEach((col, j) => { obj[col] = row[j] })
    return obj
  })
)

// ─── 导出 Excel ──────────────────────────────────────────────────────
function exportExcel() {
  if (!queryResult.value) return
  const { columns, rows } = queryResult.value
  const data = [columns, ...rows]
  const ws = XLSX.utils.aoa_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '数据指标')
  XLSX.writeFile(wb, `指标_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`)
}
</script>

<template>
  <div>
    <h2 style="margin-bottom:16px">AI 数据指标提取</h2>

    <a-row :gutter="16">
      <!-- 左侧：表选择 + AI 输入 -->
      <a-col :span="10">
        <!-- 选择数据表 -->
        <a-card size="small" title="第一步：选择数据表">
          <a-row :gutter="8">
            <a-col :span="12">
              <a-select
                v-model:value="selectedDb"
                style="width:100%"
                show-search
                placeholder="选择数据库"
                @change="onDbChange"
              >
                <a-select-option v-for="db in databases" :key="db" :value="db">{{ db }}</a-select-option>
              </a-select>
            </a-col>
            <a-col :span="12">
              <a-select
                style="width:100%"
                show-search
                placeholder="选择数据表"
                :loading="loadingTables"
                :disabled="!selectedDb"
                @change="(v: string) => addTable(v)"
              >
                <a-select-option v-for="t in tableList" :key="t.name" :value="t.name">{{ t.name }}</a-select-option>
              </a-select>
            </a-col>
          </a-row>

          <div style="margin-top:12px">
            <a-tag
              v-for="(t, idx) in selectedTables"
              :key="idx"
              closable
              color="blue"
              style="margin:4px"
              @close="removeTable(idx)"
            >
              {{ t.db }}.{{ t.table }}
            </a-tag>
            <a-empty v-if="selectedTables.length === 0" description="请添加数据表" :image-size="40" />
          </div>
        </a-card>

        <!-- AI 输入 -->
        <a-card size="small" title="第二步：描述需求" style="margin-top:12px">
          <a-textarea
            v-model:value="userRequest"
            placeholder="用自然语言描述你需要的指标，例如：统计最近7天各品类的销售额和订单量，按销售额降序排列"
            :rows="5"
            style="margin-bottom:12px"
          />
          <a-space>
            <a-button type="primary" :loading="isGenerating" @click="generateSQL" :disabled="!userRequest.trim()">
              AI 生成 SQL
            </a-button>
            <a-button v-if="history.length > 0" @click="clearHistory">清除对话历史</a-button>
            <a-tag v-if="history.length > 0" color="orange">多轮对话：{{ history.length / 2 }} 轮</a-tag>
          </a-space>
        </a-card>
      </a-col>

      <!-- 右侧：SQL 编辑 + 结果 -->
      <a-col :span="14">
        <!-- SQL 编辑区 -->
        <a-card size="small" title="SQL 语句">
          <a-textarea
            v-model:value="sqlToExecute"
            :rows="8"
            :placeholder="isGenerating ? 'AI 正在生成 SQL...' : '生成的 SQL 将显示在这里，支持手动编辑'"
            style="font-family: monospace; font-size: 13px"
            :class="{ 'generating': isGenerating }"
          />
          <a-space style="margin-top:12px">
            <a-button
              type="primary"
              :loading="isExecuting"
              :disabled="!generatedSQL.trim()"
              @click="executeSQL"
            >
              执行查询
            </a-button>
            <a-button
              :disabled="!queryResult"
              @click="exportExcel"
            >
              导出 Excel
            </a-button>
            <span v-if="queryResult" style="font-size:12px;color:#888">
              共 {{ queryResult.row_count }} 行 · {{ queryResult.elapsed_ms }}ms
            </span>
          </a-space>
        </a-card>

        <!-- 查询结果 -->
        <a-card size="small" title="查询结果" style="margin-top:12px">
          <a-table
            v-if="queryResult"
            :columns="tableColumns"
            :data-source="tableData"
            size="small"
            :scroll="{ x: 'max-content', y: 400 }"
            row-key="_key"
            :pagination="{ pageSize: 50, showSizeChanger: true, showTotal: (total: number) => `共 ${total} 行` }"
          />
          <a-empty v-else description="执行查询后结果将显示在这里" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<style scoped>
.generating {
  border-color: #1677ff !important;
  animation: blink-border 1s infinite;
}
@keyframes blink-border {
  0%, 100% { border-color: #1677ff; }
  50% { border-color: #91caff; }
}
</style>
