# -*- coding: utf-8 -*-
"""
HP(公式サイト)取得モジュール。優先度は低いため、当面は取得できなくても
処理全体は継続する(TEL・従業員数の取得を優先)。

既存のGASロジックがあればここに移植する。将来的にボリュームが増えて
GASでは処理しきれなくなった場合は、有償SERP API(SerpApi/DataForSEO等)へ
切り替える。

TODO:
  - 既存GASのHP特定ロジックをPythonに移植 or 同等のAPIに置き換え
"""


def get_hp(company_name: str, houjin_bangou: str = "") -> str | None:
    """
    企業名(+法人番号)から公式サイトURLを取得する。取得できなければNone。
    """
    # --- 未実装。見つからなければNoneを返すだけでOK(必須項目ではないため) ---
    return None
