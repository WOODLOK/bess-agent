# Scripts — 辅助脚本说明

本目录下的脚本是**可选的辅助工具**，仅在 LLM 客户端无法直接完成某些任务时才需要使用。

## 核心理念

本智能体仓库的设计哲学是"声明式优先"——80% 以上的功能由 markdown（AGENT.md + SKILL.md）与 JSON schema 驱动，LLM 客户端（Claude Code / Codex）直接读取这些声明式文件即可完成大多数操作，无需运行任何脚本。

**脚本存在的唯一理由是处理 LLM 无法直接完成的操作**：本地向量化（需要加载模型）、批量 PDF 文本抽取（需要专门的 PDF 解析库）、以及案例记忆库的批量检索（需要对多文件的聚合处理）。

## 脚本清单

| 脚本 | 用途 | 何时需要 | 何时不需要 | 依赖 |
|:---|:---|:---|:---|:---|
| `embed.py` | BGE-m3 文本向量化 | 希望完全本地向量化，不使用外部 embedding API | Claude Code / Codex 内置 embedding（Anthropic / OpenAI）可直接替代 | `sentence-transformers` |
| `search_memory.py` | 案例记忆库关键词/语义检索 | 批量检索案例库；关键词检索模式无外部依赖 | LLM 直接读取 INDEX.md + case_entry.json 进行理解式匹配（适用于案例库较小时的交互式查询） | 关键词模式无依赖；向量模式需 `sentence-transformers` |
| `extract_pdf.py` | PDF 文本批量抽取 | 客户端不支持 PDF 原生读取；需批量处理大量 PDF | Claude Code / Codex 的 Read 工具原生支持 PDF 读取 | `pymupdf` |

## 安装依赖

```bash
# 仅在需要运行 embed.py 或 search_memory.py 的向量模式时安装
pip install sentence-transformers

# 仅在需要运行 extract_pdf.py 时安装
pip install pymupdf

# 完整安装（所有脚本依赖）
pip install sentence-transformers pymupdf
```

## 添加新脚本的规则

在添加新脚本前，先问自己三个问题：

1. **LLM 能否直接完成此操作？** 如果答案是"能"（如读取文本、理解 PDF 内容、网页检索），就不该写脚本。
2. **是否有无法绕过的本地计算需求？** 如加载 ML 模型、批量操作数百个文件——这些是可以接受的理由。
3. **是否需要与外部系统交互？** 如数据库连接、API 认证——这些也可能是合理的脚本场景。

如果三个问题都指向"需要脚本"，在创建脚本前先在仓库根目录的 `DECISIONS.md` 中记录理由。例如：

> D-001 | 2026-05-21 | 新增 scripts/xxx.py | 原因：LLM 无法直接读取本地的 XXX 格式文件 | 备选方案：无

这确保了本仓库的"声明式优先"原则不被逐渐侵蚀。
