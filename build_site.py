#!/usr/bin/env python3
"""Convert markdown articles to clean HTML and build the publications site."""
import markdown
import os
import re
from datetime import datetime

SITE_DIR = os.path.dirname(os.path.abspath(__file__))

def md_to_html(md_text, title):
    """Convert markdown to HTML article body, stripping editorial metadata."""
    # Find the article body - after the "## Article" heading or the first "---" after metadata
    # For EU PLD: content after "## Article"
    # For Post-midterm: content after the first "---"
    
    # Remove editorial metadata section (everything before the article body)
    if "## Article" in md_text:
        body = md_text.split("## Article", 1)[1].strip()
    elif md_text.count("---") >= 1:
        parts = md_text.split("---", 1)
        if len(parts) > 1:
            # Check if there's a "Draft for" note we should skip
            remaining = parts[1]
            if "Draft for" in remaining and remaining.count("---") >= 1:
                body = remaining.split("---", 1)[1].strip()
            else:
                body = remaining.strip()
        else:
            body = md_text
    else:
        body = md_text
    
    # Remove the editorial review note line
    body = re.sub(r'\*Draft for[^*]*\*', '', body)
    
    # Remove compliance notes and hooks sections (everything after "## Sources" or "## Compliance Notes")
    for marker in ["## Compliance Notes", "## Companion Hooks", "\n## Sources"]:
        if marker in body:
            body = body.split(marker)[0].strip()
    
    # Keep Sources section if it exists (for EU PLD)
    # Actually let's include sources - find and append
    sources_match = re.search(r'## Sources\s*\n(.*?)(?=\n## |\Z)', md_text, re.DOTALL)
    sources_html = ""
    if sources_match:
        sources_text = sources_match.group(0)
        sources_html = markdown.markdown(sources_text, extensions=['extra'])
    
    # Convert body to HTML
    html_body = markdown.markdown(body, extensions=['extra', 'sane_lists'])
    
    return html_body, sources_html


