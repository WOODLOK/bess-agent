# Skill: Stage 5 — 写入案例记忆库 (Write Memory)

## When to invoke

当阶段四完成，以下四个文件均已生成后，触发本阶段：
- `runs/<case_id>/causal_chain.md`
- `runs/<case_id>/causal_chain.json`
- `runs/<case_id>/impact_estimates.json`
- `runs/<case_id>/uncertainty_notes.md`

## Inputs

- **`runs/<case_id>/` 下的全部文件**：
  - `event_skeleton.json`（阶段一）
  - `hypotheses.json`（阶段二）
  - `evidence_log.json`（阶段三）
  - `causal_chain.md` + `causal_chain.json`（阶段四）
  - `impact_estimates.json`（阶段四）
  - `uncertainty_notes.md`（阶段四）
- **`memory/INDEX.md`**：现有案例索引（用于追加新条目与关联标注）
- **`memory/cases/` 下的所有已有案例**：用于语义关联判断

## Steps

### Step 5.1: 创建案例目录

在 `memory/cases/` 下创建 `memory/cases/<case_id>/` 目录。

### Step 5.2: 迁移并整理案例文件

将 `runs/<case_id>/` 中的以下文件**复制**（不是移动，保留 runs/ 中的原始运行记录）到 `memory/cases/<case_id>/`：

```
memory/cases/<case_id>/
├── case_entry.json         # 结构化元数据（新生成，遵循 schemas/case_entry.schema.json）
├── causal_chain.md         # 从 runs/ 复制
├── evidence_log.json       # 从 runs/ 复制
├── impact_estimates.json   # 从 runs/ 复制
├── uncertainty_notes.md    # 从 runs/ 复制（重命名自原文件）
├── source_documents/       # 新建目录
│   └── (用户原始材料的副本或引用文件列表)
└── summary.md              # 新生成：一句话摘要 + 标签 + 创建日期
```

### Step 5.3: 生成 case_entry.json

从阶段一至四的产出物中提取结构化字段，填充 `memory/cases/<case_id>/case_entry.json`。

**关键规则**：
- 字段严格按 `schemas/case_entry.schema.json` 映射
- `causal_chain_summary`：从 `causal_chain.md` 提取约 150-300 字的核心摘要。这段文本将用于语义检索，必须包含：发生了什么、为什么发生、影响了什么
- `impact_metrics`：从 `impact_estimates.json` 中提取最关键的数值区间
- `evidence_links`：从 `evidence_log.json` 中提取所有 `status: "success"` 的条目，每条保留 evidence_id、tool、result_summary、factor_category、source_url
- `confidence_level`：综合 `impact_estimates.json` 的 `overall_confidence` 与 `uncertainty_notes.md` 中列出的证据空白规模来评定。规则：
  - 3 类以上因素有强证据 + 少量证据空白 → high
  - 2 类因素有证据 + 部分空白 → medium
  - 1 类以下有强证据 或 大面积空白 → low
- `source_documents`：从 `event_skeleton.json` 的 observations 中回溯原始材料列表

### Step 5.4: 生成 summary.md

为每个案例生成 `summary.md`，作为人工快速浏览的入口。格式：

```markdown
# <case_id>

**一句话因果总结**：<一句话描述根因、传导机制与最终影响>

**主要影响因素**：<物流, 原材料, 合同与项目, 合规与政策——从中选择实际涉及的>

**事件类型标签**：<从 event_signature 中提取>

**时间窗口**：<earliest> 至 <latest>

**整体置信度**：<low / medium / high>

**关键证据链接**：
- [E1] <result_summary> — <source_url>
- [E2] <result_summary> — <source_url>
- ...

**相关案例**：<related_cases 列表，如暂无则标注"暂无">

**创建日期**：<creation_date>
```

### Step 5.5: 建立与历史案例的语义关联

这一步是将新案例与记忆库中已有案例连接起来的关键环节。

1. **读取 `memory/INDEX.md`** 获取所有已有案例的 case_id 和一句话摘要
2. **对每个已有案例，按 AGENT.md 第 6 节的相似度匹配维度进行对比**：
   - 强匹配维度：供应链环节、中断类型、触发因素——是否相同或相近？
   - 弱匹配维度：地理区域、时间窗口、影响程度、缓解措施——用于排序
3. **标注 `related_cases`**：
   - 将在强匹配维度上至少有 2 项命中的案例列入 `related_cases`
   - 在 `summary.md` 的"相关案例"部分：对每个相关案例用一句话说明关联点
   - 格式示例：
     > - `2022-04-shanghai-cell-delay`：同为上海港出口延误，中断类型相同（海运延误+原材料价格叠加），时间窗口接近（2022年4月 vs 2021年9月）
