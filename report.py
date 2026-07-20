"""
処理結果をGmail(SMTP)で通知するモジュール。

環境変数:
  GMAIL_ADDRESS      : 送信元Gmailアドレス
  GMAIL_APP_PASSWORD : Googleアカウントの「アプリパスワード」(2段階認証が必要)
  REPORT_TO          : 通知先メールアドレス(複数はカンマ区切り)
"""

import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime


def send_report(stats: dict):
    """
    stats例:
      {
        "total": 100, "tel": 85, "employee": 60, "hp": 40, "mail": 20, "error": 3
      }
    """
    body = (
        f"本日の処理結果 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
        f"処理件数　: {stats.get('total', 0)}件\n"
        f"TEL取得　 : {stats.get('tel', 0)}件\n"
        f"従業員数　: {stats.get('employee', 0)}件\n"
        f"HP取得　　: {stats.get('hp', 0)}件\n"
        f"メール取得: {stats.get('mail', 0)}件\n"
        f"エラー　　: {stats.get('error', 0)}件\n"
    )

    msg = MIMEText(body)
    msg["Subject"] = "【営業リスト収集】本日の処理結果"
    msg["From"] = os.environ["GMAIL_ADDRESS"]
    msg["To"] = os.environ["REPORT_TO"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
        server.sendmail(
            os.environ["GMAIL_ADDRESS"],
            os.environ["REPORT_TO"].split(","),
            msg.as_string(),
        )
