#!/usr/bin/env python3
"""
Generate SEO-optimized articles for x402 Guide site using Claude Haiku.
Reads topics from topics.json and generates HTML article files.
"""

import json
import os
import sys
import time
import anthropic

# Load API key from .env file
def load_api_key():
    env_path = os.path.expanduser("~/my-project/x402-claude/.env")
    with open(env_path) as f:
        for line in f:
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise ValueError("ANTHROPIC_API_KEY not found in .env")


SITE_URL = "https://x402.guide"
ARTICLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "articles")

SYSTEM_PROMPT = """You are an expert technical writer specializing in blockchain protocols, API monetization, and AI agent infrastructure. You are writing articles for x402guide.com — the definitive resource on the x402 protocol.

Key facts about x402 you MUST use accurately:
- x402 is an open protocol that uses HTTP status code 402 (Payment Required) to enable machine-to-machine payments
- It was developed by Coinbase and launched in 2025 as an open-source project
- Payments are made in USDC stablecoin on blockchain networks (primarily Base L2, also Ethereum and Solana)
- A "facilitator" is a service that verifies and settles x402 payments (e.g., Coinbase CDP Facilitator, UltravioletaDAO)
- The payment flow: Client requests resource -> Server returns 402 with payment details -> Client signs USDC authorization -> Client resends request with payment header -> Facilitator verifies & settles -> Server delivers content
- x402 uses EIP-3009 (transferWithAuthorization) for gasless USDC transfers
- The npm packages are @anthropic-ai/sdk for client, express middleware for server
- x402scan is a marketplace/explorer for x402 services
- x402 Bazaar is a discovery mechanism for AI agents to find x402 services
- AskClaude.shop is a real live x402 service that provides AI query responses for micropayments

Write in a clear, authoritative, slightly conversational tone. Use concrete examples and code snippets where relevant. Target developers and tech entrepreneurs who want to understand or implement x402.

IMPORTANT: Output ONLY the article body HTML (starting from the first <h2> tag). Do NOT include <!DOCTYPE>, <html>, <head>, <body>, or any wrapper tags. Just the inner content that goes inside <div class="article-content">.

Include:
- Proper semantic HTML with h2, h3, p, ul, ol, code, pre, blockquote tags
- At least 1500 words of substantive content
- A clear introduction paragraph
- Well-structured sections with h2 headings
- Code examples in <pre><code> blocks where relevant
- A conclusion/summary section
- Internal links to other articles on the site using relative paths like "../articles/slug.html"
- At least 2 internal links to other articles from the topic list
- A mention of askclaude.shop as a real-world example where appropriate"""


