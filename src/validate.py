"""一致性校验规则：①②③⑤。"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import List, Sequence

from .models import ComponentItem, ProcessedRow
from .normalize import is_blank


def _k(value) -> str:
    """归一化为可比较的字符串键（缺失统一为空串）。"""
    return "" if is_blank(value) else str(value).strip().casefold()


def _ref_tokens(item: ComponentItem) -> List[str]:
    """把参考位号拆成单个位号，如 "R1,R2 R3" -> ["R1","R2","R3"]。"""
    if is_blank(item.ref_des):
        return []
    return [t for t in re.split(r"[,;，；\s]+", str(item.ref_des).strip()) if t]


def _dup_key(item: ComponentItem):
    """重复行判定键：核心字段完全一致（不含序号/备注/来源）。"""
    return (
        _k(item.ref_des), _k(item.part_number), _k(item.manufacturer),
        _k(item.mpn), _k(item.description), _k(item.package),
        _k(item.quantity), _k(item.unit),
    )


def validate(rows: Sequence[ProcessedRow]) -> None:
    """就地给每个 ProcessedRow 追加 issues。"""
    # ③ 参考位号出现次数
    ref_counter: defaultdict = defaultdict(int)
    for row in rows:
        for token in _ref_tokens(row.item):
            ref_counter[token] += 1

    # ② 重复行计数
    dup_counter: defaultdict = defaultdict(int)
    for row in rows:
        dup_counter[_dup_key(row.item)] += 1

    for row in rows:
        it = row.item
        issues: List[str] = []

        # ① 缺失料号/厂商/MPN
        if is_blank(it.part_number):
            issues.append("缺失料号")
        if is_blank(it.manufacturer):
            issues.append("缺失厂商")
        if is_blank(it.mpn):
            issues.append("缺失MPN")

        # ③ 参考位号缺失 / 重复
        tokens = _ref_tokens(it)
        if not tokens:
            issues.append("缺失参考位号")
        else:
            dups = sorted({t for t in tokens if ref_counter[t] > 1})
            if dups:
                issues.append("参考位号重复：" + ",".join(dups))

        # ② 重复行
        if dup_counter[_dup_key(it)] > 1:
            issues.append("重复行")

        # ⑤ 匹配不到零件库
        if row.match.match_status == "未匹配":
            issues.append("未匹配零件库")

        row.issues = issues
