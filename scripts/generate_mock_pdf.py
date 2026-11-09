"""生成 mock 文字版 PDF 规格书，用于验证 PDF -> DeepSeek 抽取链路。"""
from __future__ import annotations

from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# 纯 ASCII 内容，避免默认 Helvetica 字体无法渲染 CJK/特殊符号
DATASHEET_TEXT = """\
Analog Devices - AD8605ARTZ-REEL7
Precision Rail-to-Rail Operational Amplifier
SOT-23-5
----------------------------------------
Microchip Technology - ATMEGA328P-AU
8-bit AVR Microcontroller, 32KB Flash
TQFP-32
----------------------------------------
Texas Instruments - LM1117MPX-3.3/NOPB
800mA Low-Dropout Linear Regulator
SOT-223
"""


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open()
    page = doc.new_page()
    y = 72
    for line in DATASHEET_TEXT.splitlines():
        page.insert_text((72, y), line, fontsize=11)
        y += 18
    out = DATA / "sample_datasheet.pdf"
    doc.save(str(out))
    doc.close()
    print(f"已生成 mock PDF：{out}")


if __name__ == "__main__":
    main()
