<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import {
  apiListSystems, apiGetSystem, apiCreateSystem, apiUpdateSystem, apiDeleteSystem,
  apiCreateModule, apiUpdateModule, apiDeleteModule,
  apiCreateTableMapping, apiUpdateTableMapping, apiDeleteTableMapping,
} from '@/api/mapping'
import type { BusinessSystemListItem, BusinessSystemOut, FunctionModuleOut, TableMappingOut } from '@/api/mapping'

const auth = useAuthStore()

// ─── 左侧：业务系统列表 ────────────────────────────────────────────────
const systems = ref<BusinessSystemListItem[]>([])
const loadingSystems = ref(false)
const selectedSystemId = ref<number | null>(null)
const currentSystem = ref<BusinessSystemOut | null>(null)
const selectedModuleId = ref<number | null>(null)

async function loadSystems() {
  loadingSystems.value = true
  try {
    systems.value = await apiListSystems()
  } finally {
    loadingSystems.value = false
  }
}

async function selectSystem(id: number) {
  selectedSystemId.value = id
  selectedModuleId.value = null
  currentSystem.value = await apiGetSystem(id)
}

// ─── 业务系统 CRUD ────────────────────────────────────────────────────
const sysModal = ref({ visible: false, editing: false, form: { name: '', description: '', owner: '' } })

function openCreateSystem() {
  sysModal.value = { visible: true, editing: false, form: { name: '', description: '', owner: '' } }
}

function openEditSystem(sys: BusinessSystemListItem) {
  sysModal.value = { visible: true, editing: true, form: { name: sys.name, description: sys.description ?? '', owner: sys.owner ?? '' } }
}

async function saveSystem() {
  const f = sysModal.value.form
  if (!f.name.trim()) { message.error('请输入系统名称'); return }
  if (sysModal.value.editing && selectedSystemId.value) {
    await apiUpdateSystem(selectedSystemId.value, f)
  } else {
    await apiCreateSystem(f)
  }
  sysModal.value.visible = false
  await loadSystems()
  if (selectedSystemId.value) selectSystem(selectedSystemId.value)
}

async function deleteSystem(id: number) {
  Modal.confirm({
    title: '确认删除此业务系统？',
    content: '删除后，该系统下所有功能模块和表映射将一并删除，不可恢复。',
    onOk: async () => {
      await apiDeleteSystem(id)
      systems.value = systems.value.filter(s => s.id !== id)
      if (selectedSystemId.value === id) { selectedSystemId.value = null; currentSystem.value = null }
    }
  })
}

// ─── 功能模块 CRUD ───────────────────────────────────────────────────
const modModal = ref({ visible: false, editing: false, editId: 0, form: { name: '', description: '' } })

function openCreateModule() {
  modModal.value = { visible: true, editing: false, editId: 0, form: { name: '', description: '' } }
}

function openEditModule(mod: FunctionModuleOut) {
  modModal.value = { visible: true, editing: true, editId: mod.id, form: { name: mod.name, description: mod.description ?? '' } }
}

async function saveModule() {
  const f = modModal.value.form
  if (!f.name.trim()) { message.error('请输入模块名称'); return }
  if (modModal.value.editing) {
    await apiUpdateModule(modModal.value.editId, f)
  } else {
    await apiCreateModule(selectedSystemId.value!, f)
  }
  modModal.value.visible = false
  if (selectedSystemId.value) currentSystem.value = await apiGetSystem(selectedSystemId.value)
}

async function deleteModule(id: number) {
  Modal.confirm({
    title: '确认删除此功能模块？',
    onOk: async () => {
      await apiDeleteModule(id)
      if (selectedSystemId.value) currentSystem.value = await apiGetSystem(selectedSystemId.value)
      if (selectedModuleId.value === id) selectedModuleId.value = null
    }
  })
}

// ─── 表映射 CRUD ─────────────────────────────────────────────────────
const tmModal = ref({ visible: false, editing: false, editId: 0, form: { data_source: 'starrocks', database_name: '', table_name: '', remark: '' } })

const currentMappings = ref<TableMappingOut[]>([])

function selectModule(mod: FunctionModuleOut) {
  selectedModuleId.value = mod.id
  currentMappings.value = mod.table_mappings
}

function openCreateTableMapping() {
  if (!selectedModuleId.value) { message.warning('请先选择左侧功能模块'); return }
  tmModal.value = { visible: true, editing: false, editId: 0, form: { data_source: 'starrocks', database_name: '', table_name: '', remark: '' } }
}

function openEditTableMapping(tm: TableMappingOut) {
  tmModal.value = { visible: true, editing: true, editId: tm.id, form: { data_source: tm.data_source, database_name: tm.database_name, table_name: tm.table_name, remark: tm.remark ?? '' } }
}

async function saveTableMapping() {
  const f = tmModal.value.form
  if (!f.database_name || !f.table_name) { message.error('请填写数据库和表名'); return }
  if (tmModal.value.editing) {
    await apiUpdateTableMapping(tmModal.value.editId, f)
  } else {
    await apiCreateTableMapping(selectedModuleId.value!, f)
  }
  tmModal.value.visible = false
  if (selectedSystemId.value) {
    currentSystem.value = await apiGetSystem(selectedSystemId.value)
    const mod = currentSystem.value.modules.find(m => m.id === selectedModuleId.value)
    if (mod) currentMappings.value = mod.table_mappings
  }
}

async function deleteTableMapping(id: number) {
  await apiDeleteTableMapping(id)
  currentMappings.value = currentMappings.value.filter(t => t.id !== id)
}

const tmColumns = [
  { title: '数据源', dataIndex: 'data_source', width: 100 },
  { title: '数据库', dataIndex: 'database_name', width: 160 },
  { title: '表名', dataIndex: 'table_name' },
  { title: '备注', dataIndex: 'remark' },
  { title: '操作', key: 'action', width: 120 },
]

