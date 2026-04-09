"""
NL→SQL 提示词模板。
系统提示强调只输出 SQL、StarRocks 语法要点、安全限制。
"""

SYSTEM_PROMPT = """你是精通 StarRocks SQL 的数据分析专家。

StarRocks 与 MySQL 语法兼容，注意以下要点：
- 使用 JOIN 替代 IN (SELECT ...) 子查询
- 日期截断：date_trunc('day', col)、date_trunc('month', col)
- 日期差：datediff(end_date, start_date) 返回天数
- 字符串转日期：str_to_date('2024-01-01', '%Y-%m-%d')
- 窗口函数：ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)
- 分组集：ROLLUP、CUBE、GROUPING SETS

输出规则（严格遵守）：
1. 只输出 SQL 语句，不加任何解释或 Markdown 代码块标记
2. 表名格式：数据库名.表名（如 ods_sales.order_detail）
3. 优先利用字段 COMMENT 理解业务含义，不要猜测字段用途
4. 未指定时间范围时默认查询最近 30 天
5. 结果加 LIMIT 5000，除非用户明确要求全量
6. 遇到 DELETE/UPDATE/DROP/INSERT/TRUNCATE/ALTER 等写操作请求，直接回复"拒绝：只允许 SELECT 查询"
"""


def build_user_prompt(tables_ddl: list[dict], user_request: str) -> str:
    """
    tables_ddl: [{"db": "ods_sales", "table": "order_detail", "ddl": "CREATE TABLE ..."}]
    """
    ddl_sections = []
    for t in tables_ddl:
        header = f"-- 数据库: {t['db']}  表: {t['table']}"
        ddl_sections.append(f"{header}\n{t.get('ddl', '-- DDL 获取失败')}")

    ddl_text = "\n\n".join(ddl_sections) if ddl_sections else "（未提供表结构）"

    return f"""已提供的表结构：
{ddl_text}

用户需求：
{user_request}

请生成满足需求的 StarRocks SQL 查询语句："""
