"""
メールアドレス取得モジュール。HPが取得できた場合のみ実行する
(HPが無ければスキップしてよい、優先度最下位の項目)。
"""

import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SalesListBot/1.0)"
}

MAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def get_mail(hp_url: str) -> str | None:
    """
    HPのトップページ(+可能なら会社概要/お問い合わせページ)からメールアドレスを抽出する。
    取得できなければNone。
    """
    if not hp_url:
        return None
    try:
        resp = requests.get(hp_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text()
    match = MAIL_PATTERN.search(text)
    return match.group(0) if match else None
