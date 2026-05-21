# M-3 里程碑报告：五个阶段技能 SKILL.md 全部完成

**完成日期**：2026-05-21

## 完成项

全部 5 个阶段技能 SKILL.md 已写入 `skills/<stage-name>/SKILL.md`。

## 各 SKILL.md 核心 Steps 摘要

### Stage 1 — Parse Input (`skills/stage1-parse-input/SKILL.md`)

**Steps 概览**：
1. **Step 1.1** 扫描输入源并生成 case_id（格式 `YYYY-MM-DD-<slug>`）→ 创建 `runs/<case_id>/`
2. **Step 1.2** 多模态内容提取——三条处理路径：文本直接读取、PDF 优先用 Read 工具原生读取（失败则退回到 `scripts/extract_pdf.py`）、图像优先用 Read 工具原生读取
3. **Step 1.3** 按信息性质四类区分（核心步骤）：
   - `observations`：可验证事实（含 source 引用）
   - `user_claims`：主观断言（含 needs_verification）
   - `inferred_clues`：推测线索（含 priority 标注）
   - `unknown_fields`：缺失信息（含 importance + suggested_source）
4. **Step 1.4** 填充结构化字段（time_window / parties / locations / materials）
5. **Step 1.5** 写入 `event_skeleton.json`，对照 schema 验证

**关键设计点**：
- 事实 vs 主观的明确区分规则：判断标准是"第三方看到这份材料是否会得出相同结论"
- `inferred_clues` 的 priority 直接驱动阶段二的假设优先级
- PDF/图像处理声明 LLM 优先原生读取，兜底才用脚本

### Stage 2 — Reason Events (`skills/stage2-reason-events/SKILL.md`)

**Steps 概览**：
1. **Step 2.1** 回溯宏观时间线——基于训练数据中的知识列出同期宏观事件（无需工具检索）
2. **Step 2.2** 生成 3–5 条候选因果假设，每条严格按"四问模板"构建：
   - (i) 何时 — 时间节点 + 宏观背景关联
   - (ii) 何处 — BESS 供应链的具体环节
   - (iii) 为何 — 事件→传导机制
   - (iv) 何种影响 — 解释力 + 盲区
3. **Step 2.3** 分配先验权重（0-1）：高权重（0.7-1.0）= 强线索 + 宏观吻合；低权重（0-0.4）= 弱线索但保留
4. **Step 2.4** 标注 `factors_involved`（logistics / materials / projects / policy），驱动阶段三的工具调度
5. **Step 2.5** 写入 `hypotheses.json`，验证数量 3-5

**关键设计点**：
- "四问"要求每条假设同时提供解释力和盲区（"无法解释哪些现象"）
- 先验权重不是结论，而是检索优先级分配
- 如果只有 2 条有力假设方向，第 3 条作为"反事实假设"补充

### Stage 3 — Retrieve Evidence (`skills/stage3-retrieve-evidence/SKILL.md`)（最关键）

**Steps 概览**：
1. **Step 3.0** 初始化 `evidence_log.json` 骨架
2. **Step 3.1** 强制检索循环——N 条假设 × 4 类因素 = 至少 4N 次检索调用：
   - 即使 `factors_involved` 中未包含某类因素，仍执行检索
   - 即使预期检索为空，仍实际发起检索
3. **Step 3.2** 每次检索按标准模板：构造 query → 发起 WebSearch → 记录到 evidence_log entry
4. **Step 3.3** 检索空白显式记录格式：`status: "empty"` + `direction: "refute"`（"没找到"也是降低假设权重的理由）
5. **Step 3.4** 跨因素交叉验证（四类检索全部完成后执行）：
   - 检查每假设的多因素证据方向一致性 → `consistent / partially_conflicting / highly_conflicting`
   - 统计因素级证据空白
   - 写入 `cross_factor_check`
6. **Step 3.5** 验证覆盖完整性

**关键设计点**：
- "检索空白显式记录"是理论与工具设计之间的关键桥梁——落实论文 2.1.2 节"证据完整性原则"
- `cross_factor_check` 的三种一致性判定是阶段四综合的核心输入
- 通用兜底工具仅按需调用，不允许替代四类强制检索

### Stage 4 — Synthesize Causal (`skills/stage4-synthesize-causal/SKILL.md`)

**Steps 概览**：
1. **Step 4.1** 审视证据全景——回答 5 个诊断问题（哪些假设被强化/削弱/哪些因素空白/冲突/整体质量）
2. **Step 4.2** 构建最终因果链——"事件 → 中间机制 → 现象"，每个事实性主张附 `[Ex]` 引用
3. **Step 4.3** 排除被反驳的假设——每条拒绝理由引用具体 `[Ex]`
4. **Step 4.4** 区间估计——delay / cost / compliance / project 四个维度，以 `[min, max]` + confidence 形式产出
5. **Step 4.5** 撰写 `uncertainty_notes.md`——证据空白清单 + 冲突未解决项 + 用户可补充信息 + 方法局限
6. **Step 4.6** 写入四个产出文件并自检

**关键设计点**：
- `[Ex]` 引用规则是 P2（无记录不主张）的直接落地
- "无法引用证据的主张 → [假设，待验证]" 显式标注
- `uncertainty_notes.md` 的"用户可补充信息"章节——主动告诉用户补充什么可以缩小不确定性
- 区间估计的 `basis` 字段强制说明估计依据

### Stage 5 — Write Memory (`skills/stage5-write-memory/SKILL.md`)

**Steps 概览**：
1. **Step 5.1** 在 `memory/cases/` 下创建 `<case_id>/` 目录
2. **Step 5.2** 从 `runs/` 复制（非移动）文件到 `memory/cases/`
3. **Step 5.3** 生成 `case_entry.json`——从五个阶段的产出物中提取结构化字段，按 schema 严格映射
4. **Step 5.4** 生成 `summary.md`——人工快速浏览入口（因果总结 + 影响因素 + 事件标签 + 关键证据链接 + 相关案例）
5. **Step 5.5** 与历史案例建立语义关联——按 AGENT.md §6 的强匹配/弱匹配维度对比，标注 `related_cases`，必要时反向更新已有案例
6. **Step 5.6** 更新 `INDEX.md`——按时间倒序插入新行
7. **Step 5.7** 复制源文档引用（不复制大文件，仅记录路径）
8. **Step 5.8** 向用户输出最终摘要

**关键设计点**：
- 复制而非移动——保留 `runs/` 作为审计追踪
- `related_cases` 的强匹配/弱匹配二维判断体系
- 反向关联更新已有案例（追加 `related_cases` + `revision_history`）
- 对已有案例的修改限于追加，不覆盖原始字段

## 已知问题

- 无。五个阶段的 Steps 均按 AGENT.md 第 3 节工作流和论文第 4 章设计一一对应。

## 给用户的检查清单

- [ ] Stage 1 的"四类区分"规则是否足够清晰、可操作？
- [ ] Stage 2 的"四问模板"是否能有效约束 LLM 的推理方向？
- [ ] Stage 3 的强制循环逻辑 + 检索空白记录格式是否能保证 P1（强制跨因素检索）的执行？
- [ ] Stage 4 的 `[Ex]` 引用规则和"无法引用则显式标注"是否能保证 P2（无记录不主张）？
- [ ] Stage 5 的案例迁移+关联+INDEX更新流程是否完整？
