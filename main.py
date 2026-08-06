"""
営業リスト収集のメイン処理。
"""

import os
import traceback
from datetime import datetime

from sheet import fetch_unprocessed_companies, update_companies
from get_hp import get_hp
from get_employee import get_employee_count
from get_mail import get_mail
from report import send_report

BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "10"))


def process_company(company: dict) -> dict:
    name = company["company_name"]
    address = company["address"]

    result = {
        "row": company["row"],
        "hp": "", "tel": "", "mail": "", "form_url": "", "employee_count": "",
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "",
        "existing_hp": company.get("existing_hp", ""),
        "existing_tel": company.get("existing_tel", ""),
        "existing_mail": company.get("existing_mail", ""),
        "existing_form_url": company.get("existing_form_url", ""),
        "existing_employee_count": company.get("existing_employee_count", ""),
    }

    got_any = False
    api_error = False

    hp_url = company.get("existing_hp") or None
    try:
        new_hp, new_tel = get_hp(name, address)
        if new_hp:
            result["hp"] = new_hp
            hp_url = new_hp
            got_any = True
        if new_tel:
            result["tel"] = new_tel
            got_any = True
    except Exception:
        api_error = True
        traceback.print_exc()

    try:
        if hp_url and not company.get("existing_employee_count"):
            emp = get_employee_count(hp_url)
            if emp:
                result["employee_count"] = emp
                got_any = True
    except Exception:
        traceback.print_exc()

    try:
        if hp_url and not company.get("existing_mail"):
            mail = get_mail(hp_url)
            if mail:
                result["mail"] = mail
                got_any = True
    except Exception:
        traceback.print_exc()

    if got_any:
        result["status"] = "済"
    elif api_error:
        result["status"] = "APIエラー"
    else:
        result["status"] = "未取得"

    return result


def main():
    companies = fetch_unprocessed_companies(limit=BATCH_SIZE)
    if not companies:
        print("未取得の企業がありません。終了します。")
        return

    results = []
    stats = {"total": 0, "hp": 0, "tel": 0, "employee": 0, "mail": 0, "error": 0}

    print(f"処理対象: {len(companies)}件")

    for company in companies:
        r = process_company(company)
        results.append(r)
        stats["total"] += 1
        if r["hp"]: stats["hp"] += 1
        if r["tel"]: stats["tel"] += 1
        if r["employee_count"]: stats["employee"] += 1
        if r["mail"]: stats["mail"] += 1
        if r["status"] != "済": stats["error"] += 1

    update_companies(results)
    print(f"スプレッドシート更新完了")

    try:
        send_report(stats)
        print("通知メール送信完了")
    except Exception:
        print(f"通知メール送信に失敗しました")
        traceback.print_exc()

    print(f"\n処理結果: {stats}")


if __name__ == "__main__":
    main()
