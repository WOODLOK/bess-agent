# BESS Supply Chain AI Agent

将 BESS（电池储能系统）供应链的非结构化中断经验转化为可追溯、可复用、可检索的结构化因果案例的声明式 AI 智能体。

## 它是什么

一个 markdown + JSON schema 主导的 AI 智能体仓库。用户在 Claude Code 或 Codex 中提及 `AGENT.md` 即可激活智能体，将私域的供应链中断材料（合同、邮件、运输单据、会议纪要）解析为结构化因果案例并沉淀到本地记忆库。

## 快速启动

```bash
# 1. 克隆仓库
git clone https://github.com/<your-org>/bess-agent.git
cd bess-agent

# 2. 在 Claude Code 中激活智能体
# 打开 Claude Code，在对话中输入例如：
：@AGENT.md 分析我在 inputs/ 下放置的中断材料
：@AGENT.md  我们的一批 LFP 电芯 2023 年底从中国发欧洲时延误了 20 天是为什么

# 3. 将你的私域材料放入 inputs/ 目录，告诉智能体"分析这次中断"
```

## 三种主要使用场景

| 场景 | 说明 | 触发方式 |
|:---|:---|:---|
| **A — 新增分析** | 提交一份私域中断材料，智能体按五阶段流程完成因果分析并沉淀为案例 | 将材料放入 `inputs/`，说"分析这次中断" |
| **B — 检索历史** | 从已沉淀的案例记忆库中查找与当前问题最相似的历史案例 | "我们之前遇到过类似的延误吗？" |
| **C — 类比预警（实验性）** | 描述一个新近的疑似风险信号，智能体从历史案例中匹配最接近的经验并提示 | "红海危机又在扰动我们的发货" |

## 仓库目录速览

```
bess-agent/
├── AGENT.md                  # 主大脑：身份、工作原则、五阶段工作流
├── README.md                 # 本文件
├── DECISIONS.md              # 偏离设计的决策记录
├── inputs/                   # 用户放置待分析材料的位置
├── runs/                     # 中间运行产物
├── memory/                   # 案例记忆库（核心资产）
│   ├── INDEX.md              # 案例索引
│   └── cases/                # 各案例目录
├── skills/                   # 声明式技能集（五阶段 + 五类工具）
│   ├── stage1-parse-input/
│   ├── stage2-reason-events/
│   ├── stage3-retrieve-evidence/
│   ├── stage4-synthesize-causal/
│   ├── stage5-write-memory/
│   ├── tool-logistics/
│   ├── tool-materials/
│   ├── tool-projects/
│   ├── tool-policy/
│   └── tool-general-web/
├── schemas/                  # JSON Schema 定义
├── scripts/                  # 极少量辅助脚本（按需）
├── datasets/                 # 测试数据集（阶段 B 产物）
├── results/                  # 测试结果与报告（阶段 C 产物）
└── docs/                     # 架构与扩展文档
```

## 依赖说明

本仓库设计为零依赖启动——智能体的运行完全依赖 Claude Code / Codex 客户端内置的 LLM 与网页检索能力。仅当需要使用本地向量化检索历史案例时才需安装 `scripts/` 下的 Python 依赖（详见 [`scripts/README.md`](scripts/README.md)）。

## 贡献

本项目是硕士论文《Improving Battery Supply Chain Resilience and Efficiency in the Renewable Energy Industry》的概念验证实现。欢迎通过 Issue 和 PR 参与贡献。

## 许可证

MIT — 详见 [LICENSE](LICENSE)
