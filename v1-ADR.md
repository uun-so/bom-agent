# BOM-Agent-Python v1
来自设计访谈的部分记录。
记录目前已经确定的设计决策，以及尚未解决的问题，后续从待解决问题列表深挖。

## 已确定决策

### 定位
- 基于大模型的制造业 BOM 物料清单处理智能体：从工程文件提取元器件信息 → 匹配零件库 → 校验数据一致性 → 输出标准化 BOM 表格。

### 输入
- 一期：Excel BOM 导出 + PDF 规格书（文字版 PDF，多厂商格式各异）。
- 二期：CAD 原理图导出（Altium/OrCAD/KiCad/Cadence）解析。

### 零件库
- 已有 Excel 表，程序直接读取。
- 匹配主键：厂商 + 制造商料号（MPN）。
- 描述、封装作为辅助字段。

### 架构
- 固定管线（提取 → 匹配 → 校验 → 输出），各步骤内 LLM 增强；非端到端自由 agent。

### LLM
- 云端 API：DeepSeek（OpenAI 兼容接口）。

### 匹配
- 归一化精确匹配为主 + 模糊兜底（rapidfuzz）。
- 语义（embedding）匹配：v1 先跳过，需要时加本地 sentence-transformers（bge-m3）。

### 校验
- ① 缺失料号/厂商 ② 重复行 ③ 参考位号重复或缺失 ⑤ 匹配不到零件库。
- ④ 数量/单位、⑥ 描述冲突 拿到真实样例后再细化。

### 输出
- Excel(.xlsx)，对齐公司 BOM 模板。
- 无现成模板 → 由我定义默认列 + 自建 mock 样例。

### 人审
- 输出前人工复核：自动产出后高亮「不确定/失败」条目，确定项直接通过。

### 规模与接口
- 单文件几十~几百行；先 CLI（typer），验证后再包一层 Web。

### 语言
- 中英混排。

### 技术栈
- Python 3.11+；`pandas` + `openpyxl`（Excel 读写）；`pymupdf`（PDF 文本提取）；`openai` SDK 指向 DeepSeek；`pydantic`（结构化输出校验）；`rapidfuzz`（模糊匹配）；`typer`（CLI）。
- 不用 LangChain，直连 SDK。减少第三方框架黑盒、版本迭代带来的不稳定问题，获得更高可控性
- AI低代码调研：调研Dify、Coze两款AI低代码平台，能够通过拖拽方式搭建Agent流程，快速做原型演示

## 待解决问题
- [ ] 真实样例文件（脱敏 Excel BOM 导出 + 零件库）——先用自定义的默认列 + mock 样例开工，拿到真实数据后对齐。
- [ ] 厂商别名映射：库用中文/简写（村田/Microchip/TI），规格书用英文/全称（Murata/Microchip Technology/Texas Instruments），当前落到「模糊匹配」待复核；后续可加别名表（或语义匹配）。
- [ ] MPN 后缀变体归一化：`/NOPB`、`-REEL7`、`TR`、`R` 等封装/包装后缀导致精确匹配失败；后续可加去后缀规则。
