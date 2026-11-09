"""工程文件提取：Excel BOM、PDF 规格书、零件库 Excel。"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd

from . import llm
from .models import ComponentItem, LibraryPart
from .normalize import is_blank

# 表头别名 -> 标准字段（大小写不敏感匹配）
_FIELD_ALIASES = {
    "seq": ["序号", "seq", "no", "item", "行号"],
    "ref_des": ["参考位号", "位号", "designator", "reference designator", "ref des", "refdes"],
    "part_number": ["料号", "物料号", "物料编码", "编码", "part number", "pn", "料號", "物料編碼"],
    "manufacturer": ["厂商", "厂家", "制造商", "品牌", "manufacturer", "vendor", "brand", "廠商", "製造商"],
    "mpn": ["mpn", "制造商料号", "制造商型号", "manufacturer part number", "part no", "制造商料號"],
    "description": ["描述", "规格", "规格型号", "参数", "description", "規格"],
    "package": ["封装", "封装类型", "package", "footprint", "封裝"],
    "quantity": ["数量", "用量", "quantity", "qty", "數量"],
    "unit": ["单位", "unit", "單位"],
    "category": ["分类", "类别", "category", "分類"],
    "remark": ["备注", "说明", "remark", "note", "備註"],
}


def _map_columns(df: pd.DataFrame) -> dict:
    """把实际表头映射到标准字段名。"""
    mapping = {}
    for col in df.columns:
        key = str(col).strip().casefold()
        for field, aliases in _FIELD_ALIASES.items():
            if key in (a.casefold() for a in aliases):
                mapping[field] = col
                break
    return mapping


def _to_str(value) -> Optional[str]:
    if is_blank(value):
        return None
    s = str(value).strip()
    # pandas 把整数读成 "3.0" 的情况
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    return s or None


def _to_int(value) -> Optional[int]:
    if is_blank(value):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_float(value) -> Optional[float]:
    if is_blank(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def read_bom_excel(path: Path) -> List[ComponentItem]:
    df = pd.read_excel(path)
    mapping = _map_columns(df)
    items: List[ComponentItem] = []
    for _, row in df.iterrows():
        items.append(ComponentItem(
            seq=_to_int(row.get(mapping.get("seq"))),
            ref_des=_to_str(row.get(mapping.get("ref_des"))),
            part_number=_to_str(row.get(mapping.get("part_number"))),
            manufacturer=_to_str(row.get(mapping.get("manufacturer"))),
            mpn=_to_str(row.get(mapping.get("mpn"))),
            description=_to_str(row.get(mapping.get("description"))),
            package=_to_str(row.get(mapping.get("package"))),
            quantity=_to_float(row.get(mapping.get("quantity"))),
            unit=_to_str(row.get(mapping.get("unit"))),
            remark=_to_str(row.get(mapping.get("remark"))),
            source="excel",
        ))
    return items


def read_parts_library(path: Path) -> List[LibraryPart]:
    df = pd.read_excel(path)
    mapping = _map_columns(df)
    parts: List[LibraryPart] = []
    for _, row in df.iterrows():
        parts.append(LibraryPart(
            part_number=_to_str(row.get(mapping.get("part_number"))),
            manufacturer=_to_str(row.get(mapping.get("manufacturer"))),
            mpn=_to_str(row.get(mapping.get("mpn"))),
            description=_to_str(row.get(mapping.get("description"))),
            package=_to_str(row.get(mapping.get("package"))),
            category=_to_str(row.get(mapping.get("category"))),
        ))
    return parts


def read_pdf(path: Path) -> List[ComponentItem]:
    """文字版 PDF 规格书 -> 抽取纯文本 -> DeepSeek 结构化。"""
    import pymupdf

    doc = pymupdf.open(str(path))
    try:
        text = "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()
    return llm.extract_components_from_text(text)
