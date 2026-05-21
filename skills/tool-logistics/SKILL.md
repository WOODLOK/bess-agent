# Skill: Tool — 航运与物流指数检索 (Logistics)

## When to invoke

当阶段三的强制检索循环执行到 `logistics` 因素时调用本工具。触发条件：
- 当前假设的 `factors_involved` 中包含 `"logistics"`
- 或者作为强制覆盖：即使假设未标注 logistics，仍需至少发起一次检索

## What this tool does

按时间窗口回查全球集装箱航运市场的关键运价指数、港口效率数据与航线运力变化，用于验证"港口/航线中断是否导致了在途延误"这一因果链环节。

## Steps

### Step L.1: 确定检索时间窗口

从 `event_skeleton.json` 的 `time_window` 提取最早和最晚日期。将检索窗口向两侧各扩展 2 周（因为航运中断的影响通常在实际事件前 1-2 周开始显现——如船公司提前取消航次、货主提前抢舱位）。

### Step L.2: 分项检索

按以下优先级依次发起 WebSearch：

**L.2.1 SCFI 综合指数与分航线运价**

检索关键词模板：
```
SCFI Shanghai Containerized Freight Index {YYYY-MM} weekly
上海出口集装箱运价指数 {YYYY}年{M}月
```

关注指标：
- SCFI 综合指数点位（2019 年均值约 1,000 点为基准）
- 上海→美西、上海→美东、上海→欧洲三条主干航线的即期运价（$/FEU）
- 与事件时间窗口前后 2 个月的数据对比

关键阈值参考（用于快速判断是否处于"异常高位"）：
- SCFI < 1,200：正常区间
- SCFI 1,200–2,000：偏紧
- SCFI 2,000–3,500：显著紧张
- SCFI > 3,500：极端高位（2021Q3–2022Q3 的典型区间）

**L.2.2 CCFI 中国出口集装箱运价指数**

检索关键词模板：
```
CCFI China Containerized Freight Index {YYYY-MM}
中国出口集装箱运价指数 {YYYY}年{M}月
```

CCFI 与 SCFI 的区别：SCFI 反映即期运价（spot），CCFI 包含合同运价（contract），两者联合看可以判断"合同价 vs 现货价"的偏离程度。

**L.2.3 Drewry World Container Index**

检索关键词模板：
```
Drewry World Container Index {YYYY} {month}
Drewry container freight rate Shanghai Los Angeles {YYYY}
```

**L.2.4 港口拥堵与等泊数据**

检索关键词模板：
```
{port_name} congestion waiting time {YYYY-MM}
{港口名} 拥堵 船舶等待 {YYYY}年{M}月
```

针对 BESS 供应链的关键港口：
- 中国出口端：上海港（洋山+外高桥）、宁波舟山港、深圳港（盐田+蛇口）
- 北美进口端：洛杉矶港/长滩港（LA/LB）、萨凡纳港、休斯顿港
- 欧洲进口端：鹿特丹港、汉堡港、安特卫普港

特定场景：
- 2022 年 3–5 月：上海封控期间港口作业数据
- 2021 年：LA/LB 港外锚地等泊船舶数量（峰值曾达 100+ 艘）
- 2023 年 12 月起：红海危机后绕航好望角对航程时间的影响

**L.2.5 航线运力与船期可靠性**

检索关键词模板：
```
container shipping schedule reliability {YYYY-Q}
blank sailings {route} {YYYY-MM}
全球集装箱船期准班率 {YYYY}年
```

关注来源：Sea-Intelligence 的 Global Liner Performance 报告、航运公司官网的船期公告。

### Step L.3: 交叉核对静态参考数据

在发起 WebSearch 的同时，读取本工具附带的静态参考数据 `data/scfi_ccfi_history.csv`，获取月度级别的 SCFI/CCFI 基准值作为检索结果的验证锚点。静态数据的作用：
- 在 WebSearch 结果不可用或不完整时，提供兜底参考
- 当 WebSearch 返回数据与静态数据出现显著偏差时，在 `result_summary` 中标注差异

### Step L.4: 将结果填入 evidence_item

每次检索（L.2.1–L.2.5 各计为一次独立调用）填充一个 evidence_item entry，格式严格遵循 `schemas/evidence_item.schema.json`。

示例：
```json
{
  "evidence_id": "E1",
  "tool": "tool-logistics",
  "query": {
    "search_terms": "SCFI Shanghai Containerized Freight Index April 2022 weekly",
    "time_filter": "2022-03-15 to 2022-05-15",
    "domain_filter": ""
  },
  "result_summary": "SCFI综合指数4月1日报4,348.07点，4月8日报4,263.66点，4月15日报4,228.65点，4月22日报4,195.98点。整体维持4,200点以上高位，约为2019年均值(1,000点)的4.2倍。上海至美西航线即期运价约$8,500-$9,500/FEU",
  "support_or_refute_per_hypothesis": {
    "H1": { "hypothesis_id": "H1", "direction": "support", "rationale": "SCFI4,200+高位直接支撑'港口拥堵导致运价飙升'的判断" }
  },
  "retrieved_at": "2026-05-21T14:45:00Z",
  "status": "success",
  "source_url": "https://..."
}
```

如果某次检索返回空结果（如特定港口的等泊数据未公开），按阶段三 Step 3.3 的格式记录为 `status: "empty"`。

## Outputs

每次检索调用产出 1 条 `evidence_item`，写入 `runs/<case_id>/evidence_log.json` 的 `entries` 数组。物流类条目应在 4–6 条之间（L.2.1–L.2.5 各至少 1 次 + 可能的补充检索）。

## Constraints

- **必须检索，不可跳过**：即使从 event_skeleton 看物流似乎不是主要因素，仍需完成本工具的强制检索——"检索为空"才能证明物流不是主要传导通道
- **时间窗口精确匹配**：检索必须使用 event_skeleton 中的时间范围，不可使用"大约那段时间"这样的模糊描述
- **优先使用公开可查的免费源**：SCFI 周度数据在多个财经网站（如 investing.com、tradingeconomics.com）上有免费历史记录；Drewry 的详细报告为付费产品，但新闻摘要通常免费可查
- **静态数据为兜底而非首选**：WebSearch 实时结果优先于静态 CSV；仅当 WebSearch 失败时使用 CSV 中的月度近似值，并显式标注"基于静态参考数据"

## Reference Data

本工具附带的静态参考数据位于 `data/scfi_ccfi_history.csv`，包含 2019 年 1 月至 2024 年 12 月的 SCFI 综合指数与 CCFI 综合指数月度均值。
