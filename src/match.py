"""零件库匹配：归一化精确匹配为主，模糊兜底。"""
from __future__ import annotations

from typing import Dict, List

from rapidfuzz import fuzz

from .models import ComponentItem, LibraryPart, MatchOutcome
from .normalize import normalize_key


def build_index(library: List[LibraryPart]) -> Dict[str, List[LibraryPart]]:
    """按归一化 MPN 建索引，支持同一 MPN 多厂商。"""
    index: Dict[str, List[LibraryPart]] = {}
    for lp in library:
        key = normalize_key(lp.mpn)
        index.setdefault(key, []).append(lp)
    return index


def match_one(
    item: ComponentItem,
    library: List[LibraryPart],
    index: Dict[str, List[LibraryPart]],
    threshold: int = 90,
) -> MatchOutcome:
    norm_mpn = normalize_key(item.mpn)
    norm_mfr = normalize_key(item.manufacturer)

    # 1) 精确：MPN 命中，且厂商一致
    candidates = index.get(norm_mpn) if norm_mpn else []
    if candidates:
        for lp in candidates:
            if norm_mfr and normalize_key(lp.manufacturer) == norm_mfr:
                return MatchOutcome("精确匹配", 100.0, lp, "")
        # MPN 精确命中，但厂商缺失或不一致（标记待复核）
        lp = candidates[0]
        if not norm_mfr:
            note = "MPN 精确命中，但 BOM 缺少厂商，仅按 MPN 匹配"
        else:
            note = f"MPN 精确命中，但厂商不一致（BOM「{item.manufacturer}」vs 库「{lp.manufacturer}」）"
        return MatchOutcome("模糊匹配", 100.0, lp, note)

    # 2) 模糊：MPN 编辑距离兜底
    if norm_mpn:
        best: LibraryPart | None = None
        best_score = 0.0
        for lp in library:
            score = fuzz.ratio(norm_mpn, normalize_key(lp.mpn))
            if score > best_score:
                best_score = score
                best = lp
        if best is not None and best_score >= threshold:
            return MatchOutcome(
                "模糊匹配", best_score, best, f"MPN 模糊匹配（相似度 {best_score:.0f}）",
            )

    return MatchOutcome("未匹配", 0.0, None, "未匹配到零件库")
