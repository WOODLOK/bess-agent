# M-5 里程碑报告：辅助脚本完成

**完成日期**：2026-05-21

## 完成项

创建了 3 个辅助脚本 + 1 个 README.md：

| 脚本 | 行数 | 用途 | 是否必需 |
|:---|:---|:---|:---|
| `embed.py` | 81 | BGE-m3 文本向量化（单文本/单文件/批量目录） | 可选——Claude Code 内置 embedding 可替代 |
| `search_memory.py` | 133 | 案例记忆库检索（关键词模式无外部依赖，向量模式需 sentence-transformers） | 半必需——关键词模式为场景 B 提供程序化检索入口 |
| `extract_pdf.py` | 84 | PDF 文本抽取兜底（单文件/批量 + 元数据提取） | 可选——Claude Code Read 工具原生支持 PDF |
| `README.md` | 63 | 脚本使用指南 + 何时该写/不该写脚本的决策规则 | 必需（项目规范文档） |

## 各脚本说明

### embed.py
- 三个入口：`python embed.py "文本"` / `--file <path>` / `--batch <dir>`
- 加载 BAAI/bge-m3 模型，输出 normalized embedding 向量
- 仅当用户需要完全本地向量化、不使用外部 API 时才需要

### search_memory.py
- 两个模式：`--keyword`（默认，无外部依赖）和 `--vector`（需 sentence-transformers）
- `--keyword` 模式按关键词在 case_id、causal_chain_summary、event_signature、materials、route 字段上的命中频率加权评分
- `--vector` 模式自动构建/读取向量索引 `memory/vector_index.json`
- `--rebuild-index` 强制重建向量索引
- `--top-k` 控制返回数量（默认 3）

### extract_pdf.py
- 使用 PyMuPDF (fitz) 抽取文本，保留分页结构
- `--batch` 模式批量处理目录下所有 PDF，可选 `--batch-output` 输出目录
- 附带元数据提取（页数、标题、作者）

## 已知问题

- `search_memory.py` 的关键词评分为简单加权方案，未实现 AGENT.md 第 6 节定义的强匹配/弱匹配二维体系——该体系更适合 LLM 交互式执行；脚本的 --keyword 模式作为快速预筛选，LLM 在接收到 Top-K 结果后可进一步按强匹配/弱匹配维度二次排序
- `embed.py` 首次运行需下载 BGE-m3 模型（约 2GB）；已在 README 中标注
- 三个脚本的 Python 依赖为可选——不安装依赖时，本仓库的其他部分（AGENT.md + SKILL.md + schemas）仍然完全可用

## 为什么只创建了这三个脚本

遵循核心原则：**写代码不是本项目的主线**。只有当 LLM 无法直接完成某操作时才允许写脚本。具体情况：

- **PDF 文本抽取**：Claude Code 原生支持 → `extract_pdf.py` 仅为兜底
- **向量化**：Claude Code 可通过 API 调用 embedding → `embed.py` 仅为本地化替代
- **案例检索**：LLM 可直接读取 INDEX.md + case_entry.json 进行理解式匹配 → `search_memory.py` 仅提供程序化批量检索入口
- 没有创建其他脚本，因为五阶段工作流、四类工具检索均由 LLM 读取 SKILL.md 驱动

## 给用户的检查清单

- [ ] 三个脚本的接口设计是否合理？
- [ ] `search_memory.py` 的关键词加权逻辑是否需要调整？
- [ ] `scripts/README.md` 中"添加新脚本的规则"是否足够严格地保护声明式优先原则？
- [ ] 是否有遗漏的必需脚本？
