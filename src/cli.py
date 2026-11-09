"""CLI 入口：python -m src.cli run ..."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from . import config, output, pipeline

app = typer.Typer(help="制造业 BOM 处理智能体（v1）")


@app.callback()
def _root() -> None:
    """制造业 BOM 处理智能体（v1）：提取 → 匹配 → 校验 → 输出。"""


@app.command()
def run(
    bom: Path = typer.Option(..., "--bom", help="输入的 Excel BOM 导出"),
    library: Path = typer.Option(..., "--library", help="零件库 Excel"),
    pdf: Optional[Path] = typer.Option(None, "--pdf", help="可选：PDF 规格书"),
    out: Path = typer.Option(config.OUTPUT_DIR / "bom_output.xlsx", "--out", help="输出 xlsx 路径"),
):
    """提取 → 匹配 → 校验 → 输出。"""
    rows = pipeline.run_pipeline(bom, library, pdf)
    output.write_output(rows, out)

    n_review = sum(1 for r in rows if r.needs_review)
    n_unmatched = sum(1 for r in rows if r.match.match_status == "未匹配")
    typer.echo(f"处理完成：共 {len(rows)} 行，需人工复核 {n_review} 行，未匹配 {n_unmatched} 行。")
    typer.echo(f"输出：{out}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