4. **反向关联**：如果发现某已有案例与新案例强相关，在已有案例的 `case_entry.json` 的 `related_cases` 字段中追加新案例的 case_id，并更新其 `revision_history`

### Step 5.6: 更新 INDEX.md

在 `memory/INDEX.md` 的表格顶部（按时间倒序）追加新行：

```markdown
| <case_id> | <一句话因果总结> | <影响因素标签，以逗号分隔> | <related_cases，以逗号分隔> | <creation_date> |
```

- 如果新案例的 `event_time_window.earliest` 比表中的已有条目更近，则插入对应位置
- 保持表格按时间倒序

### Step 5.7: 复制源文档引用

在 `memory/cases/<case_id>/source_documents/` 下：
- 如果用户材料在 `inputs/` 下，在此创建指向原文件的引用文件（如 `source_list.md` 列出原始文件路径）
- 如果材料是对话粘贴的文本，将文本保存为 `user_pasted_text.md`
- 不要复制大型二进制文件（PDF、图像）——仅记录路径引用

### Step 5.8: 向用户输出最终摘要

完成以上步骤后，向用户输出一段简短摘要。格式参考：

```
已完成案例沉淀：**2022-04-15-shanghai-cell-delay**

上海封控导致的港口作业停滞（2022年3-5月）是该批280Ah LFP电芯延误的主要原因，
延误估计约 35-50 天。同期碳酸锂价格快速上涨可能影响了供应商的履约行为，
但目前证据仅能证明价格压力存在，不能直接证明供应商主动拖延交付。
整体置信度：中。

案例已写入 memory/cases/2022-04-15-shanghai-cell-delay/
INDEX.md 已更新。
```

## Outputs

- **`memory/cases/<case_id>/`**：完整的案例目录，包含 case_entry.json、causal_chain.md、evidence_log.json、impact_estimates.json、uncertainty_notes.md、summary.md、source_documents/
- **`memory/INDEX.md`**：已追加新条目
- **`memory/cases/<existing_case_id>/case_entry.json`**（可能）：如果新案例与已有案例强相关，已有案例的 `related_cases` 与 `revision_history` 字段被更新

## Constraints

- **不可覆盖已有案例**：对已有案例条目只能追加 `related_cases` 和 `revision_history` 字段，不可修改其他结构化字段（除非用户明确要求修订，此时新增 `revision_<n>.md` 文件）
- **保留 runs/ 中的原始记录**：复制而非移动。`runs/` 中的中间产物是审计追踪的一部分
- **关联标注有据可循**：`related_cases` 中的每条关联必须能在 `summary.md` 的"相关案例"部分找到一句解释。不允许无解释的 case_id 罗列
- **vector embedding 为可选项**：如果 `scripts/search_memory.py` 可用且用户配置了 embedding API，运行向量化以支持语义检索；否则，`INDEX.md` + `case_entry.json` 的文本字段已足够支持关键词检索
- **不修改 AGENT.md 或 schemas/**：案例条目必须符合现有 schema 定义

## Examples

### Mini 示例：summary.md

```markdown
# 2022-04-15-shanghai-cell-delay

**一句话因果总结**：上海封控（2022年3-5月）导致港口作业停滞，一批280Ah LFP电芯从上海至洛杉矶的海运延误约35-50天；同期碳酸锂价格快速上涨可能削弱了供应商的履约积极性，两者共同构成了此次延误。

**主要影响因素**：物流, 原材料

**事件类型标签**：route_disruption (港口拥堵), material_price_shock (碳酸锂冲顶)

**时间窗口**：2022-03-01 至 2022-05-31

**整体置信度**：medium

**关键证据链接**：
- [E1] SCFI综合指数2022年4月维持在4,200-4,400点 — https://...
- [E3] 上海港4月集装箱作业能力降至约60% — https://...
- [E8] 电池级碳酸锂4月现货价约50万元/吨 — https://...

**相关案例**：
- `2021-09-shenzhen-port-congestion`：同为海运延误+原材料价格双重挤压，但口岸不同，强匹配维度命中 2/3

**创建日期**：2026-05-21
```

### Mini 示例：INDEX.md 追加行

```markdown
| 2022-04-15-shanghai-cell-delay | 上海封控致LFP电芯海运延误35-50天，碳酸锂价格同步冲顶 | 物流, 原材料 | 2021-09-shenzhen-port-congestion | 2026-05-21 |
```
