# M-2 里程碑报告：所有 Schema 就绪

**完成日期**：2026-05-21

## 完成项

全部 6 个 JSON Schema（Draft 2020-12）已在 `schemas/` 下创建。

## Schema 字段汇总表

| Schema 文件 | 阶段 | 核心字段 | 与论文/AGENT.md 的对应 |
|:---|:---|:---|:---|
| `event_skeleton.schema.json` | 阶段一输出 | `case_id`, `time_window`(earliest/latest/precision), `parties`[](name/role/certainty), `locations`[](name/role/certainty), `materials`[](category/specification), `observations`[](field/value/source), `user_claims`[](claim/source), `inferred_clues`[](clue/basis/priority), `unknown_fields`[](field/importance) | AGENT.md §3 阶段一必含字段 + 四类内容区分；论文 4.2.1 节事件骨架字段 |
| `hypothesis.schema.json` | 阶段二输出 | `case_id`, `hypotheses[3-5]` 每条含 `id`(H1-H5), `summary`, `when`(time_window/macro_context), `where_in_chain`, `why`, `so_what`, `prior_weight`(0-1), `factors_involved`[] | AGENT.md §3 阶段二"四问 + 先验权重"；论文 4.2.2 节候选因果假设 |
| `evidence_item.schema.json` | 阶段三单条证据 | `evidence_id`(E1..), `tool`, `query`(search_terms/time_filter/domain_filter), `result_summary`, `support_or_refute_per_hypothesis`{}, `retrieved_at`, `status`(success/empty/failed), `error_detail`, `source_url` | AGENT.md §3 阶段三"三元结构 + 标注 + 检索空白记录"；论文 4.3.3 节工具调用证据 |
| `causal_chain.schema.json` | 阶段四输出 | `root_cause`(event/factor_category/confidence), `intermediate_mechanisms`[](step/mechanism/evidence_ids), `observed_outcomes`[], `evidence_references`[], `cross_factor_consistency`, `rejected_hypotheses`[] | AGENT.md §3 阶段四"链式叙述+证据引用"；论文 4.3.4 节因果综合 |
| `impact_estimates.schema.json` | 阶段四区间估计 | `delay`(range_days[min/max]/confidence), `cost`(description/range_percentage/confidence), `compliance`(risk_level/applicable_regulations/confidence), `project`(impact_description/confidence), `overall_confidence` | AGENT.md 工作原则 P4"区间估计而非伪精确"；论文 4.3.4 节影响量化 |
| `case_entry.schema.json` | 阶段五案例条目 | `case_id`, `creation_date`, `event_time_window`, `materials`[], `suppliers`[], `route`(origin/destination/transit_mode), `event_signature`[](type/subtype), `causal_chain_summary`, `impact_metrics`, `evidence_links`[], `confidence_level`, `source_documents`[], `related_cases`[], `cross_factor_check`, `revision_history`[] | AGENT.md §4 案例记忆库字段；论文 4.4 节数据模型表（case_id → source_documents 共 11 项必填字段 + related_cases + cross_factor_check + revision_history） |

## 与论文 4.4 节字段表的一致性验证

论文 4.4 节列出的 11 个核心结构化字段均已覆盖：

| 论文字段 | Schema 中对应 | 状态 |
|:---|:---|:---|
| `case_id` | `case_id` | 已覆盖 |
| `creation_date` | `creation_date` | 已覆盖 |
| `event_time_window` | `event_time_window` | 已覆盖 |
| `materials` | `materials` | 已覆盖 |
| `suppliers` | `suppliers` | 已覆盖 |
| `route` | `route` | 已覆盖 |
| `event_signature` | `event_signature` | 已覆盖 |
| `causal_chain_summary` | `causal_chain_summary` | 已覆盖 |
| `impact_metrics` | `impact_metrics` | 已覆盖 |
| `evidence_links` | `evidence_links` | 已覆盖 |
| `confidence_level` | `confidence_level` | 已覆盖 |
| `source_documents` | `source_documents` | 已覆盖 |

额外扩展字段：`related_cases`（语义关联）、`cross_factor_check`（跨因素交叉验证）、`revision_history`（修订追溯）——已在论文 2.1.2 节和 4.4 节中论述其必要性。

## 已知问题

- 无。所有 schema 均包含 `$id`, `$schema`, `title`, `description`, `required` 字段。

## 给用户的检查清单

- [ ] `event_skeleton` 的四类内容区分（observations / user_claims / inferred_clues / unknown_fields）是否合理？
- [ ] `hypothesis` 的 "四问" 结构是否与论文 4.2.2 一致？
- [ ] `evidence_item` 的 `support_or_refute_per_hypothesis` 多假设标注结构是否满足阶段三需求？
- [ ] `causal_chain` 的 `rejected_hypotheses` 字段是否必要？
- [ ] `impact_estimates` 的区间估计（min/max + confidence）是否符合 P4 原则？
- [ ] `case_entry` 的字段是否完整覆盖论文 4.4 节？