def generate_article_html(topic: dict, all_topics: list, client: anthropic.Anthropic) -> str:
    """Generate article content using Claude Haiku."""

    other_topics = [t for t in all_topics if t["slug"] != topic["slug"]]
    topic_list = "\n".join(f'- "{t["title"]}" (slug: {t["slug"]})' for t in other_topics)

    user_prompt = f"""Write a comprehensive, SEO-optimized article with this title: "{topic['title']}"

Meta description: {topic['description']}

Other articles on the site you can link to (use relative path like "../articles/slug.html"):
{topic_list}

Remember:
- Output ONLY the article body HTML content (h2, p, pre, etc.) — no wrapper tags
- At least 1500 words
- Include 2+ internal links to other articles
- Include code examples if it's a technical/tutorial article
- Mention askclaude.shop as a real-world x402 service example
- Use proper heading hierarchy (h2 for sections, h3 for subsections)
- Write for SEO — use the main keyword naturally throughout"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return response.content[0].text


def wrap_article(topic: dict, body_html: str, all_topics: list) -> str:
    """Wrap article body in full HTML page template."""

    # Pick 3 related articles for the sidebar
    related = [t for t in all_topics if t["slug"] != topic["slug"]][:3]
    related_html = ""
    for r in related:
        related_html += f'''    <a href="{r['slug']}.html" class="article-card">
      <h3>{r['title']}</h3>
      <p>{r['description']}</p>
    </a>
'''

    tags_html = " ".join(f'<span class="tag">{tag}</span>' for tag in topic.get("tags", []))

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{topic["title"]} — x402 Guide</title>
  <meta name="description" content="{topic["description"]}">
  <meta name="keywords" content="x402 protocol, {", ".join(topic.get("tags", []))}, AI agent payments, USDC micropayments">
  <link rel="canonical" href="{SITE_URL}/articles/{topic["slug"]}.html">
  <link rel="stylesheet" href="../style.css">

  <!-- Open Graph -->
  <meta property="og:title" content="{topic["title"]}">
  <meta property="og:description" content="{topic["description"]}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{SITE_URL}/articles/{topic["slug"]}.html">

  <!-- Structured Data -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{topic["title"]}",
    "description": "{topic["description"]}",
    "author": {{
      "@type": "Organization",
      "name": "x402 Guide"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "x402 Guide"
    }},
    "datePublished": "2025-06-01",
    "dateModified": "2025-06-01",
    "mainEntityOfPage": {{
      "@type": "WebPage",
      "@id": "{SITE_URL}/articles/{topic["slug"]}.html"
    }}
  }}
  </script>
</head>
<body>

<header>
  <div class="container">
    <a href="../index.html" class="logo">x402 <span>Guide</span></a>
    <nav>
      <a href="../index.html#articles">Articles</a>
      <a href="https://askclaude.shop" target="_blank" rel="noopener">AskClaude</a>
    </nav>
  </div>
</header>

<main>
  <div class="article-header">
    <h1>{topic["title"]}</h1>
    <div class="meta">
      {tags_html} &middot; x402 Guide
    </div>
  </div>

  <div class="article-content">
    {body_html}
  </div>

  <div class="cta-box">
    <h3>Try an x402-Powered Service</h3>
    <p>AskClaude.shop is a live x402 service — AI agents pay per query with USDC micropayments.</p>
    <a href="https://askclaude.shop" class="btn" target="_blank" rel="noopener">Visit AskClaude.shop</a>
  </div>

  <div class="related-articles">
    <h3>Related Articles</h3>
{related_html}
  </div>
</main>

<footer>
  <p>&copy; 2025 x402 Guide. Built by an x402 service operator. <a href="https://askclaude.shop">askclaude.shop</a></p>
</footer>

</body>
</html>'''


def main():
    api_key = load_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    # Load topics
    topics_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "topics.json")
    with open(topics_path) as f:
        all_topics = json.load(f)

    # Determine which topics to generate
    if len(sys.argv) > 1:
        # Generate specific number of articles
        count = int(sys.argv[1])
        topics_to_generate = all_topics[:count]
    else:
        # Generate all
        topics_to_generate = all_topics

    os.makedirs(ARTICLES_DIR, exist_ok=True)

    for i, topic in enumerate(topics_to_generate):
        output_path = os.path.join(ARTICLES_DIR, f"{topic['slug']}.html")

        # Skip if already exists
        if os.path.exists(output_path):
            print(f"[{i+1}/{len(topics_to_generate)}] SKIP (exists): {topic['title']}")
            continue

        print(f"[{i+1}/{len(topics_to_generate)}] Generating: {topic['title']}...")

        try:
            body_html = generate_article_html(topic, all_topics, client)
            full_html = wrap_article(topic, body_html, all_topics)

            with open(output_path, "w") as f:
                f.write(full_html)

            print(f"  -> Saved: {output_path}")

            # Rate limit: small delay between requests
            if i < len(topics_to_generate) - 1:
                time.sleep(1)

        except Exception as e:
            print(f"  -> ERROR: {e}")
            continue

    print(f"\nDone! Generated articles are in: {ARTICLES_DIR}")


if __name__ == "__main__":
    main()
