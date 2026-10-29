"""Turn validated JSON into two Markdown documents: client-facing and technical."""

SECTIONS = [  # display order = what a reader must see first
    ("breaking", "⚠️ Breaking Changes"),
    ("security", "🔒 Security"),
    ("feature", "✨ New Features"),
    ("improvement", "🚀 Improvements"),
    ("fix", "🐛 Bug Fixes"),
    ("known_issue", "📌 Known Issues"),
    ("internal", "🔧 Internal"),
]


def _header(product, version, date, notes, audience):
    lines = [f"# {product} {version} — {audience}", f"_Released {date}_", "",
             "## Summary", notes["summary"], ""]
    if notes["highlights"]:
        lines += ["## Highlights"] + [f"- {h}" for h in notes["highlights"]] + [""]
    return lines


def render_client(notes: dict, product: str, version: str, date: str) -> str:
    lines = _header(product, version, date, notes, "Release Notes")
    for cat, title in SECTIONS:
        if cat == "internal":
            continue  # clients do not need to see refactors
        items = [e for e in notes["entries"] if e["category"] == cat]
        if items:
            lines += [f"## {title}"] + [f"- {e['business_text']}" for e in items] + [""]
    return "\n".join(lines)


def render_technical(notes: dict, product: str, version: str, date: str) -> str:
    lines = _header(product, version, date, notes, "Technical Changelog")
    for cat, title in SECTIONS:
        items = [e for e in notes["entries"] if e["category"] == cat]
        if items:
            lines += [f"## {title}"]
            lines += [f"- **{e['ticket_id']}** ({e['impact']}) {e['technical_text']}" for e in items] + [""]
    flagged = [e for e in notes["entries"] if e["needs_attention"]]
    if flagged:  # surfaces the model's own uncertainty for a human reviewer
        lines += ["## 🔍 Needs Human Review"]
        lines += [f"- **{e['ticket_id']}**: {e['attention_reason']}" for e in flagged] + [""]
    return "\n".join(lines)
