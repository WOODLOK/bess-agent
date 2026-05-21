# 部署指南：发布到 GitHub

本文档说明如何将本仓库发布为一个公开的 GitHub 仓库，供其他 BESS 行业从业者或研究者 clone 使用。

## 发布前检查清单

在第一次 push 到 GitHub 之前，逐项确认：

### 内容完整性
- [ ] `AGENT.md` 九个小节均已填写且无占位符
- [ ] `README.md` 含完整版的快速开始 + 三场景 + 目录速览
- [ ] `skills/` 下的 10 个 SKILL.md（5 阶段 + 5 工具）均包含完整的 Steps
- [ ] `schemas/` 下的 6 个 JSON Schema 均通过 JSON Schema Draft 2020-12 验证
- [ ] `memory/INDEX.md` 至少含 1 行示例（供新用户理解格式）
- [ ] `inputs/example/` 下有可用的示例输入
- [ ] `memory/cases/example-*/` 下有对应的示例输出

### 安全性
- [ ] `.gitignore` 已包含 `runs/*`、`inputs/*`（除 `.gitkeep` 和 `example/`）、`.env`、`secrets/`
- [ ] 仓库中没有任何 API 密钥、token、密码
- [ ] 示例案例中的企业名和供应商名确认为虚构或已匿名化
- [ ] `DECISIONS.md` 不包含敏感的决策上下文

### 用户体验
- [ ] clone 后的第一步（`@AGENT.md`）能直接激活智能体
- [ ] `README.md` 的"30 秒上手"可运行
- [ ] 所有文档中的相对路径链接有效
- [ ] `scripts/README.md` 清楚说明了零依赖启动

## 发布步骤

```bash
# 1. 初始化 Git 仓库
cd bess-agent/
git init
git checkout -b main

# 2. 首次提交
git add .
git commit -m "Initial release: BESS supply chain AI agent — declarative repository"

# 3. 在 GitHub 上创建空仓库（不要勾选 README/LICENSE/.gitignore —— 我们已经有了）
#    假设仓库 URL 为 https://github.com/<your-org>/bess-agent

# 4. 关联远程并推送
git remote add origin https://github.com/<your-org>/bess-agent.git
git push -u origin main
```

## 推荐的 README Badge

在 `README.md` 顶部添加以下 badge（根据你的仓库实际 URL 调整）：

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Experimental](https://img.shields.io/badge/Status-Experimental-orange.svg)](https://github.com/<org>/bess-agent)
[![Claude Code Ready](https://img.shields.io/badge/Claude%20Code-Ready-blue.svg)](https://claude.ai/code)
```

## 克隆后第一次使用的 Checklist

给新用户的指引（可放在 README.md 的"30 秒上手"之后）：

```markdown
## 第一次使用

1. [ ] 打开本仓库目录
2. [ ] 在 Claude Code 中输入 `@AGENT.md`
3. [ ] 智能体应回复确认加载 + 询问来意（新增分析 / 检索历史 / 探索仓库）
4. [ ] 回复 "探索仓库"，智能体应列出仓库结构
5. [ ] 将 `inputs/example/` 作为输入，说 "分析这次中断"
6. [ ] 智能体应执行完整的五阶段分析并在 `memory/cases/` 下生成新的案例条目

如果第 6 步的网页检索失败，检查你的 Claude Code 是否已配置 WebSearch 工具权限。
```

## 后续更新

仓库发布后，每次推送前建议运行：

```bash
# 确保没有意外的敏感文件
git status

# 确保 .gitignore 过滤了所有运行时产物
find runs/ -type f ! -name '.gitkeep'  # 应该为空
find inputs/ -type f ! -name '.gitkeep' ! -path '*/example/*'  # 应该为空
```

## 与论文的关联

当论文提交后，在 README.md 的"贡献"节补充论文的永久链接（如 DOI 或 arXiv ID），使读者能从论文跳到仓库、从仓库跳回论文。
