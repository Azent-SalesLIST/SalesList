"""
従業員数取得モジュール。

優先順位:
  1. 構造化データ(JSON-LD の numberOfEmployees)
  2. テーブル構造(th/td, dt/dd のラベル+値ペア)
  3. 全文テキストの正規表現(全角数字を正規化してから検索)
"""

import re
import json
import unicodedata
from bs4 import BeautifulSoup

EMPLOYEE_LABEL_PATTERN = re.compile(r"従業員|社員数|職員数|スタッフ数")

EMPLOYEE_TEXT_PATTERNS = [
    r"従業員(?:数)?[:：\s]*(?:約)?(\d+)(?:人|名)?",
    r"社員(?:数)?[:：\s]*(?:約)?(\d+)(?:人|名)?",
    r"スタッフ(?:数)?[:：\s]*(?:約)?(\d+)(?:人|名)?",
    r"職員(?:数)?[:：\s]*(?:約)?(\d+)(?:人|名)?",
    r"(\d+)\s*(?:人|名)の従業員",
    r"(\d+)\s*(?:人|名)の社員",
]


def get_employee_count(pages):
    """
    pages: [(url, html), ...] fetch_site_pages()の戻り値
    """
    if not pages:
        return None

    # 優先度1: 構造化データ(全ページ横断で先に探す)
    for _, html in pages:
        result = _try_structured_data(html)
        if result:
            return result

    # 優先度2: テーブル構造
    for _, html in pages:
        result = _try_table_structure(html)
        if result:
            return result

    # 優先度3: 全文テキストの正規表現
    for _, html in pages:
        result = _try_text_pattern(html)
        if result:
            return result

    return None


def _valid_count(num_str):
    try:
        n = int(num_str)
        if 1 <= n <= 1000000:
            return str(n)
    except ValueError:
        pass
    return None


def _try_structured_data(html):
    """JSON-LD構造化データから numberOfEmployees を探す"""
    soup = BeautifulSoup(html, "lxml")
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except (TypeError, ValueError):
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            emp = item.get("numberOfEmployees")
            if emp is None:
                continue
            # QuantitativeValue形式 {"@type": "QuantitativeValue", "value": 50}
            if isinstance(emp, dict):
                emp = emp.get("value")
            result = _valid_count(str(emp))
            if result:
                return result
    return None


def _try_table_structure(html):
    """th/td, dt/dd のラベル+値ペアから探す"""
    soup = BeautifulSoup(html, "lxml")

    # th → td (同じtr内)
    for th in soup.find_all("th"):
        if EMPLOYEE_LABEL_PATTERN.search(th.get_text()):
            td = th.find_next_sibling("td")
            if td:
                text = unicodedata.normalize('NFKC', td.get_text())
                match = re.search(r"(\d+)", text)
                if match:
                    result = _valid_count(match.group(1))
                    if result:
                        return result

    # dt → dd
    for dt in soup.find_all("dt"):
        if EMPLOYEE_LABEL_PATTERN.search(dt.get_text()):
            dd = dt.find_next_sibling("dd")
            if dd:
                text = unicodedata.normalize('NFKC', dd.get_text())
                match = re.search(r"(\d+)", text)
                if match:
                    result = _valid_count(match.group(1))
                    if result:
                        return result

    return None


def _try_text_pattern(html):
    """全文テキストを正規化してから正規表現で探す"""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text()
    text = unicodedata.normalize('NFKC', text)  # 全角数字→半角に変換
    text = re.sub(r'\s+', ' ', text)

    for pattern in EMPLOYEE_TEXT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = _valid_count(match.group(1))
            if result:
                return result

    return None
