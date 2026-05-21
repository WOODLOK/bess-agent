# Skill: Tool — 政策档案与监管公告检索 (Policy)

## When to invoke

当阶段三的强制检索循环执行到 `policy` 因素时调用本工具。触发条件：
- 当前假设的 `factors_involved` 中包含 `"policy"`
- 或者作为强制覆盖：即使假设未标注 policy，仍需至少发起一次检索

## What this tool does

按时间窗口检索指定官方来源的政策公告、法律文件与海关执法记录，用于验证"是否有新的政策/法规同期生效或公布，并对供应链产生实质性影响"的因果链环节。

## Steps

### Step P.1: 确定检索时间窗口

从 `event_skeleton.json` 的 `time_window` 提取最早和最晚日期。政策检索的窗口需要向**前**扩展 6 个月——政策的公布日（announcement）与生效日（effective date）之间通常有数月的过渡期，只查生效日会漏掉公布日的市场预期反应。

### Step P.2: 与静态政策时间线对照

在开始 WebSearch 之前，先读取本工具附带的静态参考数据 `data/policy_timeline.md`，确定事件时间窗口前后是否有已知的政策节点。如果事件日期落在某个已知政策节点的 ±3 个月内，该政策应成为本轮检索的重点方向。

### Step P.3: 分项检索

按以下优先级依次发起 WebSearch。所有检索必须在查询中或域名过滤中**定向至官方来源**。

**P.3.1 美国 301 条款关税（USTR）**

检索关键词模板：
```
USTR section 301 tariff battery energy storage {YYYY}
USTR Federal Register lithium-ion battery tariff {YYYY-MM}
美国贸易代表办公室 301 关税 锂电池 储能 {YYYY}
```

域名过滤：`ustr.gov`, `federalregister.gov`

关键节点参考（来自 policy_timeline.md）：
- 2018–2019 年：301 关税第一轮（List 3 覆盖部分电池产品）
- 2022 年 5 月：USTR 启动四年审查
- 2024 年 5 月：USTR 宣布储能电池关税从 7.5% 提至 25%（2026 年）

**P.3.2 IRA / FEOC 相关规则**

检索关键词模板：
```
Inflation Reduction Act section 45X battery manufacturing {YYYY}
IRA FEOC foreign entity of concern battery guidance {YYYY-MM}
Treasury Department IRA battery sourcing requirements {YYYY}
```

域名过滤：`irs.gov`, `treasury.gov`, `energy.gov`, `federalregister.gov`

关键节点参考：
- 2022 年 8 月 16 日：IRA 签署生效
- 2023 年 3 月：财政部发布 IRA 电池采购要求拟议规则
- 2023 年 12 月：FEOC 拟议规则发布
- 2024 年 5 月：FEOC 最终规则发布

**P.3.3 UFLPA 执法**

检索关键词模板：
```
UFLPA Uyghur Forced Labor Prevention Act enforcement battery supply chain {YYYY-MM}
CBP detention battery polysilicon UFLPA {YYYY}
UFLPA 维吾尔强迫劳动预防法 执法 电池 {YYYY}
```

域名过滤：`cbp.gov`, `dhs.gov`, `federalregister.gov`

关键节点参考：
- 2021 年 12 月：UFLPA 签署
- 2022 年 6 月 21 日：UFLPA 正式生效，"可反驳推定"机制启动
- 2022 年 Q3–Q4 起：CBP 开始对太阳能光伏产品实施 UFLPA 扣留，电池行业的审查随后跟进

**P.3.4 欧盟电池法规与 CBAM**

检索关键词模板：
```
EU Battery Regulation 2023/1542 requirements timeline {YYYY}
欧盟 电池法规 2023/1542 碳足迹 电池护照 {YYYY}
EU CBAM carbon border adjustment mechanism battery {YYYY}
```

域名过滤：`europa.eu`, `eur-lex.europa.eu`, `ec.europa.eu`

关键节点参考：
- 2023 年 7 月 28 日：EU Battery Regulation (2023/1542) 正式通过
- 2024 年 2 月 18 日：法规全面生效，碳足迹声明要求开始分阶段实施
- 2025 年 8 月 18 日：电动汽车电池碳足迹声明强制
- 2026 年 8 月 18 日：工业电池碳足迹声明强制
- 2027 年 2 月 18 日：电池护照（Battery Passport）要求生效

**P.3.5 中国出口管制与产业政策**

检索关键词模板：
```
中国 石墨 出口管制 商务部 公告 {YYYY}
China graphite export controls MOFCOM announcement {YYYY-MM}
中国 锂电池 出口 退税 调整 {YYYY}
```

域名过滤：`mofcom.gov.cn`, `customs.gov.cn`, `gov.cn`

关键节点参考：
- 2023 年 10 月 20 日：商务部与海关总署宣布石墨出口管制
- 2023 年 12 月 1 日：石墨出口管制正式生效
- 2024 年 12 月：中国宣布调整部分电池产品出口退税

### Step P.4: 将结果填入 evidence_item

每条检索填充一个 evidence_item entry。政策类条目特别注意：

- **区分"公布日"与"生效日"**：在 `result_summary` 中明确标注"YYYY-MM-DD 公布，YYYY-MM-DD 生效"
- **引用具体法规编号**：如 EU 2023/1542、IRA Section 45X、19 USC § 1307（UFLPA 基础法条）
- **官方来源优先**：.gov / .eu / .europa.eu / .gov.cn 的结果优先采信；新闻媒体的"政策解读"作为补充但标注为二手来源

## Outputs

每次检索调用产出 1 条 `evidence_item`。政策类条目应在 5–7 条之间（P.3.1–P.3.5 各至少 1 次 + 可能的补充检索）。

## Constraints

- **必须检索，不可跳过**
- **定向至官方域名**：政策检索必须优先选择 .gov、.eu、.europa.eu、mofcom.gov.cn 等官方源。避免仅依赖新闻媒体的政策总结
- **区分政策阶段**：政策从"提案 → 通过 → 生效 → 执法"是一个过程。一个在"提案阶段"的政策不会直接造成清关延误，但可能已经在影响进口商的预审查行为（如 UFLPA 在 2022 年 6 月生效前，进口商在 Q1 就已开始主动加强审查）
- **与 policy_timeline.md 交叉验证**：静态时间线提供了关键节点的精确日期，WebSearch 结果中出现的日期应与时间线对照——如有冲突，以官方公告日期为准

## Reference Data

本工具附带的静态参考数据位于 `data/policy_timeline.md`，包含 2018–2025 年关键政策节点的时间线（含 IRA、UFLPA、EU Battery Regulation 2023/1542、USTR 301 关税调整、中国石墨出口管制等）。
