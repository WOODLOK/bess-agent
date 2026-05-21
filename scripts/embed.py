#!/usr/bin/env python3
"""
BGE-m3 文本向量化脚本（可选）。

用法:
    python scripts/embed.py "要向量化的文本"
    python scripts/embed.py --file memory/cases/2022-04-shanghai-cell-delay/case_entry.json
    python scripts/embed.py --batch memory/cases/

输出: JSON 数组形式的向量（float32 list），写入 stdout。

依赖: pip install sentence-transformers

注意:
    本脚本仅在以下情况下需要:
    1. 用户希望完全本地向量化，不依赖外部 embedding API
    2. 用户需要为 search_memory.py 构建向量索引

    如果用户在 Claude Code / Codex 中使用本智能体，客户端内置的
    embedding 能力（Anthropic / OpenAI）可以直接替代本脚本。
    此时不需要安装 sentence-transformers，也不需要运行本脚本。
"""

import argparse
import json
import sys
from pathlib import Path

_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer("BAAI/bge-m3")
    return _MODEL


def embed_text(text: str) -> list[float]:
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_file(filepath: str) -> dict:
    path = Path(filepath)
    if not path.exists():
        return {"error": f"文件不存在: {filepath}"}

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    embedding = embed_text(content)
    return {
        "file": str(path),
        "embedding_dim": len(embedding),
        "embedding": embedding,
    }


def embed_batch(directory: str) -> list[dict]:
    dir_path = Path(directory)
    results = []
    for case_dir in sorted(dir_path.iterdir()):
        if case_dir.is_dir():
            entry_file = case_dir / "case_entry.json"
            if entry_file.exists():
                result = embed_file(str(entry_file))
                results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description="BGE-m3 文本向量化")
    parser.add_argument("text", nargs="?", help="要向量化的文本")
    parser.add_argument("--file", help="要向量化的文件路径")
    parser.add_argument("--batch", help="批量向量化目录下所有 case_entry.json")
    args = parser.parse_args()

    if args.batch:
        results = embed_batch(args.batch)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.file:
        result = embed_file(args.file)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.text:
        embedding = embed_text(args.text)
        print(json.dumps({"embedding": embedding, "embedding_dim": len(embedding)}, ensure_ascii=False))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
