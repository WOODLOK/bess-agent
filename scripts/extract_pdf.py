#!/usr/bin/env python3
"""
PDF 文本抽取兜底脚本（可选）。

用法:
    python scripts/extract_pdf.py document.pdf              # 输出到 stdout
    python scripts/extract_pdf.py document.pdf --output out.txt
    python scripts/extract_pdf.py --batch inputs/batch_01/   # 批量处理

依赖: pip install pymupdf  (PyMuPDF)

注意:
    本脚本是 PDF 读取的兜底方案。在 Claude Code / Codex 中，
    LLM 客户端原生支持 PDF 读取（通过 Read 工具），此时不需要
    本脚本。仅在以下情况下使用:
    1. 客户端不支持 PDF 原生读取
    2. 需要批量抽取大量 PDF 的文本用于后续脚本处理
    3. 需要提取 PDF 元数据（页数、章节等）
"""

import argparse
import sys
from pathlib import Path


def extract_text(filepath: str) -> str:
    import fitz  # PyMuPDF
    doc = fitz.open(filepath)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append(f"--- 第 {i + 1} 页 ---\n{text}")
    doc.close()
    return "\n\n".join(pages)


def extract_metadata(filepath: str) -> dict:
    import fitz
    doc = fitz.open(filepath)
    meta = {
        "file": filepath,
        "pages": len(doc),
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
    }
    doc.close()
    return meta


def batch_extract(directory: str, output_dir: str = None) -> list[dict]:
    dir_path = Path(directory)
    results = []
    for pdf_file in sorted(dir_path.glob("*.pdf")):
        text = extract_text(str(pdf_file))
        meta = extract_metadata(str(pdf_file))
        meta["text_length"] = len(text)
        results.append(meta)

        if output_dir:
            out_path = Path(output_dir) / f"{pdf_file.stem}.txt"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)

    return results


def main():
    parser = argparse.ArgumentParser(description="PDF 文本抽取（兜底）")
    parser.add_argument("file", nargs="?", help="PDF 文件路径")
    parser.add_argument("--output", help="输出文本文件路径")
    parser.add_argument("--batch", help="批量处理目录下所有 PDF")
    parser.add_argument("--batch-output", help="批量处理输出目录")
    args = parser.parse_args()

    if args.batch:
        results = batch_extract(args.batch, args.batch_output)
        for r in results:
            print(f"  {r['file']}: {r['pages']} 页, {r['text_length']} 字符")
        return

    if not args.file:
        parser.print_help()
        sys.exit(1)

    text = extract_text(args.file)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已写入 {args.output} ({len(text)} 字符)")
    else:
        print(text)


if __name__ == "__main__":
    main()
