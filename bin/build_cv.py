#!/usr/bin/env python3
"""Build assets/pdf/cv.pdf from assets/json/resume.json.

The typesetting follows Jake's Resume: a centered header, uppercase section
headings with a full-width rule, and one compact row per entry with the date
flush right.

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

# Rendered in this order; a section missing from resume.json is skipped entirely.
SECTIONS = [
    ("education", "Education"),
    ("work", "Experience"),
    ("publications", "Publications"),
    ("awards", "Honors & Awards"),
    ("teaching", "Teaching"),
]

# Icons for the header contact line, as Private Use Area glyphs from the icon
# fonts that ship with the theme. Keyed by profile network name; "email" and
# "url" cover the corresponding basics fields.
ICONS = {
    "email": ("fa", "\uf0e0"),           # envelope
    "url": ("fa", "\uf0ac"),             # globe
    "Google Scholar": ("ai", "\ue9d4"),  # academicons scholar mark
}
ICON_FALLBACK = ("fa", "\uf0c1")         # link

MONTHS = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

CSS = """
@font-face { font-family: "CVIconFA"; src: url("../webfonts/fa-solid-900.woff2") format("woff2"); }
@font-face { font-family: "CVIconAI"; src: url("../fonts/academicons.ttf") format("truetype"),
                                          url("../fonts/academicons.woff") format("woff"); }
@page { size: A4; margin: 13mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "Charter","Georgia","Times New Roman",serif; font-size: 9.6pt; line-height: 1.32;
       color: #000; margin: 0; -webkit-font-smoothing: antialiased; }
header { text-align: center; margin-bottom: 9pt; }
h1 { font-size: 23pt; font-weight: 400; margin: 0; letter-spacing: .3pt; }
h1 b { font-weight: 700; }
.label { font-size: 9.4pt; margin-top: 2pt; }
.contact { font-size: 9pt; margin-top: 3pt; }
.contact span + span::before { content: " | "; }
.contact a { color: inherit; text-decoration: none; }
.ic { font-style: normal; font-size: 8.4pt; margin-right: 2.5pt; }
.ic.fa { font-family: "CVIconFA"; }
.ic.ai { font-family: "CVIconAI"; }
h2 { font-size: 10.5pt; font-weight: 700; text-transform: uppercase; letter-spacing: .5pt;
     margin: 9pt 0 1pt; padding-bottom: 1pt; border-bottom: .9pt solid #000; }
.row { display: flex; justify-content: space-between; align-items: baseline; gap: 12pt; margin-top: 4pt; }
.row .l { flex: 1; }
.row .r { text-align: right; white-space: nowrap; font-size: 9.2pt; font-style: italic;
          font-variant-numeric: tabular-nums; }
.ttl { font-weight: 700; }
.sub { font-style: italic; font-size: 9.2pt; }
.meta { font-size: 9pt; }
.url { font-family: "SF Mono", Menlo, monospace; font-size: 8pt; }
ul { margin: 1pt 0 0; padding-left: 12pt; }
li { margin: .5pt 0; }
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


def emphasize_self(authors, owner):
    """Bold and underline the CV owner's name inside an author list."""
    escaped = html.escape(authors)
    if owner:
        escaped = escaped.replace(html.escape(owner), f"<u><b>{html.escape(owner)}</b></u>")
    return escaped


def render_entry(key, entry, owner=""):
    """One resume entry as HTML. Every section is title-left / date-right."""
    e = html.escape
    out = []

    if key == "education":
        area = f', {e(entry["area"])}' if entry.get("area") else ""
        out.append(row(
            f'<span class="ttl">{e(entry["studyType"])}</span>{area}<br>'
            f'<span class="sub">{e(entry["institution"])}, {e(entry.get("location", ""))}</span>',
            fmt_span(entry.get("startDate"), entry.get("endDate")),
        ))
    elif key == "work":
        out.append(row(
            f'<span class="ttl">{e(entry["position"])}</span><br>'
            f'<span class="sub">{e(entry["name"])}</span>',
            fmt_span(entry.get("startDate"), entry.get("endDate")),
        ))
    elif key == "publications":
        out.append(row(
            f'<span class="ttl">{e(entry["name"])}</span><br>'
            f'<span class="meta">{emphasize_self(entry["publisher"], owner)}</span>',
            e(entry["venue"]),
        ))
    elif key == "awards":
        out.append(row(
            f'<span class="ttl">{e(entry["title"])}</span><br>'
            f'<span class="sub">{e(entry["awarder"])}</span>',
            fmt_date(entry["date"]),
        ))
    elif key == "teaching":
        out.append(row(
            f'<span class="ttl">{e(entry["position"])} — {e(entry["name"])}</span><br>'
            f'<span class="sub">{e(entry["institution"])}</span>',
            e(entry["date"]),
        ))

    if entry.get("summary"):
        out.append(f'<div class="meta">{e(entry["summary"])}</div>')
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

    e = html.escape
    basics = data["basics"]
    names = basics["name"].split()
    heading = f'{e(names[0])} <b>{e(" ".join(names[1:]))}</b>' if len(names) > 1 else e(basics["name"])
    links = [(basics["email"], f'mailto:{basics["email"]}', "email")]
    if basics.get("url"):
        links.append((basics["url"].replace("https://", ""), basics["url"], "url"))
    for profile in basics.get("profiles", []):
        links.append((profile["network"], profile["url"], profile["network"]))

    chunks = []
    for text, href, icon_key in links:
        family, glyph = ICONS.get(icon_key, ICON_FALLBACK)
        chunks.append(
            f'<span><a href="{e(href)}">'
            f'<i class="ic {family}">{glyph}</i>{e(text)}</a></span>'
        )
    contact = "".join(chunks)

    parts = [
        f'<header><h1>{heading}</h1>'
        f'<div class="label">{e(basics["label"])}</div>'
        f'<div class="contact">{contact}</div></header>'
    ]
    for key, headline in SECTIONS:
        entries = data.get(key) or []
        if not entries:
            continue
        parts.append(f"<h2>{headline}</h2>")
        for entry in entries:
            parts.extend(render_entry(key, entry, basics["name"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(TMP, "w") as fh:
        fh.write(
            '<!doctype html><html><head><meta charset="utf-8">'
            f'<title>{e(basics["name"])} — CV</title>'
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
