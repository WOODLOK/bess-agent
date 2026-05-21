# Skill: Stage 1 — 用户数据输入分析 (Parse Input)

## When to invoke

当用户在 `inputs/` 下放置了新的供应链中断材料，或在对话中粘贴了文本/附件时，触发本阶段。

触发信号：
- 用户说"分析这次中断"、"看看这批材料"、"帮我归因这个延误"
- `inputs/` 目录下出现了新的文件或子目录
- 对话中用户直接粘贴合同节选、邮件内容、运输记录等文本

## Inputs

输入来源（按优先级）：
1. `inputs/<batch_id>/` 下的所有文件——可能是 `.md`, `.txt`, `.pdf`, `.png`, `.jpg`, `.eml`
2. 用户在对话中直接粘贴的文本块
3. 用户在对话中上传的附件（PDF、图像、电子表格）

输入形态：纯文本叙述、PDF 合同/对账单、运输单据/检验报告的扫描件或图片、邮件往来截图、内部周会纪要，或以上形式的任意混合。

## Steps

### Step 1.1: 扫描输入源并生成 case_id

1. 遍历 `inputs/` 下所有非 `.gitkeep` 文件，列出文件名、类型、大小
2. 检查用户对话中的文本粘贴或附件
3. 生成 `case_id`，格式 `YYYY-MM-DD-<2-3-word-slug>`，例如：
   - `2022-04-15-shanghai-cell-delay`
   - `2023-12-01-graphite-export-ban`
   - slug 用英文小写，以 `-` 连接，概括事件核心特征
4. 创建运行目录 `runs/<case_id>/`

### Step 1.2: 多模态内容提取

按输入类型选择处理路径：

**文本（.md / .txt / 对话粘贴）**：
- 直接读取全文，不修改原始内容

**PDF（.pdf）**：
- 优先使用 Read 工具直接读取 PDF（本客户端支持 PDF 原生阅读）
- 若 Read 工具返回错误或内容不完整，退回到 `python scripts/extract_pdf.py <file>` 批量抽取文本
- PDF 中的表格数据需单独标注"来源为 PDF 表格"

**图像/扫描件（.png / .jpg / .tiff）**：
- 优先使用 Read 工具直接读取图像（本客户端支持图像原生阅读）
- 从图像中提取：文字（OCR 由客户端自动完成）、表格结构、手写笔记、印章/签名等视觉信息
- 对扫描质量较差的图像，在 `observations` 中标注"图像质量影响识别准确度"

**混合多模态**：
- 对同一事件的多种材料，交叉比对信息。例如：合同 PDF 中的交货日期 vs 邮件中的"实际到港日" vs 运输单据上的提单日期
- 如有信息冲突，在 `inferred_clues` 中记录而不自行裁决

### Step 1.3: 抽取事件骨架——按信息性质四类区分

这是本阶段最关键的步骤。从所有材料中抽取信息后，**严格按以下四类归档**，不得混淆：

**一类：`observations`（可直接验证的事实）**
- 判断标准：如果第三方看到这份材料，是否会得出相同的结论？
- 示例：
  - "合同附件第 3 页：合同编号 PO-2022-0317，交货日期 2022-03-01"
  - "运输单据 BL-20220415：提单日期 2022-04-12，装货港上海，卸货港洛杉矶"
  - "邮件 2022-05-20 from 张三：'至今未收到货'"
- 每项必须注明 `source`（材料名 + 页码/行号）

**二类：`user_claims`（用户的主观断言）**
- 判断标准：这是用户/叙述者的解释、判断或感受，而非可被材料本身证明的事实
- 示例：
  - "CEO 在邮件中认为延误主要是供应商管理混乱"
  - "项目经理口头表示'我们当时根本来不及切换供应商'"
- 每项必须标注 `needs_verification: true`

**三类：`inferred_clues`（推测线索）**
- 判断标准：材料中没有直接说，但你能从上下文、语气、文件间关系中间接嗅到的信号
- 示例：
  - "供应商在 3 封邮件中反复提及 'renegotiation'，但合同并未到期——暗示可能存在价格争议"
  - "提单日期 2022-04-12 与合同约定的交货日期 2022-03-01 相差 42 天，但期间邮件往来极少——可能电话沟通替代了书面记录，或双方已在走不可抗力流程"
- 每项标注 `priority`（high/medium/low），高优先级的 clue 将作为阶段二的假设方向

**四类：`unknown_fields`（明显缺失的信息）**
- 判断标准：对后续推理至关重要但当前材料完全没有覆盖
- 示例：
  - "缺失：电芯的具体规格（280Ah? 302Ah?）——影响判断是否有替代供应"
  - "缺失：最终实际到港日期——无法确定总延误天数"
