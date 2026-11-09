"""主管线：提取 -> 匹配 -> 校验。"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from . import config, extract, match, validate
from .models import ComponentItem, LibraryPart, ProcessedRow


def run_pipeline(
    bom_excel: Path,
    library_excel: Path,
    pdf: Optional[Path] = None,
) -> List[ProcessedRow]:
    library: List[LibraryPart] = extract.read_parts_library(library_excel)
    items: List[ComponentItem] = extract.read_bom_excel(bom_excel)
    if pdf is not None:
        items.extend(extract.read_pdf(pdf))

    index = match.build_index(library)
    rows = [
        ProcessedRow(item=it, match=match.match_one(it, library, index, threshold=config.FUZZY_THRESHOLD))
        for it in items
    ]
    validate.validate(rows)
    return rows
