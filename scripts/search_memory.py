#!/usr/bin/env python3
"""
案例记忆库语义/关键词检索脚本。

用法:
    python scripts/search_memory.py "上海港延误 LFP电芯"
    python scripts/search_memory.py --keyword "上海港" --top-k 5
    python scripts/search_memory.py --vector "上海港延误" --top-k 3

输出: JSON 格式的 Top-K 匹配案例，含相似度分数与匹配理由。

依赖（仅 vector 模式）: pip install sentence-transformers
关键词模式无外部依赖。

注意:
    本脚本用于 AGENT.md 第 6 节"场景 B——检索历史"。
    在 Claude Code / Codex 中，LLM 可以直接读取 memory/INDEX.md
    和 memory/cases/*/case_entry.json 进行基于理解的匹配，此时
    本脚本是补充手段而非必需入口。
"""

import argparse
import json
import os
import re
from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory" / "cases"


def load_all_cases() -> list[dict]:
    cases = []
    if not MEMORY_DIR.exists():
        return cases
    for case_dir in sorted(MEMORY_DIR.iterdir(), reverse=True):
        if case_dir.is_dir() and not case_dir.name.startswith("."):
            entry = case_dir / "case_entry.json"
            if entry.exists():
                with open(entry, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["_dir"] = str(case_dir)
                    cases.append(data)
    return cases


def keyword_search(query: str, cases: list[dict], top_k: int = 3) -> list[dict]:
    query_lower = query.lower()
    scored = []
    for case in cases:
        score = 0
        # 搜索 case_id
        if query_lower in case.get("case_id", "").lower():
            score += 10
        # 搜索 causal_chain_summary
        summary = case.get("causal_chain_summary", "")
        score += summary.lower().count(query_lower) * 2
        # 搜索 event_signature
        for es in case.get("event_signature", []):
            if query_lower in es.get("type", "").lower() or query_lower in es.get("subtype", "").lower():
                score += 5
        # 搜索 materials
        for m in case.get("materials", []):
            if query_lower in m.get("category", "").lower() or query_lower in m.get("specification", "").lower():
                score += 3
        # 搜索 route
        route = case.get("route", {})
        for v in route.values():
            if isinstance(v, str) and query_lower in v.lower():
                score += 3

        if score > 0:
            scored.append((score, case))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "case_id": case["case_id"],
            "score": score,
            "causal_chain_summary": case.get("causal_chain_summary", "")[:200],
            "event_signature": case.get("event_signature", []),
            "route": case.get("route", {}),
            "confidence_level": case.get("confidence_level", "unknown"),
        }
        for score, case in scored[:top_k]
    ]


def vector_search(query: str, cases: list[dict], top_k: int = 3) -> list[dict]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("BAAI/bge-m3")
    query_vec = model.encode(query, normalize_embeddings=True)

    # 尝试加载已有索引；如不存在，现场构建
    index_path = MEMORY_DIR.parent / "vector_index.json"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {}
        for case in cases:
            text = f"{case.get('case_id', '')} {case.get('causal_chain_summary', '')} {' '.join([es.get('type', '') for es in case.get('event_signature', [])])}"
            vec = model.encode(text, normalize_embeddings=True)
            index[case.get("case_id", "")] = vec.tolist()
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f)

    from numpy import dot
    from numpy.linalg import norm

    scored = []
    for case in cases:
        cid = case.get("case_id", "")
        if cid in index:
            case_vec = index[cid]
            similarity = float(dot(query_vec, case_vec) / (norm(query_vec) * norm(case_vec)))
            scored.append((similarity, case))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "case_id": case["case_id"],
            "cosine_similarity": round(score, 4),
            "causal_chain_summary": case.get("causal_chain_summary", "")[:200],
            "event_signature": case.get("event_signature", []),
            "route": case.get("route", {}),
            "confidence_level": case.get("confidence_level", "unknown"),
        }
        for score, case in scored[:top_k]
    ]


def main():
    parser = argparse.ArgumentParser(description="案例记忆库检索")
    parser.add_argument("query", nargs="?", help="检索查询文本")
    parser.add_argument("--keyword", action="store_true", default=True, help="使用关键词检索 (默认)")
    parser.add_argument("--vector", action="store_true", help="使用向量语义检索 (需 sentence-transformers)")
    parser.add_argument("--top-k", type=int, default=3, help="返回结果数 (默认 3)")
    parser.add_argument("--rebuild-index", action="store_true", help="重建向量索引")
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        return

    cases = load_all_cases()
    if not cases:
        print(json.dumps({"error": "案例记忆库为空", "hint": "至少完成一次阶段五分析后才有可检索的案例"}, ensure_ascii=False, indent=2))
        return

    if args.rebuild_index:
        index_path = MEMORY_DIR.parent / "vector_index.json"
        if index_path.exists():
            os.remove(index_path)

    if args.vector:
        results = vector_search(args.query, cases, args.top_k)
    else:
        results = keyword_search(args.query, cases, args.top_k)

    print(json.dumps({"query": args.query, "mode": "vector" if args.vector else "keyword", "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
