# Skill: Tool — 通用网页检索 (General Web)

## When to invoke

通用网页检索是兜底工具。在下述情况下按需调用，**不可替代四类专用工具的强制检索**：

1. **四类专用工具检索均返回 empty**：更换检索策略后再次尝试（如使用更宽泛的关键词、去除域名过滤、尝试小语种媒体）
2. **需要验证地方性/突发性事件**：某特定工业园区的突发停电、地方交通管制通知、区域性洪水/地震对物流路线的影响——这些事件的报道通常不在航运指数或政策公报的覆盖范围内
3. **需要访问小语种媒体或非主流来源**：如韩语、日语、德语媒体的区域性报道中文/英文媒体未覆盖
4. **证据冲突需要第三方来源仲裁**：当四类工具返回的证据存在方向冲突时，用通用检索查找不受行业分类限制的额外信息源
5. **查找特定企业/特定事件的非系统性报道**：如某次行业会议上的发言、某投资银行的行业研究报告片段

## When NOT to invoke

- **不要替代 tool-logistics**：检索航运信息时，先执行 tool-logistics 的强制检索步骤（SCFI/CCFI/Drewry/港口等泊数据），然后再考虑通用检索
- **不要替代 tool-materials**：检索原材料价格时，先执行 tool-materials 的强制检索步骤
- **不要替代 tool-projects**：检索项目公告与财报时，先执行 tool-projects 的强制检索步骤
- **不要替代 tool-policy**：检索政策信息时，先执行 tool-policy 的强制检索步骤（定向至官方域名）
- **不要用"做一次通用检索"来偷懒**：通用检索不能跳过四类强制检索的逐因素覆盖

## Steps

### Step G.1: 确认前置条件

在调用本工具前，确认：
1. 四类专用工具的强制检索步骤已全部完成
2. 明确标识出哪些信息缺口是专用工具未能覆盖的
3. 通用检索的调用目的不是"重复四类工具已有的检索"

### Step G.2: 构造检索策略

通用检索不限制域名和来源类型，但应采用以下策略提高信噪比：

**检索策略 A — 宽泛关键词 + 时间窗口**：
```
{event_description} {YYYY} {month} supply chain impact
BESS battery delay {port_name} {YYYY-MM}
```

**检索策略 B — 定向至特定信息类型**：
```
{company_name} investor call transcript {YYYY-Q}
{industry_event} presentation slides {YYYY}
site:linkedin.com {company_name} supply chain {YYYY}
```

**检索策略 C — 小语种覆盖**：
```
{港口名} 渋滞 {YYYY}年 (日语)
{Unternehmen} Batterie Lieferkette {YYYY} (德语)
```

**检索策略 D — 反事实搜索**：
```
# 如果四类工具均返回 empty，搜索"同期该地区是否有其他事件"
{location} {YYYY-MM} disruption event -covid -shipping
```

### Step G.3: 评估检索结果的可信度

通用检索返回的结果来自非标准化来源，需对每条结果做可信度评估：

| 来源类型 | 可信度 | 在 evidence_item 中的标注方式 |
|:---|:---|:---|
| 上市公司官方公告/财报 | 高 | `result_summary` 中标明"SEC Filing / 交易所公告" |
| 权威行业媒体（Reuters, Bloomberg, Energy Storage News） | 中高 | 标注媒体名称 |
| 一般新闻/博客/LinkedIn | 中低 | 标注"未经独立核实" |
| 论坛/社交媒体 | 低 | 仅在无其他来源时记录，明确标注"未经验证的社交媒体来源" |

### Step G.4: 将结果填入 evidence_item

每次通用检索填充一个 evidence_item entry。`tool` 字段填 `"tool-general-web"`。

在 `support_or_refute_per_hypothesis` 的 rationale 中，若证据来自低可信度来源，必须附带可信度声明——如 "LinkedIn 帖子提到某供应商延迟交付（未经验证，仅作参考）"。

## Outputs

每次调用产出 1 条 `evidence_item`。通用检索的条目数量不设上下限——按需使用，但每增加一条应能说明"为什么四类专用工具无法覆盖这一信息"。

## Constraints

- **不可替代四类强制检索**：本工具是兜底，不是捷径
- **低可信度来源的结果不影响高权重假设的方向判断**：一篇 LinkedIn 帖子不应该推翻 SCFI 时间序列数据和 SEC Filing 的综合证据方向
- **不在通用检索中做政策/价格/物流的"标配检索"**：这些是四类专用工具的职责。通用检索覆盖的是专用工具的设计范围之外的信息
- **标注可信度**：只要证据来源不是专用工具覆盖的标准化数据源，就要在 rationale 中标注可信度

## Examples

### 场景：某工业园区的突发停电导致电芯工厂停产

四类专用工具（logistics/materials/projects/policy）均无法覆盖这一地方性事件。此时通用检索发挥作用：

```
检索词: "{工业园区名} 停电 停产 {YYYY-MM}"
域名过滤: 无
结果摘要: "据当地新闻报道，XX工业园区于2024年3月12日因变电站故障停电约36小时，区内3家电芯配套企业被迫停产"
```

这条证据补充了"为什么供应商在那个时间窗口产能不足"的解释，是四类专用工具无法自行覆盖的信息类型。
