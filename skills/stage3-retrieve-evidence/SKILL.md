# Skill: Stage 3 — 归因分析和证据检索 (Retrieve Evidence)

## When to invoke

当阶段二完成，`runs/<case_id>/hypotheses.json` 已生成（含 3–5 条候选假设），触发本阶段。

## Inputs

- **`runs/<case_id>/hypotheses.json`**：阶段二的完整输出，每条假设含 `factors_involved` 标注
- **`runs/<case_id>/event_skeleton.json`**：需要其中的 `time_window` 来锁定检索的时间范围
- **四个工具 SKILL.md**（按调用顺序读取）：
  1. `skills/tool-logistics/SKILL.md`
  2. `skills/tool-materials/SKILL.md`
  3. `skills/tool-projects/SKILL.md`
  4. `skills/tool-policy/SKILL.md`
  5. `skills/tool-general-web/SKILL.md`（兜底，按需调用）

## Steps

### Step 3.0: 初始化 evidence_log

在 `runs/<case_id>/` 下创建 `evidence_log.json` 的初始骨架：

```json
{
  "case_id": "<case_id>",
  "generated_at": "<ISO 8601>",
  "entries": [],
  "cross_factor_check": {}
}
```

每条证据条目（entry）的结构遵循 `schemas/evidence_item.schema.json`。

### Step 3.1: 强制检索循环

这是整个智能体工作流中最关键的步骤。执行以下强制循环：

```
对于 hypotheses.json 中的每条假设 H{n}:
  对于 [logistics, materials, projects, policy] 中的每类因素 f:
    如果 H{n}.factors_involved 中包含 f:
      读取 skills/tool-{f}/SKILL.md
      按其指示执行至少 1 次检索调用
      将每次检索的结果写入 evidence_log.json 的一个 entry
      在 entry.support_or_refute_per_hypothesis 中标注对该假设的方向
    如果 H{n}.factors_involved 中不包含 f:
      仍执行至少 1 次检索调用（违反直觉但必要——假设可能遗漏了某个因素）
      标注方向时特别关注：该因素是否有证据"意外出现"？
```

**强制规则**：
- 每条假设 × 每类因素 = 至少 1 次检索调用。5 条假设 × 4 类因素 = 至少 20 次调用
- 即使某类因素的检索预期为 null，也必须实际发起检索，然后将结果记录为 `status: "empty"`
- `status: "empty"` 本身就是有价值的信息——"某类因素在此次中断中不是主要传导通道"是一条合法的因果推断，但它必须被显式记录，而非被省略

### Step 3.2: 每个 tool 的检索流程

读取对应的 `skills/tool-{f}/SKILL.md` 后，每次调用按以下模板执行：

1. **构造 query**：结合 `event_skeleton.json` 的 `time_window`、`locations`、`materials` 字段 + 当前假设的 `why` 描述，生成具体的检索关键词
2. **发起检索**：使用 Claude Code / Codex 内置的 WebSearch 工具
3. **记录结果**：无论检索是否有结果，都填充以下字段：
   ```json
   {
     "evidence_id": "E{自增序号，从E1开始}",
     "tool": "tool-{logistics|materials|projects|policy|general-web}",
     "query": {
       "search_terms": "<实际使用的检索词>",
       "time_filter": "<时间过滤条件>",
       "domain_filter": "<域名过滤条件>"
     },
     "result_summary": "<有结果写摘要，无结果写'无相关结果'>",
     "support_or_refute_per_hypothesis": {
       "H1": { "hypothesis_id": "H1", "direction": "support|refute|neutral", "rationale": "..." },
       "H2": { "hypothesis_id": "H2", "direction": "support|refute|neutral", "rationale": "..." }
     },
     "retrieved_at": "<ISO 8601>",
     "status": "success|empty|failed",
     "source_url": "<URL if applicable>"
   }
   ```

### Step 3.3: 检索空白的记录格式

当某次检索返回空结果时，**绝不能**悄无声息地跳过。按以下格式显式记录：

```json
{
  "evidence_id": "E15",
  "tool": "tool-policy",
  "query": {
    "search_terms": "UFLPA customs seizure battery cell 2022 Q2",
    "time_filter": "2022-03-01 to 2022-06-30",
    "domain_filter": "ustr.gov, cbp.gov"
  },
  "result_summary": "检索为空：在指定时间窗口未发现UFLPA相关电池电芯查扣执法记录",
  "support_or_refute_per_hypothesis": {
    "H5": { "hypothesis_id": "H5", "direction": "refute", "rationale": "如果UFLPA执法在此期间已显著影响电池供应链，应能找到相关报道或执法公告，实际检索为空降低了H5的先验概率" }
  },
  "retrieved_at": "2026-05-21T15:00:00Z",
  "status": "empty",
  "source_url": null
}
```

关键：`status: "empty"` + `direction: "refute"` 的组合是有意义的——"没找到证据"是降低某个假设权重的合法理由。

### Step 3.4: 跨因素交叉验证

四类强制检索全部完成后，执行跨因素交叉验证。对**每一条候选假设**，检查：