onMounted(loadSystems)
</script>

<template>
  <div>
    <h2 style="margin-bottom:16px">业务系统功能模块与底层表映射</h2>

    <a-row :gutter="16" style="height:calc(100vh - 180px)">
      <!-- 左侧：业务系统树 -->
      <a-col :span="7" style="height:100%;overflow-y:auto">
        <a-card size="small" :body-style="{ padding: 0 }">
          <template #title>
            <a-space>
              <span>业务系统</span>
              <a-button v-if="auth.isEditor" type="link" size="small" @click="openCreateSystem">+ 新建</a-button>
            </a-space>
          </template>
          <a-spin :spinning="loadingSystems">
            <a-list
              size="small"
              :data-source="systems"
            >
              <template #renderItem="{ item }">
                <a-list-item
                  style="cursor:pointer;padding:10px 12px"
                  :class="{ 'selected-item': selectedSystemId === item.id }"
                  @click="selectSystem(item.id)"
                >
                  <div style="width:100%">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                      <span style="font-weight:500">{{ item.name }}</span>
                      <a-space v-if="auth.isEditor">
                        <a-button type="link" size="small" @click.stop="openEditSystem(item)">编辑</a-button>
                        <a-button type="link" size="small" danger @click.stop="deleteSystem(item.id)">删除</a-button>
                      </a-space>
                    </div>
                    <div style="font-size:12px;color:#999;margin-top:2px">
                      {{ item.module_count }} 个功能模块 · {{ item.owner || '未指定负责人' }}
                    </div>
                  </div>
                </a-list-item>
              </template>
            </a-list>
          </a-spin>
        </a-card>

        <!-- 功能模块列表 -->
        <a-card v-if="currentSystem" size="small" style="margin-top:12px" :body-style="{ padding: 0 }">
          <template #title>
            <a-space>
              <span>功能模块 - {{ currentSystem.name }}</span>
              <a-button v-if="auth.isEditor" type="link" size="small" @click="openCreateModule">+ 新建</a-button>
            </a-space>
          </template>
          <a-list size="small" :data-source="currentSystem.modules">
            <template #renderItem="{ item }">
              <a-list-item
                style="cursor:pointer;padding:10px 12px"
                :class="{ 'selected-item': selectedModuleId === item.id }"
                @click="selectModule(item)"
              >
                <div style="width:100%">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span>{{ item.name }}</span>
                    <a-space v-if="auth.isEditor">
                      <a-button type="link" size="small" @click.stop="openEditModule(item)">编辑</a-button>
                      <a-button type="link" size="small" danger @click.stop="deleteModule(item.id)">删除</a-button>
                    </a-space>
                  </div>
                  <div style="font-size:12px;color:#999">{{ item.description }}</div>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>

      <!-- 右侧：底层表映射 -->
      <a-col :span="17">
        <a-card size="small" style="height:100%">
          <template #title>
            <a-space>
              <span>底层表映射{{ selectedModuleId ? ' - ' + currentSystem?.modules.find(m => m.id === selectedModuleId)?.name : '' }}</span>
              <a-button v-if="auth.isEditor && selectedModuleId" type="primary" size="small" @click="openCreateTableMapping">
                + 新增映射
              </a-button>
            </a-space>
          </template>

          <a-table
            v-if="selectedModuleId"
            :columns="tmColumns"
            :data-source="currentMappings"
            size="small"
            row-key="id"
            :pagination="false"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button v-if="auth.isEditor" type="link" size="small" @click="openEditTableMapping(record)">编辑</a-button>
                  <a-button v-if="auth.isEditor" type="link" size="small" danger @click="deleteTableMapping(record.id)">删除</a-button>
                </a-space>
              </template>
            </template>
          </a-table>
          <a-empty v-else description="请选择左侧功能模块查看底层表映射" />
        </a-card>
      </a-col>
    </a-row>

    <!-- 业务系统弹窗 -->
    <a-modal v-model:open="sysModal.visible" :title="sysModal.editing ? '编辑业务系统' : '新建业务系统'" @ok="saveSystem">
      <a-form layout="vertical">
        <a-form-item label="系统名称" required>
          <a-input v-model:value="sysModal.form.name" placeholder="如：ERP 系统" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="sysModal.form.description" :rows="3" />
        </a-form-item>
        <a-form-item label="负责人">
          <a-input v-model:value="sysModal.form.owner" placeholder="负责人姓名" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 功能模块弹窗 -->
    <a-modal v-model:open="modModal.visible" :title="modModal.editing ? '编辑功能模块' : '新建功能模块'" @ok="saveModule">
      <a-form layout="vertical">
        <a-form-item label="模块名称" required>
          <a-input v-model:value="modModal.form.name" placeholder="如：订单管理" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="modModal.form.description" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 表映射弹窗 -->
    <a-modal v-model:open="tmModal.visible" :title="tmModal.editing ? '编辑表映射' : '新增表映射'" @ok="saveTableMapping">
      <a-form layout="vertical">
        <a-form-item label="数据源" required>
          <a-radio-group v-model:value="tmModal.form.data_source">
            <a-radio value="starrocks">StarRocks</a-radio>
            <a-radio value="hive">Hive</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="数据库名" required>
          <a-input v-model:value="tmModal.form.database_name" placeholder="如：ods_sales" />
        </a-form-item>
        <a-form-item label="表名" required>
          <a-input v-model:value="tmModal.form.table_name" placeholder="如：order_detail" />
        </a-form-item>
        <a-form-item label="备注">
          <a-input v-model:value="tmModal.form.remark" placeholder="说明该表在此功能中的作用" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.selected-item { background: #e6f4ff; }
</style>
