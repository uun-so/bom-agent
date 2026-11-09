"""输出：写 Excel，高亮需人工复核的行。"""
from __future__ import annotations

from pathlib import Path
from typing import List

from openpyxl import Workbook
from openpyxl.styles import PatternFill

from .models import ProcessedRow

_HEADERS = [
    "序号", "参考位号", "料号", "厂商", "MPN", "描述", "封装", "数量", "单位", "备注", "来源",
    "匹配状态", "匹配说明", "匹配料号", "匹配厂商", "匹配MPN", "匹配描述", "匹配封装", "匹配分类",
    "校验问题", "是否需人工复核",
]


def _val(v):
    return "" if v is None else v


def write_output(rows: List[ProcessedRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "BOM"
    ws.append(_HEADERS)

    yellow = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")

    for row in rows:
        it = row.item
        m = row.match.matched
        values = [
            _val(it.seq), _val(it.ref_des), _val(it.part_number), _val(it.manufacturer),
            _val(it.mpn), _val(it.description), _val(it.package), _val(it.quantity),
            _val(it.unit), _val(it.remark), _val(it.source),
            row.match.match_status,
            row.match.note,
            _val(m.part_number) if m else "", _val(m.manufacturer) if m else "",
            _val(m.mpn) if m else "", _val(m.description) if m else "",
            _val(m.package) if m else "", _val(m.category) if m else "",
            "；".join(row.issues),
            "是" if row.needs_review else "否",
        ]
        ws.append(values)
        if row.needs_review:
            for cell in ws[ws.max_row]:
                cell.fill = yellow

    wb.save(path)
