#!/usr/bin/env python3
"""Build assets/pdf/cv.pdf from assets/json/resume.json.

The CV page and the downloadable PDF are generated from the same source, so
edit assets/json/resume.json and re-run this script to keep them in sync.

Usage:
    python3 bin/build_cv.py            # repo root is inferred from this file
    python3 bin/build_cv.py <repo>     # or pass it explicitly

Requires Google Chrome (headless) for PDF rendering.
"""

import html
import json
import os
import subprocess
import sys

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "assets/json/resume.json")
OUT = os.path.join(REPO, "assets/pdf/cv.pdf")
TMP = os.path.join(REPO, "assets/pdf/.cv.html")

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# Sections are rendered in this order; missing or empty ones are skipped.
SECTIONS = [
    ("education", "Education"),
    ("work", "Experience"),
    ("publications", "Publications"),
    ("awards", "Honors and Awards"),
    ("projects", "Projects"),
]

MONTHS = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

CSS = """
@page { size: A4; margin: 18mm 17mm; }
* { box-sizing: border-box; }
body { font-family: "Charter","Georgia","Times New Roman",serif; font-size: 9.8pt; line-height: 1.42;
       color: #1a1a1a; margin: 0; -webkit-font-smoothing: antialiased; }
header { margin-bottom: 14pt; }
h1 { font-size: 21pt; font-weight: 600; letter-spacing: .2pt; margin: 0 0 2pt; }
.label { font-size: 10.5pt; color: #444; margin-bottom: 4pt; }
.contact { font-size: 8.8pt; color: #666; }
h2 { font-size: 10pt; font-weight: 700; text-transform: uppercase; letter-spacing: .9pt;
     margin: 15pt 0 6pt; padding-bottom: 2.5pt; border-bottom: .6pt solid #bbb; }
.row { display: flex; justify-content: space-between; align-items: baseline; gap: 12pt; margin-top: 6pt; }
.row .l { flex: 1; }
.row .r { font-size: 8.8pt; color: #666; white-space: nowrap; font-variant-numeric: tabular-nums; }
.ttl { font-weight: 700; }
.area { color: #555; font-style: italic; }
.inst { color: #333; }
ul { margin: 2pt 0 0; padding-left: 13pt; }
li { margin: 1pt 0; color: #333; }
.sum { margin-top: 2pt; color: #333; text-align: justify; }
.pub { margin-top: 7pt; }
.pub .ttl { display: block; }
.pub .auth { color: #333; }
.pub .ven { font-size: 8.8pt; color: #666; font-style: italic; }
.url { font-style: normal; font-family: "SF Mono",Menlo,monospace; font-size: 8pt; }
h2, .row, .pub { break-inside: avoid; }
h2 { break-after: avoid; }
"""


def fmt_date(value):
    if not value:
        return ""
    if value == "present":
        return "Present"
    parts = value.split("-")
    return f"{MONTHS[parts[1]]} {parts[0]}" if len(parts) > 1 else parts[0]


def fmt_span(start, end):
    return f"{fmt_date(start)} – {fmt_date(end)}" if end else fmt_date(start)


def row(left, right):
    return f'<div class="row"><div class="l">{left}</div><div class="r">{right}</div></div>'


def bullets(items):
    return "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>"


def render_entry(key, entry):
    out = []
    if key == "education":
        area = f' <span class="area">{html.escape(entry["area"])}</span>' if entry.get("area") else ""
        out.append(row(
            f'<span class="ttl">{html.escape(entry["studyType"])}</span>{area}<br>'
            f'<span class="inst">{html.escape(entry["institution"])}</span>, {html.escape(entry.get("location", ""))}',
            fmt_span(entry.get("startDate"), entry.get("endDate")),
        ))
    elif key == "work":
        out.append(row(
            f'<span class="ttl">{html.escape(entry["position"])}</span><br>'
            f'<span class="inst">{html.escape(entry["name"])}</span>',
            fmt_span(entry.get("startDate"), entry.get("endDate")),
        ))
    elif key == "publications":
        out.append(
            f'<div class="pub"><div class="ttl">{html.escape(entry["name"])}</div>'
            f'<div class="auth">{html.escape(entry["publisher"])}</div>'
            f'<div class="ven">{html.escape(entry["venue"])} &nbsp;·&nbsp; '
            f'<span class="url">{html.escape(entry["url"])}</span></div></div>'
        )
    elif key == "awards":
        out.append(row(
            f'<span class="ttl">{html.escape(entry["title"])}</span><br>'
            f'<span class="inst">{html.escape(entry["awarder"])}</span>',
            fmt_date(entry["date"]),
        ))
    elif key == "projects":
        out.append(row(f'<span class="ttl">{html.escape(entry["name"])}</span>',
                       fmt_span(entry.get("startDate"), entry.get("endDate"))))
        if entry.get("summary"):
            out.append(f'<div class="sum">{html.escape(entry["summary"])}</div>')

    if entry.get("summary") and key in ("education", "work", "awards", "publications"):
        out.append(f'<div class="sum">{html.escape(entry["summary"])}</div>')
    if entry.get("highlights"):
        out.append(bullets(entry["highlights"]))
    return out


def find_chrome():
    for path in CHROME_CANDIDATES:
        if os.path.exists(path):
            return path
    sys.exit("Google Chrome not found. Install it, or add its path to CHROME_CANDIDATES.")


def main():
    with open(SRC) as fh:
        data = json.load(fh)

    basics = data["basics"]
    parts = [
        f'<header><h1>{html.escape(basics["name"])}</h1>'
        f'<div class="label">{html.escape(basics["label"])}</div>'
        f'<div class="contact">{html.escape(basics["email"])} &nbsp;·&nbsp; '
        f'Data Systems Lab, POSTECH &nbsp;·&nbsp; juevn.github.io</div></header>'
    ]
    for key, heading in SECTIONS:
        entries = data.get(key) or []
        if not entries:
            continue
        parts.append(f"<h2>{heading}</h2>")
        for entry in entries:
            parts.extend(render_entry(key, entry))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(TMP, "w") as fh:
        fh.write(
            '<!doctype html><html><head><meta charset="utf-8">'
            f'<title>{html.escape(basics["name"])} — CV</title>'
            f"<style>{CSS}</style></head><body>{''.join(parts)}</body></html>"
        )

    subprocess.run(
        [find_chrome(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={OUT}", f"file://{TMP}"],
        capture_output=True, check=True,
    )
    os.remove(TMP)
    print(f"Wrote {os.path.relpath(OUT, REPO)} ({os.path.getsize(OUT) // 1024} KB)")


if __name__ == "__main__":
    main()
