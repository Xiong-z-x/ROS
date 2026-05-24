#!/usr/bin/env python3
"""Export the combined ROS1 textbook Markdown file to HTML/PDF.

The script keeps Mermaid diagrams compact in print output. It uses Python
Markdown for Markdown-to-HTML conversion and a local Chrome/Edge executable for
PDF printing. If a local Mermaid bundle exists under book-build/node_modules,
it is embedded into the HTML; otherwise the HTML falls back to the jsDelivr CDN.
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "ROS1零基础自学指导书-最终版.md"
DEFAULT_HTML = ROOT / "ROS1零基础自学指导书-最终版.html"
DEFAULT_PDF = ROOT / "ROS1零基础自学指导书-最终版.pdf"


def replace_mermaid_blocks(markdown_text: str) -> str:
    pattern = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)

    def repl(match: re.Match[str]) -> str:
        diagram = html.escape(match.group(1).strip())
        return f'\n<pre class="mermaid">{diagram}</pre>\n'

    return pattern.sub(repl, markdown_text)


def find_mermaid_script() -> str:
    candidates = [
        ROOT / "book-build" / "node_modules" / "mermaid" / "dist" / "mermaid.min.js",
        ROOT / "node_modules" / "mermaid" / "dist" / "mermaid.min.js",
    ]
    for candidate in candidates:
        if candidate.exists():
            return f"<script>{candidate.read_text(encoding='utf-8')}</script>"
    return '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'


def find_chrome(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if path.exists():
            return path
        raise FileNotFoundError(f"Chrome/Edge executable not found: {path}")

    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Chrome or Edge executable was not found.")


def build_html(markdown_path: Path, html_path: Path) -> None:
    raw = markdown_path.read_text(encoding="utf-8")
    prepared = replace_mermaid_blocks(raw)
    body = markdown.markdown(
        prepared,
        extensions=[
            "extra",
            "toc",
            "sane_lists",
            "smarty",
        ],
        output_format="html5",
    )

    mermaid_script = find_mermaid_script()
    css = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body {
  font-family: "Microsoft YaHei", "Noto Sans CJK SC", "SimSun", Arial, sans-serif;
  color: #1f2933;
  font-size: 12px;
  line-height: 1.62;
  max-width: 980px;
  margin: 0 auto;
}
h1, h2, h3, h4 { color: #111827; line-height: 1.28; page-break-after: avoid; }
h1 { font-size: 25px; border-bottom: 1px solid #d0d7de; padding-bottom: 8px; margin-top: 24px; }
h2 { font-size: 19px; margin-top: 22px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }
h3 { font-size: 15px; margin-top: 16px; }
p, li { orphans: 3; widows: 3; }
code { font-family: Consolas, "Cascadia Mono", monospace; font-size: 0.88em; }
pre {
  background: #f6f8fa;
  border: 1px solid #d0d7de;
  border-radius: 5px;
  padding: 8px 10px;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  page-break-inside: avoid;
  font-size: 10px;
  line-height: 1.35;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0 14px;
  page-break-inside: avoid;
}
th, td { border: 1px solid #d0d7de; padding: 5px 7px; vertical-align: top; }
th { background: #f3f4f6; }
blockquote {
  border-left: 4px solid #94a3b8;
  color: #334155;
  margin: 10px 0;
  padding: 6px 12px;
  background: #f8fafc;
}
.mermaid {
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 5px;
  padding: 6px;
  margin: 8px auto 12px;
  text-align: center;
  page-break-inside: avoid;
  overflow: hidden;
}
.mermaid svg {
  max-width: 100% !important;
  max-height: 240px !important;
  height: auto !important;
}
"""

    script = """
<script>
document.addEventListener("DOMContentLoaded", async () => {
  if (window.mermaid) {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "loose",
      theme: "neutral",
      flowchart: { htmlLabels: true, curve: "basis" },
      sequence: { mirrorActors: false }
    });
    await mermaid.run({ querySelector: ".mermaid" });
  }
  document.body.dataset.rendered = "true";
});
</script>
"""

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>ROS1 零基础自学指导书</title>
  <style>{css}</style>
  {mermaid_script}
  {script}
</head>
<body>
{body}
</body>
</html>
"""
    html_path.write_text(page, encoding="utf-8", newline="\n")


def print_pdf(chrome: Path, html_path: Path, pdf_path: Path) -> None:
    pdf_path.unlink(missing_ok=True)
    url = html_path.resolve().as_uri()
    command = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        "--virtual-time-budget=12000",
        url,
    ]
    subprocess.run(command, check=True)
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"PDF was not created: {pdf_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--html", default=str(DEFAULT_HTML))
    parser.add_argument("--pdf", default=str(DEFAULT_PDF))
    parser.add_argument("--chrome", default=None)
    parser.add_argument("--html-only", action="store_true")
    args = parser.parse_args()

    markdown_path = Path(args.input)
    html_path = Path(args.html)
    pdf_path = Path(args.pdf)

    build_html(markdown_path, html_path)
    print(f"Wrote HTML: {html_path}")

    if not args.html_only:
        chrome = find_chrome(args.chrome)
        print_pdf(chrome, html_path, pdf_path)
        print(f"Wrote PDF: {pdf_path}")


if __name__ == "__main__":
    main()
