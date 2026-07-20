"""
営業リスト収集のメイン処理。
優先度: TEL > 従業員数 > HP > メール(HPが取れた場合のみ)

1回の実行で処理する件数は BATCH_SIZE で調整する(まずは10〜50件で検証推奨)。
"""

import os
import traceback
from datetime import datetime

from sheet import fetch_unprocessed_companies, update_companies
from get_tel import get_tel
from get_employee import get_employee_count
from get_hp import get_hp
from get_mail import get_mail
from report import send_report

BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "10"))  # 検証中は小さめに


def process_company(company: dict) -> dict:
    name = company["company_name"]
    houjin_bangou = company["houjin_bangou"]
    address = company["address"]

    result = {
        "row": company["row"],
        "hp": "",
        "tel": "",
        "mail": "",
        "form_url": "",
        "employee_count": "",
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "",
    }

    got_any = False

    # 優先度1: TEL
    try:
        tel = get_tel(name, address)
        if tel:
            result["tel"] = tel
            got_any = True
    except NotImplementedError:
        pass
    except Exception:
        traceback.print_exc()

    # 優先度2: 従業員数
    try:
        emp = get_employee_count(name, houjin_bangou)
        if emp:
            result["employee_count"] = emp
            got_any = True
    except NotImplementedError:
        pass
    except Exception:
        traceback.print_exc()

    # 優先度3: HP(取れなくても継続)
    try:
        hp = get_hp(name, houjin_bangou)
        if hp:
            result["hp"] = hp
            got_any = True

            # 優先度4: メール(HPが取れた場合のみ)
            mail = get_mail(hp)
            if mail:
                result["mail"] = mail
    except Exception:
        traceback.print_exc()

    result["status"] = "済" if got_any else "エラー"
    return result


def main():
    companies = fetch_unprocessed_companies(limit=BATCH_SIZE)
    if not companies:
        print("未取得の企業がありません。終了します。")
        return

    results = []
    stats = {"total": 0, "tel": 0, "employee": 0, "hp": 0, "mail": 0, "error": 0}

    for company in companies:
        r = process_company(company)
        results.append(r)

        stats["total"] += 1
        if r["tel"]:
            stats["tel"] += 1
        if r["employee_count"]:
            stats["employee"] += 1
        if r["hp"]:
            stats["hp"] += 1
        if r["mail"]:
            stats["mail"] += 1
        if r["status"] == "エラー":
            stats["error"] += 1

    update_companies(results)

    try:
        send_report(stats)
    except Exception:
        print("通知メール送信に失敗しました(処理自体は完了)")
        traceback.print_exc()

    print(f"処理完了: {stats}")


if __name__ == "__main__":
    main()
