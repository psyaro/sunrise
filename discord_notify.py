from datetime import datetime
import hashlib
import json
import os
import requests
import time
import settings

def simple_notify(message):
    """Discordにシンプルに通知します。

    Args:
        message (str): 通知するメッセージ
    """
    hook = settings.discord_webhook
    data = {
        "content": message
    }
    try:
        requests.post(hook, data=data)
    except Exception as e:
        print(f"Discord通知エラー: {e}")

def notify_with_duplicate_check(message):
    """重複チェック付きでDiscordに通知します。

    3時間以内に同じ通知が行われていた場合は通知をスキップします。

    Args:
        message (str): 通知するメッセージ
    Returns:
        bool: 通知を実行した場合True、スキップした場合False
    """
    # 通知履歴を読み込み
    if os.path.exists(settings.NOTIFICATION_HISTORY_FILE_DISCORD):
        with open(settings.NOTIFICATION_HISTORY_FILE_DISCORD, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    # メッセージのハッシュ値を生成
    message_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
    # 3時間以内に同じメッセージが通知されていないかチェック
    three_hours_ago = datetime.now().timestamp() - (3 * 60 * 60)
    for entry in history:
        if entry.get('hash') == message_hash and datetime.fromisoformat(entry['timestamp']).timestamp() > three_hours_ago:
            # 同じメッセージが見つかった
            timestamp = datetime.fromisoformat(entry['timestamp'])
            elapsed = datetime.now() - timestamp
            print(f"同じ通知が{elapsed.seconds // 3600}時間{(elapsed.seconds % 3600) // 60}分前に行われています。")
            return False

    # 通知を送信
    hook = settings.discord_webhook_duplicate_checked
    data = {
        "content": message
    }
    try:
        requests.post(hook, data=data)
    except Exception as e:
        print(f"Discord通知エラー: {e}")
        return False
    # 通知成功
    print("Discordに通知を送信しました。")
    # 履歴に追加
    new_entry = {
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'hash': message_hash
    }
    history.append(new_entry)
    
    with open(settings.NOTIFICATION_HISTORY_FILE_DISCORD, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return True

if __name__ == "__main__":
    notify_with_duplicate_check("テスト通知です。これは重複チェック付きの通知機能のテストです。")