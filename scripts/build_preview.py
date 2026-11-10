"""Builds preview.html: the README rendered like a GitHub profile, openable straight
from disk in any browser (Firefox included, which blocks fetch() on file:// pages).

Run: python scripts/build_preview.py   then open preview.html
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
readme = (root / "README.md").read_text(encoding="utf-8")

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Profile preview</title>
<style>
  body {{ background: #0d1117; color: #e6edf3; margin: 0;
         font-family: -apple-system, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 1.5; }}
  .wrap {{ max-width: 900px; margin: 24px auto; padding: 24px; border: 1px solid #30363d; border-radius: 6px; }}
  .bar {{ font-size: 12px; color: #8d96a0; margin-bottom: 16px; }}
  a {{ color: #4493f8; text-decoration: none; }}
  img {{ max-width: 100%; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td {{ border: 1px solid #30363d; padding: 8px 13px; }}
  h3, h4 {{ margin: 24px 0 12px; }}
  code {{ background: #262c36; padding: .2em .4em; border-radius: 6px; font-size: 85%; }}
  ul {{ padding-left: 2em; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="bar">rayenchatti / README.md</div>
  <div id="readme"></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script>
  document.getElementById("readme").innerHTML = marked.parse({json.dumps(readme)});
</script>
</body>
</html>
"""
(root / "preview.html").write_text(html, encoding="utf-8")
print("wrote", root / "preview.html")
