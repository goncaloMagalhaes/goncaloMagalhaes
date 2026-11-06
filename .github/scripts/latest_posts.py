"""Write the latest posts from goncalomagalhaes.com into README.md.

Reads the English RSS feed and replaces whatever sits between the
<!-- writing:start --> and <!-- writing:end --> markers. Run by
.github/workflows/latest-posts.yml; standard library only, so the
workflow needs nothing installed.
"""
import email.utils
import re
import urllib.request
import xml.etree.ElementTree as ET

FEED = "https://goncalomagalhaes.com/en/feed.xml"
HOW_MANY = 3
README = "README.md"


def md_escape(text: str) -> str:
    return text.replace("[", r"\[").replace("]", r"\]")


def latest_posts() -> list[str]:
    request = urllib.request.Request(FEED, headers={"User-Agent": "goncaloMagalhaes-profile-readme"})
    with urllib.request.urlopen(request, timeout=30) as response:
        channel = ET.fromstring(response.read()).find("channel")
    lines = []
    for item in channel.findall("item")[:HOW_MANY]:
        title = md_escape(item.findtext("title", "").strip())
        link = item.findtext("link", "").strip()
        date = email.utils.parsedate_to_datetime(item.findtext("pubDate"))
        lines.append(f"- [{title}]({link}) · {date:%b %Y}")
    return lines


def main() -> None:
    lines = latest_posts()
    if not lines:
        raise SystemExit("The feed has no posts; README left as it was.")
    with open(README, encoding="utf-8") as f:
        text = f.read()
    updated, found = re.subn(
        r"(<!-- writing:start -->).*?(<!-- writing:end -->)",
        lambda m: m.group(1) + "\n" + "\n".join(lines) + "\n" + m.group(2),
        text,
        flags=re.S,
    )
    if not found:
        raise SystemExit("README.md has no writing markers.")
    with open(README, "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    main()
