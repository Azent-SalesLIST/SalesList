# 営業リスト収集システム

## セットアップ手順

1. **このフォルダをGitHubリポジトリにpush**
   ```
   cd sales-list-collector
   git init
   git add .
   git commit -m "initial skeleton"
   git branch -M main
   git remote add origin <あなたのリポジトリURL>
   git push -u origin main
   ```
   ※分数制限を回避したい場合はリポジトリをpublicにする(コードに機密情報を含めない設計になっているため問題なし)。

2. **Googleサービスアカウントを作成**
   - Google Cloud ConsoleでサービスアカウントJSON鍵を発行
   - 対象スプレッドシートを、サービスアカウントのメールアドレスに「編集者」権限で共有

3. **GitHub Secretsに登録**（リポジトリ Settings → Secrets and variables → Actions）
   - `GOOGLE_SERVICE_ACCOUNT_JSON` : サービスアカウントJSONの中身をそのまま貼り付け
   - `SPREADSHEET_ID` : スプレッドシートURLの `/d/` と `/edit` の間の文字列
   - `SHEET_NAME` : シート名(タブ名)
   - `GMAIL_ADDRESS` : 通知送信元Gmail
   - `GMAIL_APP_PASSWORD` : Googleアカウントのアプリパスワード(2段階認証必須)
   - `REPORT_TO` : 通知先メールアドレス

4. **スプレッドシートの列構成**（`sheet.py`と合わせる。ずれる場合はsheet.py側の定数を変更）
   ```
   A:法人番号 B:会社名 C:住所 D:HP E:TEL F:メール G:フォームURL H:従業員数 I:取得日 J:ステータス
   ```

5. **未実装ロジックを埋める**（現状はスケルトンのみ）
   - `get_tel.py` : iタウンページ等からのTEL取得ロジック
   - `get_employee.py` : jobantenna社名検索 / gBizINFO連携
   - `get_hp.py` : 既存GASロジックの移植(任意)

6. **ローカルでのテスト**
   ```
   pip install -r requirements.txt
   export GOOGLE_SERVICE_ACCOUNT_JSON='...'
   export SPREADSHEET_ID='...'
   export SHEET_NAME='...'
   export BATCH_SIZE=3
   python main.py
   ```

7. **GitHub Actionsで手動実行して動作確認**（Actionsタブ → workflow_dispatchで実行）
   → 問題なければ`run.yml`のcronコメントアウトを外して定期実行を有効化。BATCH_SIZEも段階的に増やす(10→50→100)。
