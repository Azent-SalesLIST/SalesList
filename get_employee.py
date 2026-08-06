# -*- coding: utf-8 -*-
"""
従業員数取得モジュール。

候補: jobantenna(社名検索でヒットした場合のみ。IDの連番推測はできないので必ず
検索機能経由でマッチさせること)、gBizINFOなど。
複数ソースを順番に試し、最初に見つかったものを採用する設計にしておくと拡張しやすい。

TODO:
  - jobantennaのサイト内検索の実際のURL/パラメータを調査
  - gBizINFO API(法人番号から企業情報取得)を第二候補として実装
  - 会社名の表記ゆれ(株式会社の前後など)を吸収する正規化処理を入れる
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SalesListBot/1.0)"
}


def get_employee_count(company_name: str, houjin_bangou: str = "") -> str | None:
    """
    企業名(+法人番号)から従業員数を取得する。取得できなければNone。
    """
    result = _try_jobantenna(company_name)
    if result:
        return result

    result = _try_gbizinfo(houjin_bangou)
    if result:
        return result

    return None


def _try_jobantenna(company_name: str) -> str | None:
    # --- サイト内検索 → 会社名一致するページを開いて従業員数をパース ---
    raise NotImplementedError("jobantenna検索ロジック未実装")


def _try_gbizinfo(houjin_bangou: str) -> str | None:
    if not houjin_bangou:
        return None
    # --- gBizINFO API呼び出し(要APIキー登録)を実装 ---
    raise NotImplementedError("gBizINFO連携未実装")
