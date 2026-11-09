"""字符串归一化：匹配键与展示文本。"""
from __future__ import annotations

import re
from typing import Optional


def normalize_key(value: Optional[object]) -> str:
    """生成用于匹配的归一化键：小写、去空白与符号，保留字母/数字/CJK。"""
    if value is None:
        return ""
    s = str(value).casefold()
    return "".join(ch for ch in s if ch.isalnum() or "一" <= ch <= "鿿")


def normalize_text(value: Optional[object]) -> str:
    """压缩多余空白，用于展示。"""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def is_blank(value: Optional[object]) -> bool:
    """判断字段是否缺失/空白。"""
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.casefold() in {"nan", "none", "null"}
