"""
メールアドレス取得モジュール。

優先順位:
  1. <a href="mailto:...">リンク(最も確実)
  2. 全文テキストの正規表現(ノイズ除外あり)
"""

import re
from bs4 import BeautifulSoup

MAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

EXCLUDE_PATTERNS = [
    r"@\d+\.\d+", r"wght@", r"viewport", r"example\.", r"sentry\.", r"schema\.",
    r"\.(jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff)$",
    r"\.(js|css|woff|woff2|ttf|eot|map)$",
    r"^\d", r"@\dx\.", r"[-_]\d+x\d+",
]


def get_mail(pages):
    """
    pages: [(url, html), ...] fetch_site_pages()の戻り値
    """
    if not pages:
        return None

    # 優先度1: mailtoリンク
    for _, html in pages:
        result = _try_mailto_link(html)
        if result:
            return result

    # 優先度2: 全文テキストの正規表現
    for _, html in pages:
        result = _try_text_pattern(html)
        if result:
            return result

    return None


def _try_mailto_link(html):
    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().startswith("mailto:"):
            email = href[7:].split("?")[0].strip()
            if email and _is_valid_email(email):
                return email
    return None


def _try_text_pattern(html):
    candidates = MAIL_PATTERN.findall(html)
    for email in candidates:
        if _is_valid_email(email):
            return email
    return None


def _is_valid_email(email):
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, email, re.IGNORECASE):
            return False
    return True
