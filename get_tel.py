"""
電話番号(TEL)取得モジュール。

優先度が最も高い項目。iタウンページ等の企業電話帳サイトを社名+住所で検索して
電話番号を抽出する想定。サイトのHTML構造が変わったら都度パース部分を調整する。

TODO:
  - 実際のiタウンページ検索URL/パラメータを調査して実装する
  - 検索結果が複数ヒットした場合の会社名一致判定ロジックを入れる
  - 取得失敗時はNoneを返し、呼び出し側でstatusを"一部取得"にする
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SalesListBot/1.0)"
}


def get_tel(company_name: str, address: str = "") -> str | None:
    """
    企業名(+住所)から電話番号を検索して返す。取得できなければNone。
    """
    # --- ここに検索先サイトへのリクエスト & パース処理を実装 ---
    # 例:
    # resp = requests.get(SEARCH_URL, params={"keyword": company_name}, headers=HEADERS, timeout=10)
    # soup = BeautifulSoup(resp.text, "lxml")
    # ... 電話番号のパース ...
    raise NotImplementedError("TEL取得ロジック未実装")
