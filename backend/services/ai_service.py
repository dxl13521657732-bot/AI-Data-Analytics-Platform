"""Anthropic Claude API 封装 — 流式 NL→SQL 生成。"""

import json
from typing import AsyncGenerator, Optional

import anthropic

from config import settings
from prompts.nl_to_sql import SYSTEM_PROMPT, build_user_prompt


class AiService:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate_sql_stream(
        self,
        tables_ddl: list[dict],
        user_request: str,
        history: Optional[list[dict]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        流式生成 SQL，返回 SSE 格式数据块：
          data: {"type": "text", "content": "..."}\n\n
          data: {"type": "done"}\n\n
        """
        messages = []

        # 多轮对话历史
        if history:
            for msg in history:
                if msg.get("role") in ("user", "assistant"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        # 当前轮次
        user_prompt = build_user_prompt(tables_ddl, user_request)
        messages.append({"role": "user", "content": user_prompt})

        async with self.client.messages.stream(
            model=settings.anthropic_model,
            max_tokens=settings.anthropic_max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                payload = json.dumps({"type": "text", "content": text}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"
