"""
HPとその関連ページ(会社概要・採用情報・お問い合わせ等)をまとめて取得する。
従業員数・メール抽出の両方でこの結果を使い回すことで、
アクセス回数とサーバー負荷を最小化する。
"""

import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 会社概要・採用情報・お問い合わせ、関連しそうなページを幅広く拾うキーワード
SUBPAGE_KEYWORDS = [
    "会社概要", "会社情報", "企業情報", "会社案内", "企業概要", "コーポレート",
    "about", "company", "corporate", "profile", "プロフィール",
    "採用", "採用情報", "採用サイト", "recruit", "careers", "career", "求人",
    "お問い合わせ", "問い合わせ", "contact", "inquiry",
]

MAX_SUBPAGES = 4       # 見に行く関連ページ数の上限
REQUEST_INTERVAL = 0.5  # リクエスト間隔(秒) サーバー負荷対策


def fetch_site_pages(hp_url):
    """
    HP + 関連ページを取得する。
    戻り値: [(url, html), ...] のリスト(取得できたページのみ)
    """
    if not hp_url:
        return []

    pages = []

    top_html = _fetch_html(hp_url)
    if not top_html:
        return []

    pages.append((hp_url, top_html))

    subpage_urls = _find_subpages(top_html, hp_url)
    for url in subpage_urls[:MAX_SUBPAGES]:
        time.sleep(REQUEST_INTERVAL)
        sub_html = _fetch_html(url)
        if sub_html:
            pages.append((url, sub_html))

    return pages


def _find_subpages(html, base_url):
    soup = BeautifulSoup(html, "lxml")
    found = []
    seen = set()

    for a in soup.find_all("a", href=True):
        link_text = a.get_text().strip().lower()
        href = a["href"]

        for keyword in SUBPAGE_KEYWORDS:
            if keyword.lower() in link_text or keyword.lower() in href.lower():
                full_url = urljoin(base_url, href)
                # 同一ドメイン内のみ(外部リンクは辿らない)
                if full_url not in seen and full_url.startswith("http"):
                    seen.add(full_url)
                    found.append(full_url)
                break

    return found


def _fetch_html(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return resp.text
    except requests.RequestException:
        return None
