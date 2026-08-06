"""
Googleスプレッドシートの読み書きを担当するモジュール。
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

COL_HOUJIN_BANGOU = 1
COL_COMPANY_NAME = 2
COL_ADDRESS = 3
COL_INDUSTRY = 4
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
    ws = get_worksheet()
    all_values = ws.get_all_values()

    targets = []
    for i, row in enumerate(all_values[1:], start=2):
        status = row[COL_STATUS - 1] if len(row) >= COL_STATUS else ""
        if status.strip() == "済":
            continue
        targets.append({
            "row": i,
            "houjin_bangou": row[COL_HOUJIN_BANGOU - 1] if len(row) >= COL_HOUJIN_BANGOU else "",
            "company_name": row[COL_COMPANY_NAME - 1] if len(row) >= COL_COMPANY_NAME else "",
            "address": row[COL_ADDRESS - 1] if len(row) >= COL_ADDRESS else "",
            "industry": row[COL_INDUSTRY - 1] if len(row) >= COL_INDUSTRY else "",
            "existing_hp": row[COL_HP - 1] if len(row) >= COL_HP else "",
            "existing_tel": row[COL_TEL - 1] if len(row) >= COL_TEL else "",
            "existing_mail": row[COL_MAIL - 1] if len(row) >= COL_MAIL else "",
            "existing_form_url": row[COL_FORM_URL - 1] if len(row) >= COL_FORM_URL else "",
            "existing_employee_count": row[COL_EMPLOYEE_COUNT - 1] if len(row) >= COL_EMPLOYEE_COUNT else "",
        })
        if len(targets) >= limit:
            break
    return targets


def update_companies(results):
    ws = get_worksheet()
    data = []
    for r in results:
        row = r["row"]
        hp = r.get("hp") or r.get("existing_hp", "")
        tel = r.get("tel") or r.get("existing_tel", "")
        mail = r.get("mail") or r.get("existing_mail", "")
        form_url = r.get("form_url") or r.get("existing_form_url", "")
        employee_count = r.get("employee_count") or r.get("existing_employee_count", "")

        values = [hp, tel, mail, form_url, employee_count, r.get("fetched_at", ""), r.get("status", "")]
        data.append({"range": f"E{row}:K{row}", "values": [values]})

    if data:
        ws.batch_update(data, value_input_option="USER_ENTERED")
