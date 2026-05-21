# M-4 里程碑报告：五个工具 SKILL.md + 静态参考数据就绪

**完成日期**：2026-05-21

## 完成项

全部 5 个工具 SKILL.md 和 3 份静态参考数据已就位。

## 各工具 SKILL.md 核心 Steps 摘要

### tool-logistics (`skills/tool-logistics/SKILL.md`)

**检索流程**：5 个分项（L.2.1–L.2.5）
- L.2.1 SCFI 综合指数与分航线运价（上海→美西/美东/欧洲）
- L.2.2 CCFI 中国出口集装箱运价指数（SCFI vs CCFI 联合判断即期 vs 合同偏离）
- L.2.3 Drewry World Container Index
- L.2.4 港口拥堵与等泊数据（上海/宁波/深圳/LA-LB/鹿特丹/汉堡）
- L.2.5 航线运力与船期可靠性（blank sailings / schedule reliability）

**关键设计**：
- 附 SCFI 异常高位阈值表（<1,200 正常 → >3,500 极端高位）
- 针对 BESS 的港口列表（中国出口端 + 北美/欧洲进口端）
- 静态数据 `scfi_ccfi_history.csv` 作为兜底参考

### tool-materials (`skills/tool-materials/SKILL.md`)

**检索流程**：5 个分项（M.2.1–M.2.5）
- M.2.1 电池级碳酸锂现货价（SMM / Asian Metal / Fastmarkets）
- M.2.2 磷酸铁前驱体价格
- M.2.3 石墨价格与出口管制动态
- M.2.4 六氟磷酸锂（LiPF₆）价格
- M.2.5 行业供需与价格展望报告

**关键设计**：
- 物料→矿物品目对应表（LFP电芯→碳酸锂+磷酸铁+石墨+LiPF₆）
- 碳酸锂价格阈值表（<10 低位 → >40 极端高位）
- 价格精确性要求：每个数字必须有具体日期

### tool-projects (`skills/tool-projects/SKILL.md`)

**检索流程**：5 个分项（P.2.1–P.2.5）
- P.2.1 主要 BESS 集成商/开发商财报风险披露（Fluence / NextEra / AES / Wärtsilä / Tesla / CATL）
- P.2.2 行业项目延期与取消报道
- P.2.3 行业统计数据（ACP 年报 / EIA 月度电力报告）
- P.2.4 合同争议与不可抗力条款讨论
- P.2.5 贸易信用与供应商财务健康（按需）

**关键设计**：
- 6 家核心检索对象的完整列表
- 财报证据 > 行业媒体 > 分析师推测的采信层级
- 注意行业统计数据的发布时滞（3-6个月）

### tool-policy (`skills/tool-policy/SKILL.md`)

**检索流程**：5 个分项（P.3.1–P.3.5）
- P.3.1 美国 301 关税（USTR / Federal Register）
- P.3.2 IRA / FEOC 规则（IRS / Treasury / DOE）
- P.3.3 UFLPA 执法（CBP / DHS）
- P.3.4 欧盟电池法规与 CBAM（EUR-Lex / EU Official Journal）
- P.3.5 中国出口管制与产业政策（MOFCOM / 海关总署）

**关键设计**：
- 每项检索指定官方域名过滤
- 区分"公布日"与"生效日"
- 附 `policy_timeline.md` 作为精确节点对照

### tool-general-web (`skills/tool-general-web/SKILL.md`)

**调用场景**：明确"何时用"（4 种场景）和"何时不要用"（5 条禁止）
- 场景：四类工具全 empty / 地方性事件 / 小语种媒体 / 证据冲突仲裁 / 特定企业非系统报道
- 禁止：替代四类专用工具 / "偷懒式一次通用检索"

**关键设计**：
- 四种检索策略（宽泛 / 定向 / 小语种 / 反事实）
- 来源可信度五级评估表
- 低可信度来源的强制标注规则

## 静态参考数据

### scfi_ccfi_history.csv (72 行, 2019-01 → 2024-12)
```
date,SCFI_composite,CCFI_composite,SCFI_USWC_FEU,SCFI_USEC_FEU,SCFI_Europe_FEU,notes
2019-01,956.64,863.18,1974,3106,980,正常区间；春节前小高峰
2019-02,888.03,851.68,1745,2910,897,节后回落
...
2022-01,5109.45,...  ← SCFI 历史峰值
...
2024-12,1185.56,1004.27,1820,4050,1620,
```
覆盖周期：2019-01 至 2024-12，含 SCFI 综合指数、CCFI 综合指数、美西/美东/欧洲分航线 FEU 运价。

### battery_materials_prices.csv (72 行, 2019-01 → 2024-12)
```
date,lithium_carbonate_battery_grade_CNY_10k_per_ton,iron_phosphate_precursor_index_CNY_per_ton,natural_graphite_spherical_FOB_USD_per_ton,LiPF6_electrolyte_salt_CNY_10k_per_ton,notes
2019-01,7.95,10500,3200,11.2,补贴退坡过渡期
...
2022-11,60.00,...  ← 碳酸锂历史峰值
...
2024-12,9.50,10000,3650,10.2,
```
覆盖四种关键矿物/材料的价格月度序列，含碳酸锂冲顶（2022-11）和石墨管制（2023-12）等关键节点。

### policy_timeline.md (6 个政策板块)
- 一、美国 301 关税（8 个节点，2018-2026）
- 二、IRA / FEOC（6 个节点，2022-2025）
- 三、UFLPA（4 个节点，2021-2025）
- 四、EU Battery Regulation 2023/1542（7 个节点，2020-2027）
- 五、中国石墨出口管制（3 个节点，2023-2024）
- 六、其他重要政策与地缘事件（5 个节点，2020-2024）

每个节点含精确日期、事件描述、对 BESS 供应链的实质性影响说明。

## 已知问题

- 静态 CSV 数据基于公开报告的月度均值编制，非日度精确值。在 SKILL.md 中已明确：WebSearch 实时结果优先于静态 CSV
- policy_timeline.md 需年度更新（最后更新 2026-05）
- tool-projects 无静态数据（财报信息时效性太强，不适合预编译）

## 给用户的检查清单

- [ ] 四类专用工具的检索分项是否覆盖了论文 2.1.2 节定义的各类证据源？
- [ ] tool-policy 的域名定向（.gov / .eu / .europa.eu / mofcom.gov.cn）是否合理？
- [ ] tool-general-web 的"何时不用"规则是否能有效防止滥用通用检索替代强制检索？
- [ ] SCFI/CCFI 数据的月度值是否大致反映真实走势（特别是 2022-01 峰值和 2023-12 红海危机）？
- [ ] battery_materials_prices.csv 的碳酸锂峰值（2022-11 约 60 万元/吨）是否准确？
- [ ] policy_timeline.md 的关键节点是否有遗漏？