- 每项标注 `importance`（critical/high/medium）和 `suggested_source`

### Step 1.4: 填充事件骨架结构化字段

从已归类的信息中，提取以下结构化字段填入 `event_skeleton.json`：

- `time_window`：从材料的各类日期中推断最早和最晚时间边界
- `parties`：所有提及的相关方（供应商/承运人/客户/监管机构），标注 certainty（explicit/inferred）
- `locations`：所有提及的地理位置，标注在供应链中的角色（origin/port_of_loading/port_of_discharge/destination）
- `materials`：涉及的物料类别与规格

如果信息不足以填充某字段，在 `unknown_fields` 中记录而非编造。

### Step 1.5: 写入并验证

1. 将以上四类内容写入 `runs/<case_id>/event_skeleton.json`
2. 对照 `schemas/event_skeleton.schema.json` 验证必填字段完整性
3. 确认 `observations` 中每一条都能回指到材料的具体位置
4. 确认没有把 `user_claims` 混入 `observations`

## Outputs

- **`runs/<case_id>/event_skeleton.json`**：符合 `schemas/event_skeleton.schema.json` 的事件骨架，是阶段二的唯一输入。四类内容（observations / user_claims / inferred_clues / unknown_fields）均有明确标记。

## Constraints

- **P6 五阶段不可跳跃**：必须在阶段二之前完成本阶段，产出 `event_skeleton.json` 后才能进入下一阶段
- **事实 vs 主观必须区分**：`observations` 中不允许出现"我们认为"、"推测"、"可能"等主观表述；这些必须归入 `user_claims` 或 `inferred_clues`
- **缺失信息不编造**：`unknown_fields` 必须被诚实地记录，不允许用猜测填充
- **材料不修改**：原始材料不做任何修改，仅做抽取与归档；如需标记，在 `observations` 的 `source` 字段中引用
- **不删除 AGENT.md、skills/、schemas/**：这些都是项目宪法文件

## Examples

### Mini 示例：纯文本口述

**用户输入**（粘贴在对话中）：
> "我们 2022 年 4 月从上海港发的一批 280Ah LFP 电芯，本来应该 3 月初到洛杉矶的。结果 5 月底才到。供应商说是港口拥堵，但我们怀疑是他们排产出了问题。那段时间碳酸锂价格也在疯涨。"

**产出 event_skeleton.json 节选**：

```json
{
  "case_id": "2022-04-15-shanghai-cell-delay",
  "time_window": { "earliest": "2022-03-01", "latest": "2022-05-31", "precision": "month" },
  "parties": [
    { "name": "(未具名供应商)", "role": "supplier", "certainty": "inferred" }
  ],
  "locations": [
    { "name": "上海港", "role": "port_of_loading", "certainty": "explicit" },
    { "name": "洛杉矶港", "role": "port_of_discharge", "certainty": "explicit" }
  ],
  "materials": [
    { "category": "lfp_cell", "specification": "280Ah LFP电芯" }
  ],
  "observations": [
    {
      "field": "planned_departure",
      "value": "2022年4月从上海港发货",
      "source": "用户口述"
    },
    {
      "field": "planned_arrival",
      "value": "原定2022年3月初到洛杉矶",
      "source": "用户口述"
    },
    {
      "field": "actual_arrival",
      "value": "2022年5月底到港",
      "source": "用户口述"
    }
  ],
  "user_claims": [
    {
      "claim": "供应商说是港口拥堵导致延误",
      "source": "用户转述供应商解释",
      "needs_verification": true
    },
    {
      "claim": "用户怀疑供应商排产出了问题",
      "source": "用户主观判断",
      "needs_verification": true
    }
  ],
  "inferred_clues": [
    {
      "clue": "碳酸锂价格同期疯涨——可能影响了供应商的履约意愿或成本结构",
      "basis": "用户提及'碳酸锂价格在疯涨'+ 发货时间(2022年4月)与碳酸锂价格冲顶阶段(2022年)重叠",
      "priority": "high"
    },
    {
      "clue": "发货日(4月)晚于原定到港日(3月)——可能存在用户未提及的更早期谈判或合同变更",
      "basis": "时间线倒挂：4月发货不可能实现3月到港",
      "priority": "high"
    }
  ],
  "unknown_fields": [
    {
      "field": "供应商名称与合同编号",
      "importance": "high",
      "suggested_source": "向用户索要合同附件或采购订单"
    },
    {
      "field": "提单号与船名",
      "importance": "medium",
      "suggested_source": "向用户索要运输单据"
    },
    {
      "field": "实际成交价格与合同价格对比",
      "importance": "high",
      "suggested_source": "合同附件或财务对账单"
    }
  ]
}
```
