# 论文章节 ↔ 仓库文件对照表

本文档建立了论文《Improving Battery Supply Chain Resilience and Efficiency in the Renewable Energy Industry》各章节与本仓库文件之间的明确对应关系，便于读者在论文与实现之间双向导航。

## Chapter 2：理论基础与文献综述

| 论文章节 | 对应仓库文件 | 说明 |
|:---|:---|:---|
| §2.1.1 涟漪效应 → BESS 四重影响因素 | `AGENT.md` §1, §2 (P1) | 四重影响因素（物流—原材料—合同/项目—合规/政策）是智能体强制跨因素检索（P1）的理论直接来源 |
| §2.1.2 从四重影响因素到工具设计 | `AGENT.md` §2 (P1); `skills/tool-logistics/SKILL.md`, `skills/tool-materials/SKILL.md`, `skills/tool-projects/SKILL.md`, `skills/tool-policy/SKILL.md` | 三条工具设计原则（证据完整性/因素到证据类型/跨因素交叉验证）直接映射为四类专用工具 + 阶段三的强制循环 |
| §2.2 动态能力理论 | `AGENT.md` §1, §6 | 智能体定位于"感知"与"重构（学习）"的外部增强器：中断分析＝感知，案例复用＝组织学习 |
| §2.2.1 组织知识外化与组织记忆 | `AGENT.md` §4, §6 (场景 B, C); `skills/stage5-write-memory/SKILL.md` | "内隐→外显"转化对应阶段五的案例沉淀；"保留与提取"对应 INDEX.md + search_memory.py |
| §2.3 AI 在 SCM 中的三代演进 | `README.md` "它是什么/不是什么" | 将本智能体定位为第三代 Agentic AI 的探索性概念设计 |

## Chapter 3：BESS 行业风险格局与现有工具分析

| 论文章节 | 对应仓库文件 | 说明 |
|:---|:---|:---|
| §3.1 BESS 上游供应链结构性特征 | `schemas/event_skeleton.schema.json` 中的 `materials` 枚举；`skills/tool-materials/SKILL.md` 中的物料-矿物对照表 | 四个层级（电芯→模组→电力电子→温控消防）映射为 schema 中的物料类别枚举 |
| §3.2 风险近期演化 (2023–2025) | `skills/tool-policy/data/policy_timeline.md` | USTR 关税升级、石墨管制、电池护照等新近政策节点均已收录 |
| §3.3 现有商业工具概览 | (无直接文件映射) | 论文中描述性介绍的工具（Resilinc, Kinaxis, Coupa, o9）用于对比说明本设计的差异化定位 |
| §3.4 Gap 1: 跨因素分析缺失 | `skills/stage3-retrieve-evidence/SKILL.md` 强制循环 + 交叉验证 | 论文指出的"理论层多因素 vs 工具层单一维度"鸿沟，通过阶段三的 N×4 强制检索结构在架构层直接回应 |
| §3.4 Gap 2: 私域数据外化缺失 | `AGENT.md` §1 (身份与目标); §5 (场景 A 新增分析) | 本智能体的核心价值主张——将非结构化中断经验转化为结构化因果案例 |

## Chapter 4：AI 智能体设计

| 论文章节 | 对应仓库文件 | 说明 |
|:---|:---|:---|
| §4.1 总体架构：单一 Agent + 阶段化工具链 | `AGENT.md` §1, §3 | 架构由三层组成：接口层(inputs/)、核心层(AGENT.md + skills/)、工具与存储层(skills/tool-*/ + memory/) |
| §4.2.1 阶段一：输入解析 | `skills/stage1-parse-input/SKILL.md`; `schemas/event_skeleton.schema.json` | "事实 vs 主观叙述"四类区分：schema 中的 observations/user_claims/inferred_clues/unknown_fields |
| §4.2.2 阶段二：事件推理 | `skills/stage2-reason-events/SKILL.md`; `schemas/hypothesis.schema.json` | "何时—何处—为何—何种影响"四问框架 + 3-5 条假设约束 |
| §4.3.3 阶段三：证据检索 | `skills/stage3-retrieve-evidence/SKILL.md` + 全部四个 `skills/tool-*/SKILL.md`; `schemas/evidence_item.schema.json` | 工具集的推导（从影响因素到证据类型）、强制循环、检索空白记录、跨因素交叉验证 |
| §4.3.4 阶段四：因果综合 | `skills/stage4-synthesize-causal/SKILL.md`; `schemas/causal_chain.schema.json` + `schemas/impact_estimates.schema.json` | [Ex] 引用规则、区间估计 [min, max]、rejected_hypotheses 记录 |
| §4.3.5 阶段五：写入记忆库 | `skills/stage5-write-memory/SKILL.md`; `schemas/case_entry.schema.json` | 从 runs/ 到 memory/ 的迁移、INDEX.md 更新、历史案例关联 |
| §4.4 案例数据库概念设计 | `memory/INDEX.md`; `schemas/case_entry.schema.json`; `scripts/search_memory.py` | 结构化元数据 + 向量索引混合模型、隐私与安全的本地优先原则 |

## Chapter 5：验证方案设计

| 论文章节 | 对应仓库文件 | 说明 |
|:---|:---|:---|
| §5.1 合成案例构造方法 | `datasets/raw_events/`; `datasets/synthetic_cases/`; `datasets/ground_truth/` | 三类维度多样性（事件类型/输入难度/信息完整性）的案例设计 |
| §5.2 技术性能指标 (M1–M4) | `results/metrics.py` (阶段 C 产物) | 输入解析准确率 / 因果归因准确率 / 工具调用有效性 / 输出一致性 |

## Chapter 6：局限与未来方向

| 论文章节 | 对应仓库文件 | 说明 |
|:---|:---|:---|
| §6.1 研究局限 | `DECISIONS.md`; `docs/ARCHITECTURE.md` 中的设计局限说明 | LLM 事后知识泄漏、私域数据合规等局限在仓库文档中诚实陈述 |
| §6.2 未来研究方向 | `docs/HOW_TO_EXTEND.md` | 类比预警模块、真实部署研究等扩展方向 |

---

> 此对照表随论文的修订而更新。最后更新：2026-05。
