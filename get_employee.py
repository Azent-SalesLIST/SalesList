"""
従業員数取得モジュール。HPのHTMLから従業員数を抽出する。
"""

import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SalesListBot/1.0)"
}

EMPLOYEE_PATTERNS = [
    r"従業員(?:数)?[:：\s]*(?:約)?(\d+)(?:人|名)?",
    r"社員(?:数)?[:：\s]*(?:約)?(\d+)(?:人|名)?",
    r"スタッフ(?:数)?[:：\s]*(?:約)?(\d+)(?:人|名)?",
    r"職員(?:数)?[:：\s]*(?:約)?(\d+)(?:人|名)?",
    r"(\d+)\s*(?:人|名)の従業員",
    r"(\d+)\s*(?:人|名)の社員",
]


def get_employee_count(hp_url):
    if not hp_url:
        return None

    try:
        html = _fetch_html(hp_url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)

        for pattern in EMPLOYEE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                emp_num = match.group(1)
                try:
                    emp_int = int(emp_num)
                    if 1 <= emp_int <= 1000000:
                        return str(emp_int)
                except ValueError:
                    continue

        return None

    except Exception:
        return None


def _fetch_html(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return resp.text
    except requests.RequestException:
        return None
