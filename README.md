# BOM-Agent-Python v1

基于大模型的制造业 BOM 物料清单处理智能体。

管线：**工程文件提取 → 归一化 → 匹配零件库 → 一致性校验 → 输出标准化 BOM（含人审高亮部分）**。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. （可选）生成 mock 样例，验证用
python scripts/generate_mock_data.py

# 3. 设置 DeepSeek API Key（仅 PDF 抽取需要；纯 Excel 流程无需）
#    方式一（推荐）：在项目根目录建 .env 文件，写入一行：DEEPSEEK_API_KEY=sk-...
#    方式二：环境变量  export DEEPSEEK_API_KEY=sk-...  （Windows: set DEEPSEEK_API_KEY=sk-...）

# 4. 运行（纯 Excel 流程，无需 API Key）
python -m src.cli run \
  --bom data/sample_bom_export.xlsx \
  --library data/parts_library.xlsx \
  --out output/bom_output.xlsx

# 含 PDF 规格书（需要 API Key）
python -m src.cli run \
  --bom data/sample_bom_export.xlsx \
  --library data/parts_library.xlsx \
  --pdf data/some_datasheet.pdf
```

## 目录结构

```
Bom-Agent-Python/
├─ data/             # 输入样例（BOM 导出 + 零件库）
├─ scripts/          # generate_mock_data.py 生成 mock 样例
├─ src/
│  ├─ config.py      # 路径、DeepSeek 配置、模糊阈值
│  ├─ models.py      # pydantic / dataclass 数据结构
│  ├─ normalize.py   # 归一化
│  ├─ extract.py     # Excel / PDF 提取
│  ├─ llm.py         # DeepSeek 封装（PDF 结构化抽取）
│  ├─ match.py       # 精确 + 模糊匹配
│  ├─ validate.py    # 一致性校验
│  ├─ pipeline.py    # 主管线
│  ├─ output.py      # 写 Excel + 高亮
│  └─ cli.py         # typer CLI
├─ output/           # 输出结果
├─ v1-ADR.md         # 设计决策记录
└─ README.md
```

## 输出说明

输出 xlsx 在原始字段基础上追加：

- **匹配状态**：精确匹配 / 模糊匹配 / 未匹配
- **匹配料号/厂商/MPN/描述/封装/分类**：命中零件库后回填的字段
- **校验问题**：缺失料号、缺失厂商、缺失MPN、缺失参考位号、参考位号重复、重复行、未匹配零件库
- **是否需人工复核**：有校验问题或匹配不确定时为是，该行整行黄色高亮

## 当前版本功能（v1)

- 读取Excel格式bom清单
- 读取零件库文件
- PDF datasheet信息提取
- 基础字段匹配，输出匹配结果Excel
- CLI交互运行

## 迭代计划（v2）

- [ ] 厂商别名映射（manufacturer alias mapping）
- [ ] MPN后缀归一化/剥离，提升匹配成功率
- [ ] 优化大模型Prompt，进一步提升提取准确率
- [ ] 增加Web/可视化界面

## 项目难点

- PDF datasheet排版不规范，文本提取容易乱码、字段错位，需要预处理清洗文本
- MPN带有各类后缀（如  /NOPB ），直接精确匹配就失败，后续计划增加后缀剥离模块
- 厂商名称写法不统一（全称 / 简写 / 中英文），考虑维护别名映射表来解决
-  一开始AI提取结果不稳定，反复调试Prompt，并且增加校验逻辑，对输出结果做验证

## 设计决策

见 `v1-ADR.md`。
