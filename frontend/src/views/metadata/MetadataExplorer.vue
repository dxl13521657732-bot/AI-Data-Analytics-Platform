<script setup lang="ts">
import { ref, watch } from 'vue'
import { apiGetDatabases, apiSearchTables, apiGetColumns } from '@/api/metadata'
import type { TableItem, TableDetail } from '@/api/metadata'

const sources = [
  { key: 'starrocks', label: 'StarRocks' },
  { key: 'hive', label: 'Hive' },
]

const selectedSource = ref('starrocks')
const databases = ref<{ name: string }[]>([])
const selectedDb = ref('')
const keyword = ref('')
const tables = ref<TableItem[]>([])
const selectedTable = ref<TableDetail | null>(null)
const loading = ref(false)
const tableLoading = ref(false)
const detailLoading = ref(false)

async function loadDatabases() {
  loading.value = true
  try {
    databases.value = await apiGetDatabases(selectedSource.value)
    selectedDb.value = ''
    tables.value = []
    selectedTable.value = null
  } finally {
    loading.value = false
  }
}

async function loadTables() {
  if (!selectedDb.value) return
  tableLoading.value = true
  try {
    tables.value = await apiSearchTables(selectedSource.value, selectedDb.value, keyword.value || undefined)
    selectedTable.value = null
  } finally {
    tableLoading.value = false
  }
}

async function showDetail(table: TableItem) {
  detailLoading.value = true
  try {
    selectedTable.value = await apiGetColumns(selectedSource.value, table.database, table.name)
  } finally {
    detailLoading.value = false
  }
}

watch(selectedSource, loadDatabases, { immediate: true })
watch(selectedDb, loadTables)

const columnDefs = [
  { title: '字段名', dataIndex: 'name', key: 'name', width: 180 },
  { title: '类型', dataIndex: 'type', key: 'type', width: 150 },
  { title: '允许空', dataIndex: 'nullable', key: 'nullable', width: 80,
    customRender: ({ text }: any) => text === true ? '是' : text === false ? '否' : '-' },
  { title: '注释', dataIndex: 'comment', key: 'comment' },
]
</script>

<template>
  <div>
    <h2 style="margin-bottom:16px">元数据查询</h2>

    <a-row :gutter="16">
      <!-- 左侧：数据源 + 库 + 表列表 -->
      <a-col :span="8">
        <a-card size="small" title="数据源">
          <a-radio-group v-model:value="selectedSource" button-style="solid">
            <a-radio-button v-for="s in sources" :key="s.key" :value="s.key">{{ s.label }}</a-radio-button>
          </a-radio-group>
        </a-card>

        <a-card size="small" title="选择数据库" style="margin-top:12px">
          <a-spin :spinning="loading">
            <a-select
              v-model:value="selectedDb"
              style="width:100%"
              show-search
              placeholder="请选择数据库"
              @change="loadTables"
            >
              <a-select-option v-for="db in databases" :key="db.name" :value="db.name">
                {{ db.name }}
              </a-select-option>
            </a-select>
          </a-spin>
        </a-card>

        <a-card size="small" title="数据表" style="margin-top:12px">
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索表名"
            @search="loadTables"
            style="margin-bottom:8px"
          />
          <a-spin :spinning="tableLoading">
            <a-list
              size="small"
              :data-source="tables"
              :style="{ maxHeight: '400px', overflowY: 'auto' }"
            >
              <template #renderItem="{ item }">
                <a-list-item
                  style="cursor:pointer;padding:8px 12px"
                  :class="{ 'selected-item': selectedTable?.table === item.name }"
                  @click="showDetail(item)"
                >
                  <span style="font-size:13px">{{ item.name }}</span>
                  <span v-if="item.comment" style="font-size:11px;color:#999;margin-left:8px">{{ item.comment }}</span>
                </a-list-item>
              </template>
            </a-list>
          </a-spin>
        </a-card>
      </a-col>

      <!-- 右侧：表详情 -->
      <a-col :span="16">
        <a-card size="small" :title="selectedTable ? `${selectedTable.database}.${selectedTable.table}` : '表详情'" :loading="detailLoading">
          <template v-if="selectedTable">
            <a-tabs>
              <a-tab-pane key="columns" tab="字段列表">
                <a-table
                  :columns="columnDefs"
                  :data-source="selectedTable.columns"
                  size="small"
                  :pagination="false"
                  row-key="name"
                />
              </a-tab-pane>
              <a-tab-pane key="ddl" tab="DDL">
                <pre style="background:#f5f5f5;padding:12px;border-radius:4px;font-size:12px;white-space:pre-wrap;max-height:500px;overflow-y:auto">{{ selectedTable.ddl || '暂无 DDL 信息' }}</pre>
              </a-tab-pane>
            </a-tabs>
          </template>
          <a-empty v-else description="请选择左侧数据表查看详情" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<style scoped>
.selected-item { background: #e6f4ff; border-radius: 4px; }
</style>
