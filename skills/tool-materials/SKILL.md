# Skill: Tool — 大宗商品与关键矿物价格检索 (Materials)

## When to invoke

当阶段三的强制检索循环执行到 `materials` 因素时调用本工具。触发条件：
- 当前假设的 `factors_involved` 中包含 `"materials"`
- 或者作为强制覆盖：即使假设未标注 materials，仍需至少发起一次检索

## What this tool does

按给定日期回查 BESS 价值链中关键原材料与中间品的公开价格数据，用于验证"原材料价格是否在同期出现异常波动"以及"价格冲击是否沿供应链向项目端传导"的因果链环节。

## Steps

### Step M.1: 确定检索时间窗口与关键物料

从 `event_skeleton.json` 的 `time_window` 和 `materials` 字段中提取：
- 时间窗口（向两侧各扩展 1 个月——原材料价格传导通常有滞后）
- 涉及的物料类别 → 确定需要检索的具体矿物品目

物料-矿物对应表：
| 事件中涉及的物料 | 需检索的矿物品目 | 关键价格指标 |
|:---|:---|:---|
| LFP 电芯 | 电池级碳酸锂 (Li₂CO₃ ≥99.5%) | 中国现货价 (万元/吨 RMB) |
| LFP 正极材料 | 磷酸铁 (FePO₄) | 前驱体价格指数 |
| 石墨负极 | 天然石墨/人造石墨 | 中国 FOB 价格 ($/t) |
| 电解液 | 六氟磷酸锂 (LiPF₆) | 中国现货价 (万元/吨 RMB) |
| NMC 电芯（如涉及） | 硫酸钴、硫酸镍、碳酸锂 | LME 钴/镍价 + 碳酸锂价 |

### Step M.2: 分项检索

按以下优先级依次发起 WebSearch：

**M.2.1 电池级碳酸锂现货价**

检索关键词模板：
```
battery grade lithium carbonate price China {YYYY-MM} SMM
电池级碳酸锂 现货价格 {YYYY}年{M}月
lithium carbonate spot price CIF North Asia {YYYY-MM}
```

关注指标：
- 中国电池级碳酸锂现货价（万元/吨 RMB）
- CIF 北亚/欧洲价格（如涉及进口）
- 月度/季度涨跌幅

关键阈值参考：
- < 10 万元/吨：低位（如 2020 年中、2024 年初）
- 10–20 万元/吨：中等
- 20–40 万元/吨：高位
- > 40 万元/吨：极端高位（2022 年下半年峰值约 60 万元/吨）

主要数据源：Shanghai Metals Market (SMM)、Asian Metal、Fastmarkets、Benchmark Mineral Intelligence。

**M.2.2 磷酸铁前驱体价格**

检索关键词模板：
```
iron phosphate FePO4 price battery grade {YYYY-MM}
磷酸铁 前驱体 价格 {YYYY}年
```

**M.2.3 石墨价格与出口管制动态**

检索关键词模板：
```
graphite price natural synthetic battery anode {YYYY-MM}
石墨 价格 负极材料 {YYYY}年
China graphite export controls battery {YYYY-MM}
中国 石墨 出口管制 {YYYY-MM}
```

特别关注：2023 年 10 月中国宣布石墨出口管制、2023 年 12 月 1 日正式生效这一节点的前后价格变化。

**M.2.4 六氟磷酸锂（电解液关键组分）价格**

检索关键词模板：
```
lithium hexafluorophosphate LiPF6 price China {YYYY-MM}
六氟磷酸锂 价格 {YYYY}年{M}月
```

**M.2.5 行业供需与价格展望报告**

检索关键词模板：
```
lithium market outlook supply demand {YYYY} {quarter}
battery raw material price forecast {YYYY}
BESS battery cost trend {YYYY}
```

### Step M.3: 交叉核对静态参考数据

读取本工具附带的静态参考数据 `data/battery_materials_prices.csv`，获取月度级别的碳酸锂、磷酸铁、石墨等价格基准值。作用同 tool-logistics 的静态数据——WebSearch 结果的首选校验锚点与兜底参考。

### Step M.4: 将结果填入 evidence_item

每次检索填充一个 evidence_item entry。格式同阶段三 Step 3.2 的标准模板。

特别注意：
- 价格数据具有精确性——在 `result_summary` 中标注具体日期和数值（如"2022年4月15日 SMM 电池级碳酸锂报价 50.2 万元/吨"），而非模糊描述（"碳酸锂很贵"）
- 如果 WebSearch 返回的价格信息与静态 CSV 数据有显著偏差（>15%），在 `result_summary` 中标注差异并优先采信 WebSearch 实时结果（因为静态 CSV 为月度均值）
- 如果检索返回空，按阶段三 Step 3.3 格式记录 `status: "empty"`

## Outputs

每次检索调用产出 1 条 `evidence_item`，写入 `runs/<case_id>/evidence_log.json`。原材料类条目应在 5–7 条之间（M.2.1–M.2.5 各至少 1 次）。

## Constraints

- **必须检索，不可跳过**：即使从 event_skeleton 看原材料似乎不是主要因素
- **价格数据必须有时间戳**：`result_summary` 中的每一个价格数字必须注明是哪一天/哪一周的数据。"约 50 万元/吨"是不够的——必须是"2022 年 4 月 15 日 SMM 报价 50.2 万元/吨"
- **区分现货价与合同价**：原材料现货价的波动可能不直接等于用户企业实际支付的价格（用户可能有长期合同锁定价格）。在 `support_or_refute_per_hypothesis` 的 rationale 中需要考虑这层区别
- **静态数据为兜底而非首选**：原则同 tool-logistics

## Reference Data

本工具附带的静态参考数据位于 `data/battery_materials_prices.csv`，包含 2019 年 1 月至 2024 年 12 月的电池级碳酸锂（中国现货，万元/吨）、磷酸铁前驱体、天然石墨（$/t）月度价格。
