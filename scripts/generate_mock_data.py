"""生成脱敏 mock 样例数据，用于端到端验证。"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)

    library = [
        # 料号, 厂商, MPN, 描述, 封装, 分类
        ["PN-1001", "国巨", "RC0603FR-0710KL", "10kΩ 1% 0603 电阻", "0603", "电阻"],
        ["PN-1002", "村田", "GRM188R71C105KA12D", "1uF 16V X7R 0603 电容", "0603", "电容"],
        ["PN-1003", "TI", "LM1117MPX-3.3", "LDO 稳压器 3.3V 800mA", "SOT-223", "IC"],
        ["PN-1004", "STMicroelectronics", "STM32F103C8T6", "ARM Cortex-M3 MCU 64KB", "LQFP-48", "IC"],
        ["PN-1005", "Vishay", "1N4148WS", "开关二极管 100V 150mA", "SOD-323", "二极管"],
        ["PN-1006", "国巨", "RC0603FR-071KL", "1kΩ 1% 0603 电阻", "0603", "电阻"],
        ["PN-1007", "村田", "GRM188R71E104KA01D", "0.1uF 25V X7R 0603 电容", "0603", "电容"],
        ["PN-1008", "Microchip", "ATMEGA328P-AU", "8位 AVR MCU 32KB", "TQFP-32", "IC"],
        ["PN-1009", "ON Semiconductor", "MMBT3904", "NPN 三极管 40V 200mA", "SOT-23", "三极管"],
        ["PN-1010", "Wurth", "744042100", "4.7uH 功率电感", "SMD", "电感"],
    ]
    lib_df = pd.DataFrame(library, columns=["料号", "厂商", "MPN", "描述", "封装", "分类"])
    lib_df.to_excel(DATA / "parts_library.xlsx", index=False)

    bom = [
        # 序号, 参考位号, 料号, 厂商, MPN, 描述, 封装, 数量, 单位, 备注
        [1, "R1,R2,R3", "PN-1001", "国巨", "RC0603FR-0710KL", "10kΩ", "0603", 3, "pcs", "精确匹配"],
        [2, "C1,C2", "PN-1002", "村田", "GRM188R71C105KA12D", "1uF 16V", "0603", 2, "pcs", "精确匹配"],
        [3, "U1", "PN-1003", "TI", "LM1117MPX-3.3", "LDO 3.3V", "SOT-223", 1, "pcs", "精确匹配"],
        [4, "U2", "PN-1004", "ST", "STM32F103C8T6", "MCU", "LQFP-48", 1, "pcs", "厂商别名→模糊"],
        [5, "D1", "PN-1005", "Vishay", "1N4148WS", "二极管", "SOD-323", 1, "pcs", "精确匹配"],
        [6, "R4", "PN-1006", "国巨", "RC0603FR-071KL", "1kΩ", "0603", 1, "pcs", "精确匹配"],
        [7, "R5", None, "国巨", "RC0603FR-0710KL", "10kΩ", "0603", 1, "pcs", "缺失料号"],
        [8, "C3", "PN-1007", None, "GRM188R71E104KA01D", "0.1uF 25V", "0603", 1, "pcs", "缺失厂商"],
        [9, None, "PN-1008", "Microchip", "ATMEGA328P-AU", "MCU", "TQFP-32", 1, "pcs", "缺失参考位号"],
        [10, "R1", "PN-1001", "国巨", "RC0603FR-0710KL", "10kΩ", "0603", 1, "pcs", "参考位号R1重复"],
        [11, "C4", "PN-1002", "村田", "GRM188R71C105KA12O", "1uF 16V", "0603", 1, "pcs", "MPN笔误→模糊"],
        [12, "U3", "PN-1011", "NXP", "XYZ123456", "未知芯片", "QFN-32", 1, "pcs", "未匹配"],
        [13, "R4", "PN-1006", "国巨", "RC0603FR-071KL", "1kΩ", "0603", 1, "pcs", "与行6重复行"],
        [14, "C5", "PN-1012", "村田", None, "0.1uF", "0603", 1, "pcs", "缺失MPN"],
    ]
    bom_df = pd.DataFrame(bom, columns=["序号", "参考位号", "料号", "厂商", "MPN", "描述", "封装", "数量", "单位", "备注"])
    bom_df.to_excel(DATA / "sample_bom_export.xlsx", index=False)

    print(f"已生成 mock 样例：")
    print(f"  零件库：{DATA / 'parts_library.xlsx'}")
    print(f"  BOM 导出：{DATA / 'sample_bom_export.xlsx'}")


if __name__ == "__main__":
    main()