1. **多因素证据方向一致性**：
   - 如果 H1 在 logistics, materials, projects 三类因素上均获得 `direction: "support"` → 标注为 `consistent`，该假设的可信度增强
   - 如果 H2 在 logistics 上获得 support，但在 projects 和 policy 上获得 refute → 标注为 `partially_conflicting`，需要进一步审视物流证据的强度，或者 H2 的因果链描述需要修正
   - 如果 H3 在多个因素上出现方向相反的 strong 证据 → 标注为 `highly_conflicting`，这是高价值信号——说明原先的因果假设可能把两个独立事件错误地连接在一起

2. **因素级证据空白统计**：
   - 某类因素在所有假设的检索中均为 `status: "empty"` → 该因素大概率不是本次中断的主要传导通道
   - 这是一个合法的因果推断，但必须被显式记录

3. **写入 `cross_factor_check` 字段**（在 `evidence_log.json` 顶层）：

```json
{
  "cross_factor_check": {
    "H1": {
      "consistency": "consistent",
      "supporting_factors": ["logistics", "materials", "projects"],
      "conflicting_factors": [],
      "empty_factors": ["policy"],
      "notes": "H1在物流和原材料两个因素上均获得了强支撑证据，港口拥堵数据与碳酸锂价格数据共同指向'复合型延误'。政策类检索为空，符合预期——UFLPA在2022年6月才正式生效，4月时应尚未对电芯清关产生实质影响"
    },
    "H2": {
      "consistency": "partially_conflicting",
      "supporting_factors": ["materials"],
      "conflicting_factors": ["logistics"],
      "empty_factors": [],
      "notes": "原材料价格证据强烈支撑'价格→履约压力'逻辑，但物流证据显示同期SCFI处于5,000+高位——港口拥堵确实是事实，供应商的'排产问题'说辞可能与港口拥堵混合在一起，难以完全剥离两者的各自贡献"
    }
  }
}
```

### Step 3.5: 写入并验证

1. 确认 `evidence_log.json` 的 `entries` 数组中每条假设的四类因素检索都已覆盖
2. 确认每条 entry 的 `status` 字段已正确标记（success / empty / failed）
3. 确认 `cross_factor_check` 对每条假设都给出了判断
4. 对照 `schemas/evidence_item.schema.json` 验证单条 entry 结构

## Outputs

- **`runs/<case_id>/evidence_log.json`**：包含所有检索条目的完整证据日志（通常 20+ 条目）+ 跨因素交叉验证结果。每个 entry 符合 `schemas/evidence_item.schema.json`。这是阶段四进行因果综合的唯一证据来源。

## Constraints

- **P1 强制跨因素检索**：不可跳过任何影响因素类别。检索为空不是跳过该类工具的理由——检索为空本身就是信息
- **P2 无记录不主张**：最终因果链中的任何事实性主张必须在 `evidence_log.json` 中有对应的 entry。这是本阶段最核心的约束
- **检索空白显式记录**：`status: "empty"` 的条目与 `status: "success"` 的条目同等重要
- **工具间证据冲突不强行收敛**：冲突如实记录，留给阶段四去处理。不要在阶段三就"选边站"
- **不修改 skills/ 下的工具 SKILL.md**：只读取，不修改
- **通用兜底工具（tool-general-web）仅按需调用**：在以下情况才使用：(a) 四类专用工具返回 empty 后尝试不同的检索策略；(b) 需要验证地方性/突发性事件（如某工业园区停电）；(c) 需要访问小语种媒体或非主流来源。不允许用通用检索替代四类强制检索

## Examples

（完整示例需配合四个工具 SKILL.md 的调用，此处展示 evidence_log 中一条 entry 的格式）

```json
{
  "evidence_id": "E1",
  "tool": "tool-logistics",
  "query": {
    "search_terms": "SCFI Shanghai export container freight index April 2022",
    "time_filter": "2022-03-01 to 2022-06-30",
    "domain_filter": ""
  },
  "result_summary": "SCFI综合指数在2022年4月维持在4,200-4,400点区间，约为2019年均值的4.2倍。上海至美西航线即期运费约$8,000-$10,000/FEU。多家航运媒体报道上海港因封控导致集卡进港受限、仓库运转效率大幅下降",
  "support_or_refute_per_hypothesis": {
    "H1": { "hypothesis_id": "H1", "direction": "support", "rationale": "SCFI高位+港口封控报道直接支撑'港口延误'假设" },
    "H2": { "hypothesis_id": "H2", "direction": "neutral", "rationale": "运价高企本身不直接证明或反驳供应商的价格动机假设" },
    "H3": { "hypothesis_id": "H3", "direction": "support", "rationale": "物流端的强证据与H3'复合型延误'的判断一致" },
    "H4": { "hypothesis_id": "H4", "direction": "neutral", "rationale": "港口拥堵与供应商产能问题是两个独立维度" },
    "H5": { "hypothesis_id": "H5", "direction": "neutral", "rationale": "物流检索与合规假设无直接关联" }
  },
  "retrieved_at": "2026-05-21T14:45:00Z",
  "status": "success",
  "source_url": "https://example.com/scfi-april-2022-report"
}
```
