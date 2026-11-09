"""数据模型：元器件条目、零件库条目、处理结果。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from pydantic import BaseModel


class ComponentItem(BaseModel):
    """从工程文件提取出的一条元器件记录。"""
    seq: Optional[int] = None            # 序号
    ref_des: Optional[str] = None        # 参考位号，如 "R1,R2,R3"
    part_number: Optional[str] = None    # 内部料号
    manufacturer: Optional[str] = None   # 厂商
    mpn: Optional[str] = None            # 制造商料号
    description: Optional[str] = None    # 描述
    package: Optional[str] = None        # 封装
    quantity: Optional[float] = None     # 数量
    unit: Optional[str] = None           # 单位
    remark: Optional[str] = None         # 备注
    source: str = "excel"                # 来源：excel | pdf


class LibraryPart(BaseModel):
    """零件库中的一条零件。"""
    part_number: Optional[str] = None    # 内部料号（主键）
    manufacturer: Optional[str] = None   # 厂商
    mpn: Optional[str] = None            # 制造商料号
    description: Optional[str] = None    # 描述
    package: Optional[str] = None        # 封装
    category: Optional[str] = None       # 分类


@dataclass
class MatchOutcome:
    """单条元器件的匹配结果。"""
    match_status: str                    # 精确匹配 | 模糊匹配 | 未匹配
    score: float = 0.0
    matched: Optional[LibraryPart] = None
    note: str = ""


@dataclass
class ProcessedRow:
    """一条元器件经过匹配与校验后的完整结果。"""
    item: ComponentItem
    match: MatchOutcome
    issues: List[str] = field(default_factory=list)

    @property
    def needs_review(self) -> bool:
        """需人工复核：有校验问题，或匹配不确定。"""
        return bool(self.issues) or self.match.match_status in ("未匹配", "模糊匹配")
