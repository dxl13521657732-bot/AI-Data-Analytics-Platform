# AI 数据分析平台

> 智能元数据查询 · 自然语言生成 SQL · 业务系统表映射

## 功能模块

| 模块 | 描述 |
|------|------|
| **元数据查询** | 浏览 Hive / StarRocks 数据库的表结构、字段、DDL |
| **AI 指标提取** | 选择数据表，用自然语言描述需求，AI 自动生成 SQL，执行查询并导出 Excel |
| **系统表映射** | 维护"业务系统 → 功能模块 → 底层数据表"多层映射关系，支持多人协作 |

## 技术栈

- **后端**：FastAPI + SQLAlchemy (SQLite) + PyMySQL (StarRocks) + Anthropic Claude API
- **前端**：Vue 3 + Vite + Ant Design Vue + Pinia
- **部署**：Docker + docker-compose + GitHub Actions

## 快速开始

### 本地开发

**后端**
```bash
cd backend
cp .env.example .env      # 填写配置（StarRocks、Anthropic Key 等）
pip install -r requirements.txt
uvicorn main:app --reload
# 访问 http://localhost:8000/docs 查看 API 文档
```

**前端**
```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### Docker 部署

```bash
# 复制并填写配置
cp backend/.env.example backend/.env
vim backend/.env

# 一键启动
docker-compose up -d

# 访问 http://服务器IP
```

## 配置说明

编辑 `backend/.env`，填写以下关键配置：

| 配置项 | 说明 |
|--------|------|
| `APP_SECRET_KEY` | JWT 签名密钥（随机字符串，至少 32 位） |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key |
| `STARROCKS_HOST` / `PORT` / `USER` / `PASSWORD` | StarRocks 只读连接信息 |
| `TDATA_API_BASE` / `TDATA_API_TOKEN` | 公司数据平台 API（用于 Hive 元数据查询） |

## 适配公司数据平台 API

如果公司数据平台 API 路径与默认不一致，需修改 `backend/services/metadata_service.py` 中的以下方法：

- `_hive_list_databases()` — 获取 Hive 库列表
- `_hive_search_tables()` — 搜索 Hive 表
- `_hive_get_table_detail()` — 获取 Hive 表字段

每个方法都有详细注释说明如何适配。

## 用户权限

| 角色 | 元数据 | AI 查询 | 映射查看 | 映射编辑 | 用户管理 |
|------|--------|---------|---------|---------|---------|
| admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| editor | ✓ | ✓ | ✓ | ✓ | ✗ |
| viewer | ✓ | ✓ | ✓ | ✗ | ✗ |

> 第一个注册的用户自动成为 admin 并直接审批通过。后续用户注册需管理员审批。

## 目录结构

```
AI-Data-Analytics-Platform/
├── backend/          # FastAPI 后端
│   ├── api/          # 路由层
│   ├── core/         # 数据库、认证、依赖注入
│   ├── models/       # SQLAlchemy 模型
│   ├── schemas/      # Pydantic 数据模型
│   ├── services/     # 业务逻辑层（元数据/StarRocks/AI）
│   └── prompts/      # AI 提示词模板
├── frontend/         # Vue 3 前端
│   └── src/
│       ├── views/    # 页面组件
│       ├── api/      # API 调用封装
│       ├── stores/   # Pinia 状态管理
│       └── router/   # 路由配置
└── docker-compose.yml
```