def build_page(title, html_body, sources_html, subtitle, publish_date, author="Monumental Health"):
    """Wrap article HTML in a clean page template."""
    disclaimer = ""
    if "EU Product Liability" in title:
        disclaimer = '<p class="disclaimer"><em>This article provides information about regulatory developments, not legal advice. Organizations should consult qualified counsel for their specific circumstances.</em></p>'
    
    crisis_line = ""
    if "Election" in title or "veteran" in title.lower() or "Veterans" in title:
        crisis_line = '<div class="crisis-line"><p><strong>Veterans Crisis Line:</strong> Dial 988, then press 1. Available 24/7. Text 838255. Chat at veteranscrisisline.net.</p></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Monumental Health</title>
    <meta name="description" content="{subtitle}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{subtitle}">
    <meta property="og:type" content="article">
    <style>
        :root {{
            --bg: #0f1117;
            --surface: #1a1d28;
            --text: #e4e6eb;
            --text-muted: #9ca3af;
            --accent: #6b8aff;
            --border: #2a2d3a;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Georgia, serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
            max-width: 760px;
            margin: 0 auto;
            padding: 2rem 1.2rem;
        }}
        header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .logo {{
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--accent);
            text-decoration: none;
            letter-spacing: -0.02em;
        }}
        .logo:hover {{ text-decoration: underline; }}
        .meta {{
            color: var(--text-muted);
            font-size: 0.88rem;
            margin-top: 1rem;
        }}
        h1 {{
            font-size: 2rem;
            line-height: 1.3;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 1.05rem;
            margin-bottom: 0.5rem;
        }}
        article {{
            font-size: 1.08rem;
        }}
        article h2 {{
            font-size: 1.4rem;
            margin-top: 2.2rem;
            margin-bottom: 0.8rem;
            color: var(--text);
        }}
        article h3 {{
            font-size: 1.15rem;
            margin-top: 1.8rem;
            margin-bottom: 0.6rem;
            color: var(--accent);
        }}
        article p {{
            margin-bottom: 1.1rem;
        }}
        article strong {{
            color: #fff;
        }}
        article ul, article ol {{
            margin-bottom: 1.1rem;
            padding-left: 1.5rem;
        }}
        article li {{
            margin-bottom: 0.4rem;
        }}
        .disclaimer {{
            color: var(--text-muted);
            font-size: 0.92rem;
            border-left: 3px solid var(--border);
            padding-left: 1rem;
            margin: 2rem 0;
        }}
        .crisis-line {{
            background: rgba(107, 138, 255, 0.1);
            border: 1px solid var(--accent);
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin: 2rem 0;
        }}
        .crisis-line p {{
            margin: 0;
            font-size: 0.95rem;
        }}
        .sources {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
        }}
        .sources h2 {{
            font-size: 1.1rem;
            color: var(--text-muted);
        }}
        .sources ol {{
            font-size: 0.88rem;
            color: var(--text-muted);
        }}
        .firewall-note {{
            color: var(--text-muted);
            font-size: 0.82rem;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        footer {{
            margin-top: 4rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        footer a {{
            color: var(--accent);
            text-decoration: none;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 1rem 0.8rem; }}
            h1 {{ font-size: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <a href="index.html" class="logo">Monumental Health</a>
        <div class="meta">Published {publish_date} · {author}</div>
    </header>
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    <article>
        {html_body}
        {disclaimer}
        {crisis_line}
    </article>
    {f'<div class="sources">{sources_html}</div>' if sources_html else ''}
    <p class="firewall-note">No Capital Intelligence data (investment positions, strategies, returns, or proprietary research) is referenced in this article.</p>
    <footer>
        <p>Monumental Health · Veteran education and advocacy · <a href="index.html">All articles</a></p>
        <p style="margin-top:0.5rem">monumentalhealth.io</p>
    </footer>
</body>
</html>"""


def build_index(articles):
    """Build the index page listing all published articles."""
    items = ""
    for a in articles:
        items += f"""        <article class="card">
            <a href="{a['url']}">
                <h2>{a['title']}</h2>
                <p class="card-subtitle">{a['subtitle']}</p>
                <p class="card-meta">{a['date']}</p>
            </a>
        </article>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monumental Health — Publications</title>
    <meta name="description" content="Educational and analytical articles on veteran healthcare, clinical AI governance, and health policy from Monumental Health.">
    <style>
        :root {{
            --bg: #0f1117;
            --surface: #1a1d28;
            --text: #e4e6eb;
            --text-muted: #9ca3af;
            --accent: #6b8aff;
            --border: #2a2d3a;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Georgia, serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            max-width: 760px;
            margin: 0 auto;
            padding: 2rem 1.2rem;
        }}
        header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent);
            text-decoration: none;
            letter-spacing: -0.02em;
        }}
        .tagline {{
            color: var(--text-muted);
            margin-top: 0.5rem;
            font-size: 1rem;
        }}
        h1 {{
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.2rem;
            transition: border-color 0.2s;
        }}
        .card:hover {{
            border-color: var(--accent);
        }}
        .card a {{
            text-decoration: none;
            color: inherit;
        }}
        .card h2 {{
            font-size: 1.25rem;
            color: var(--text);
            margin-bottom: 0.4rem;
        }}
        .card-subtitle {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }}
        .card-meta {{
            color: var(--text-muted);
            font-size: 0.82rem;
        }}
        footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 1rem 0.8rem; }}
            .card {{ padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <span class="logo">Monumental Health</span>
        <p class="tagline">Veteran education, clinical AI governance, and health policy analysis</p>
    </header>
    <h1>Publications</h1>
{items}
    <footer>
        <p>Monumental Health · monumentalhealth.io</p>
        <p style="margin-top:0.5rem">Educational content. Not clinical advice.</p>
    </footer>
</body>
</html>"""


# Define articles to publish
articles_to_publish = [
    {
        "source": "/root/.hermes/shared/editorial/eu-product-liability-directive-linkedin-article-draft.md",
        "output": "eu-product-liability-directive.html",
        "title": "EU Product Liability Directive: What AI-Health Companies Must Know Before December 9",
        "subtitle": "Software and AI are now \"products\" under strict, no-fault liability. The transposition deadline is December 9, 2026.",
        "date": "November 16, 2026",
    },
    {
        "source": "/root/.hermes/shared/editorial/post-midterm-veterans-policy-linkedin-draft.md",
        "output": "post-midterm-veterans-policy.html",
        "title": "What the 2026 Election Means for Veterans Healthcare, AI Regulation, and Telehealth Policy",
        "subtitle": "A policy analysis of what changes — and what doesn't — when congressional power shifts.",
        "date": "November 16, 2026",
    },
]

published = []
for a in articles_to_publish:
    with open(a["source"], "r") as f:
        md_text = f.read()
    
    html_body, sources_html = md_to_html(md_text, a["title"])
    page_html = build_page(a["title"], html_body, sources_html, a["subtitle"], a["date"])
    
    out_path = os.path.join(SITE_DIR, a["output"])
    with open(out_path, "w") as f:
        f.write(page_html)
    
    published.append({**a, "url": a["output"]})
    print(f"Built: {out_path}")

# Build index
index_html = build_index(published)
with open(os.path.join(SITE_DIR, "index.html"), "w") as f:
    f.write(index_html)
print(f"Built: {os.path.join(SITE_DIR, 'index.html')}")

print(f"\nDone. {len(published)} articles published.")
