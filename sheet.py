"""
Googleスプレッドシートの読み書きを担当するモジュール。

環境変数:
  GOOGLE_SERVICE_ACCOUNT_JSON : サービスアカウントのJSON鍵(文字列そのまま)
  SPREADSHEET_ID              : 対象スプレッドシートのID
  SHEET_NAME                  : 対象シート名(例: "シート1")
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# スプレッドシートの列構成(1始まり)。沖縄営業リストの実際の列に合わせました。
COL_HOUJIN_BANGOU = 1
COL_COMPANY_NAME = 2
COL_ADDRESS = 3
COL_INDUSTRY = 4          # 業種(Places形式)
COL_HP = 5
COL_TEL = 6
COL_MAIL = 7
COL_FORM_URL = 8
COL_EMPLOYEE_COUNT = 9
COL_FETCHED_AT = 10
COL_STATUS = 11


def _get_client():
    sa_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    info = json.loads(sa_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_worksheet():
    client = _get_client()
    sh = client.open_by_key(os.environ["SPREADSHEET_ID"])
    return sh.worksheet(os.environ["SHEET_NAME"])


def fetch_unprocessed_companies(limit=100):
    """
    未取得(STATUS列が空欄)の企業行を最大limit件取得する。
    戻り値: [{"row": 行番号, "houjin_bangou": str, "company_name": str, "address": str, "industry": str}, ...]
    """
    ws = get_worksheet()
    all_values = ws.get_all_values()  # ヘッダー行込み

    targets = []
    for i, row in enumerate(all_values[1:], start=2):  # 2行目からデータ
        status = row[COL_STATUS - 1] if len(row) >= COL_STATUS else ""
        if status.strip():
            continue  # 取得済みはスキップ
        targets.append({
            "row": i,
            "houjin_bangou": row[COL_HOUJIN_BANGOU - 1] if len(row) >= COL_HOUJIN_BANGOU else "",
            "company_name": row[COL_COMPANY_NAME - 1] if len(row) >= COL_COMPANY_NAME else "",
            "address": row[COL_ADDRESS - 1] if len(row) >= COL_ADDRESS else "",
            "industry": row[COL_INDUSTRY - 1] if len(row) >= COL_INDUSTRY else "",
        })
        if len(targets) >= limit:
            break
    return targets


def update_companies(results):
    """
    複数行をまとめてbatch_updateする。
    results: [{"row": int, "hp": str, "tel": str, "mail": str, "form_url": str,
               "employee_count": str, "fetched_at": str, "status": str}, ...]
    """
    ws = get_worksheet()
    data = []
    for r in results:
        row = r["row"]
        values = [
            r.get("hp", ""),
            r.get("tel", ""),
            r.get("mail", ""),
            r.get("form_url", ""),
            r.get("employee_count", ""),
            r.get("fetched_at", ""),
            r.get("status", ""),
        ]
        # HP列(E)からSTATUS列(K)までをまとめて更新
        data.append({
            "range": f"E{row}:K{row}",
            "values": [values],
        })

    if data:
        ws.batch_update(data, value_input_option="USER_ENTERED")
