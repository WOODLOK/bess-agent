# Skill: Tool — 行业项目公告与财务披露检索 (Projects)

## When to invoke

当阶段三的强制检索循环执行到 `projects` 因素时调用本工具。触发条件：
- 当前假设的 `factors_involved` 中包含 `"projects"`
- 或者作为强制覆盖：即使假设未标注 projects，仍需至少发起一次检索

## What this tool does

检索 BESS/可再生能源行业的项目延期公告、上市公司财务披露中的供应链风险说明、以及行业统计报告中的项目完工率数据，用于验证"行业同期是否出现了项目集中延期"以及"合同层面的争议或违约条款是否被触发"的因果链环节。

## Steps

### Step P.1: 确定检索范围

从 `event_skeleton.json` 提取：
- `time_window`：向两侧各扩展 1 个季度——项目延期公告通常在事件发生后 1-2 个季度才出现在财报中
- `materials`、`locations`：用于限定行业细分（如 utility-scale BESS vs C&I storage）

### Step P.2: 分项检索

按以下优先级依次发起 WebSearch：

**P.2.1 主要 BESS 集成商/开发商的财报风险披露**

检索关键词模板：
```
{company_name} 10-Q 10-K supply chain risk disclosure {YYYY}
{company_name} quarterly report delay battery storage {YYYY-Q}
{company_name} 年报 供应链 风险 延误 {YYYY}
```

核心检索对象（BESS 行业主要公开上市企业）：
- **Fluence Energy** (NASDAQ: FLNC) —— 全球最大的 BESS 集成商之一，SEC 10-Q/10-K 中常披露供应链中断影响
- **NextEra Energy** (NYSE: NEE) —— 美国最大可再生能源开发商
- **AES Corporation** (NYSE: AES) —— 与 Fluence 合资的 BESS 开发商
- **Wärtsilä** (HEL: WRT1V) —— 欧洲主要 BESS 集成商
- **Tesla Energy** —— 非独立上市但季度财报中含储能业务数据
- **CATL** (SZ: 300750) —— 全球最大 LFP 电芯制造商，年报中披露产能与交付数据

**P.2.2 行业项目延期与取消的公开报道**

检索关键词模板：
```
battery storage project delay cancellation {YYYY}
BESS project delayed supply chain {YYYY}
储能 项目 延期 供应链 {YYYY}年
energy storage installation delay {region} {YYYY}
```

关注来源：
- Energy Storage News (energystorage-news.com)
- PV Magazine (pv-magazine.com)
- Utility Dive (utilitydive.com)
- Reuters / Bloomberg 能源线

**P.2.3 行业统计数据（项目完工率与延期规模）**

检索关键词模板：
```
ACP clean power annual report {YYYY} project delays
EIA electric power monthly battery storage {YYYY-MM}
美国清洁能源协会 年报 项目延期 {YYYY}
IEA battery storage deployment {YYYY}
```

关键数据点：
- ACP 年报中的项目延期安装总量（GW）
- EIA 月度电力报告中公用事业级储能项目的计划 vs 实际完工日期
- IEA 年度电池与储能报告中的全球部署量与预测对比

**P.2.4 合同争议与不可抗力条款的行业讨论**

检索关键词模板：
```
force majeure battery supply contract {YYYY}
不可抗力 电池 供应 合同 {YYYY}
supply chain liquidated damages energy storage {YYYY}
battery price renegotiation contract dispute {YYYY}
```

这一检索方向关注的是"延误是否引发了合同层面的后果"——这可能与用户材料中的 renegotiation 信号直接相关。

**P.2.5 贸易信用与供应商财务健康**

检索关键词模板：
```
battery manufacturer financial distress {YYYY}
电芯 供应商 财务 困境 {YYYY}
supplier bankruptcy restructuring battery {YYYY}
```

仅在用户材料中有供应商行为异常信号时才进行此项检索（如"供应商突然失联"、"多次要求改付款条件"等）。

### Step P.3: 将结果填入 evidence_item

每条检索填充一个 evidence_item entry。特别注意：
- 财报类证据具有权威性——SEC filing 中的风险披露为经过法律审核的正式陈述，置信度高于行业媒体的猜测性报道
- 在 `result_summary` 中区分"企业自己承认的风险"和"第三方分析师的推测"
- 行业统计数据的时效性——ACP 年报通常在次年 Q1 发布，检索时需考虑数据可能存在 3-6 个月的发布滞后

## Outputs

每次检索调用产出 1 条 `evidence_item`。项目类条目应在 4–6 条之间（P.2.1–P.2.4 各至少 1 次，P.2.5 按需）。

## Constraints

- **必须检索，不可跳过**
- **财报证据优先采信**：SEC 10-Q/10-K 中的正式披露 > 行业媒体报道 > 分析师推测
- **注意数据发布时滞**：行业统计报告的发布日期与其覆盖的时间窗口之间存在 3-6 个月的滞后。检索时需要搜索"覆盖 YYYY 年的报告"而非"发布于 YYYY-MM 的报告"
- **不替代 legal review**：本工具检索的合同争议信息为公开报道层面，不构成法律意见。在最终摘要中说明"合同条款的具体适用需要法务审查"

## Reference Data

本工具无附带的静态参考数据——项目与财报信息的时效性强，依赖实时 WebSearch。
