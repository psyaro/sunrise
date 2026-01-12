# 空席通知システム

空席情報を自動的にチェックし、空席が見つかった場合にDiscord WebhookとGoogleHomeで通知するスクリプトです。
これ以降の文章はAIによる自動生成です

## 機能

- 🚂 空席情報を自動取得
- 💬 Discord Webhookによる通知
- 🔊 GoogleHomeでの音声通知
- 🔄 12時間以内の重複通知を自動防止

## 必要な環境

- Python 3.7以上
- GoogleHomeデバイス（同じネットワーク上）

## インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/sunrise.git
cd sunrise
```

### 2. 必要なパッケージのインストール

```bash
pip install requests pandas beautifulsoup4 pychromecast
```

### 3. 設定ファイルの作成

`settings.py.example` をコピーして `settings.py` を作成し、必要な情報を設定します。

```bash
cp settings.py.example settings.py
```

`settings.py` を編集：

```python
import requests

# Discord Webhook URL
discord_webhook = 'https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN'

# GoogleHome設定
google_home_device_name = 'YOUR_GOOGLE_HOME_DEVICE_NAME'  # GoogleHomeのデバイス名
google_home_volume = 0.5  # 音量（0.0～1.0）

def get_session(use_tor=False):
    session = requests.Session()
    if not use_tor:
        session.proxies.update({
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        })
    # ... 以下省略
```

## 使い方

### 基本的な実行

```bash
python get_page.py
```

### GoogleHome通知のテスト

```bash
python google_home_notify.py
```

## ファイル構成

```
sunrise/
├── get_page.py                 # メインスクリプト（空席チェック）
├── parse_html.py               # HTML解析モジュール
├── google_home_notify.py       # GoogleHome通知モジュール
├── settings.py                 # 設定ファイル（.gitignore対象）
├── settings.py.example         # 設定ファイルのテンプレート
├── notification_history.json   # 通知履歴（自動生成、.gitignore対象）
├── .gitignore
└── README.md
```

## 主な機能の説明

### 空席検索（get_page.py）

指定した日付・時刻・方向・列車種別で空席情報を取得します。

```python
search_main(
    direction=1,           # 1: 東京→岡山, 2: 岡山→東京
    date="20260212",       # YYYYMMDD形式
    hour=21,               # 時
    minute=0,              # 分
    train=1                
)
```

### GoogleHome通知（google_home_notify.py）

#### 基本的な通知

```python
from google_home_notify import GoogleHome

google_home = GoogleHome()
if google_home.find_device():
    google_home.speak_to_google_home("こんにちは")
    google_home.stop_discovery()
```

#### 重複チェック付き通知

```python
from google_home_notify import notify_with_duplicate_check

# デフォルト設定（settings.pyから取得）
notify_with_duplicate_check("空席が見つかりました")

# カスタム設定
notify_with_duplicate_check(
    message="空席が見つかりました",
    friendly_name="GoogleHome",  # デバイス名を指定
    volume=0.8,                   # 音量を指定
    hours=6                       # 重複チェック期間を6時間に変更
)
```

### 重複通知防止機能

- 通知履歴は `notification_history.json` に保存されます
- メッセージ内容をMD5ハッシュ化して重複判定
- デフォルトで12時間以内の同一メッセージは通知をスキップ
- 古い履歴は自動的にクリーンアップ

## カスタマイズ

### 検索対象の変更

`get_page.py` の `main()` 関数内で検索条件を変更できます：

```python
def main():
    search_main(1, datetime(2026, 2, 12).strftime("%Y%m%d"), 21, 0, 1)

    search_main(1, datetime(2026, 2, 12).strftime("%Y%m%d"), 21, 0, 2)
```

### 通知条件の変更

`get_page.py:72-83` で通知条件を変更できます：

```python
# 現在はB寝台の空席のみ通知
if info['status'] != "残席なし" and 'B寝台' in info['seat']:
    # 通知処理
```

## トラブルシューティング

### GoogleHomeが見つからない

1. GoogleHomeとPCが同じネットワークに接続されているか確認
2. `settings.py` の `google_home_device_name` が正しいか確認
3. GoogleHomeアプリでデバイス名を確認

### Proxy接続エラー

`settings.py` のProxy設定を確認してください。Proxyを使用しない場合は、`get_session()` 関数を修正してください。

### Discord通知が送信されない

Discord Webhook URLが正しいか確認してください。

## 注意事項

- このスクリプトは教育目的で作成されています
- サーバーに過度な負荷をかけないよう、適切な間隔でアクセスしてください
- `settings.py` と `notification_history.json` は `.gitignore` に含まれており、Gitリポジトリにはコミットされません
