"""
メールアドレス取得モジュール。HPからメールアドレスを抽出する。
"""

import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

MAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

EXCLUDE_PATTERNS = [
    r"@\d+\.\d+", r"wght@", r"viewport", r"example\.", r"sentry\.", r"schema\.",
    r"\.(jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff)$",
    r"\.(js|css|woff|woff2|ttf|eot|map)$",
    r"^\d", r"@\dx\.", r"[-_]\d+x\d+",
]


def get_mail(hp_url):
    if not hp_url:
        return None

    try:
        html = _fetch_html(hp_url)
        if not html:
            return None

        candidates = MAIL_PATTERN.findall(html)
        if not candidates:
            return None

        for email in candidates:
            if _is_valid_email(email):
                return email

        return None

    except Exception:
        return None


def _fetch_html(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5, allow_redirects=True)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return resp.text
    except requests.RequestException:
        return None


def _is_valid_email(email):
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, email, re.IGNORECASE):
            return False
    return True
