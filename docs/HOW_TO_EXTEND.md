# 如何扩展本仓库

本仓库设计为可扩展的声明式智能体框架。以下说明如何在不写代码的前提下添加新的能力。

## 添加新的技能（Skill）

### 场景一：添加新的处理阶段

如果论文设计的五阶段工作流需要扩展（例如未来增加"阶段六：类比预警匹配"），按以下步骤操作：

1. **创建 SKILL.md**
   ```bash
   mkdir -p skills/stage6-analogy-alert/
   ```
   从任一已有 SKILL.md 复制模板结构（# Skill: / ## When to invoke / ## Inputs / ## Steps / ## Outputs / ## Constraints / ## Examples），填充新阶段的具体内容。

2. **在 AGENT.md 中注册**
   在 AGENT.md 的"五阶段工作流"章节追加第 6 个小节，描述新阶段的触发条件与产出。同时更新"P6 五阶段不可跳跃"原则为"P6 六阶段不可跳跃"。

3. **定义新 Schema（如需要）**
   如果新阶段产出新的结构化数据，在 `schemas/` 下新增对应的 JSON Schema 文件。

4. **添加示例**
   在 `inputs/example/` 下补充一个能触发新阶段的示例输入，在 `memory/cases/` 下补充对应的示例输出。

5. **更新文档**
   更新 `docs/PAPER_REFERENCE.md` 添加新论文章节↔新文件的对照行。更新 `docs/ARCHITECTURE.md` 中的工作流图。

### 场景二：添加新的工具（Tool）

如果论文梳理的影响因素发生变化（例如增加了"地缘政治风险"作为第五类因素），按以下步骤操作：

1. **创建 tool SKILL.md + 可选静态数据**
   ```bash
   mkdir -p skills/tool-geopolitics/data/
   ```
   按四类现有工具的统一模板创建 `SKILL.md`。如果该工具有可预编译的参考数据（如某指数的历史序列），放入 `data/` 子目录。

2. **在 stage3 SKILL.md 中注册**
   将新工具的名称加入 `skills/stage3-retrieve-evidence/SKILL.md` 的强制检索循环中：
   ```
   对于 [logistics, materials, projects, policy, geopolitics] 中的每类因素 f:
   ```

3. **更新 AGENT.md**
   在 AGENT.md §2 P1 中将"四类影响因素"改为"五类影响因素"。在 §3 阶段三的工具调用顺序中追加新工具。

4. **更新约束文档**
   如果新工具触及了现有约束（如是否需要强制检索、检索空白如何记录），在对应的 SKILL.md Constraints 节中明确。

5. **更新文档**
   更新 `docs/PAPER_REFERENCE.md`、`docs/ARCHITECTURE.md` 中的工具集推导图。

### 场景三：修改已有技能的步骤

1. **先读 DECISIONS.md**：确认此次修改是否涉及对论文设计或 AGENT.md 的偏离。如有偏离，先在 `DECISIONS.md` 中追加一条记录。
2. **编辑对应的 SKILL.md**：仅修改 Steps 和/或 Constraints 节。
3. **运行回归测试**：使用 `datasets/` 下的合成案例测试修改后的智能体行为是否仍然合理。
4. **更新 PAPER_REFERENCE.md**：如果修改涉及论文的某个章节对应的实现，更新对照表中的说明。

## 添加新的 Schema

1. 在 `schemas/` 下创建 `<name>.schema.json`，遵循 JSON Schema Draft 2020-12
2. 必须在文件中包含 `$id`、`$schema`、`title`、`description`、`required` 五个字段
3. 在对应的 SKILL.md 中引用新 schema 作为产出格式约束
4. 更新 `docs/PAPER_REFERENCE.md` 中的 schema 对照

## 添加新的脚本

**在动手写脚本之前，先完成以下检查：**

1. 这个操作 LLM 能否直接完成？（如能 → 不该写脚本）
2. 是否有无法绕过的本地计算需求？（如加载 ML 模型）
3. 是否需要与外部系统交互？（如数据库连接）

如果三项都指向"需要脚本"：
1. 在 `DECISIONS.md` 中记录理由
2. 在 `scripts/` 下创建脚本
3. 在 `scripts/README.md` 中追加一行说明

## 为新用户准备的工作清单

如果你修改了仓库后 push 到 GitHub，确保新用户 clone 后能直接使用：

- [ ] `AGENT.md` 是用户进入后的第一个接触点，它的启动协议（§8）是否仍然正确？
- [ ] `README.md` 的 30 秒上手是否能走通？
- [ ] `inputs/example/` 下的示例是否仍然能触发完整五阶段流程？
- [ ] `skills/` 下每个 SKILL.md 的 Examples 节是否仍然有效？
- [ ] 如果新增了脚本，`scripts/README.md` 是否更新了依赖说明？
