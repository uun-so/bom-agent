"""DeepSeek 接入：用于 PDF 规格书的结构化抽取。"""
from __future__ import annotations

import json
import re
from typing import List

from pydantic import ValidationError

from . import config
from .models import ComponentItem

_EXTRACT_PROMPT = """你是制造业 BOM 工程师的助手。下面是从一份元器件规格书（datasheet）中提取的文本。
请从中找出所有元器件条目，并以 JSON 输出。只输出 JSON，不要输出任何解释。

JSON 结构：
{"components": [{"part_number": "内部料号(若无则 null)", "manufacturer": "厂商", "mpn": "制造商料号",
"description": "描述", "package": "封装", "quantity": 数量数字或 null, "unit": "单位", "remark": "备注"}]}

要求：
- 字段缺失时填 null。
- 只提取真实出现在文本中的信息，不要编造。
- manufacturer 与 mpn 尽量同时给出；两者都未知时都填 null。

文本如下：
"""


def _parse_json(content: str) -> dict:
    """稳健解析 LLM 返回的 JSON（去除可能的 markdown 代码块）。"""
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def extract_components_from_text(text: str) -> List[ComponentItem]:
    """把 PDF 抽取的纯文本交给 DeepSeek，返回结构化元器件列表。"""
    if not config.DEEPSEEK_API_KEY:
        raise RuntimeError(
            "未设置环境变量 DEEPSEEK_API_KEY。请在运行前设置：export DEEPSEEK_API_KEY=sk-..."
        )

    from openai import OpenAI

    client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)
    resp = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": "你只输出 JSON。"},
            {"role": "user", "content": _EXTRACT_PROMPT + text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    data = _parse_json(resp.choices[0].message.content)
    comps = data.get("components", [])

    items: List[ComponentItem] = []
    for c in comps:
        try:
            items.append(ComponentItem(**c, source="pdf"))
        except ValidationError:
            # 跳过无法解析的条目，避免单个字段类型错误中断整批
            continue
    return items
