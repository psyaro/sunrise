import pychromecast
import json
import os
from datetime import datetime, timedelta
import hashlib
import settings


class GoogleHome():
    def __init__(self):
        self.cast = None
        self.browser = None

    def find_device(self, friendly_name=None):
        """指定された名前のGoogle Homeデバイスを探して接続します。"""
        if friendly_name is None:
            friendly_name = settings.google_home_device_name
        print(f"デバイス '{friendly_name}' を検索中...")
        chromecasts, self.browser = pychromecast.get_listed_chromecasts(friendly_names=[friendly_name])
        if not chromecasts:
            print(f"'{friendly_name}' が見つかりません")
            return False

        self.cast = chromecasts[0]
        self.cast.wait()
        print(f"'{self.cast.name}' に接続しました。")
        return True

    def speak_to_google_home(self, text_to_speak="接続の試行を簡素化しました。これでお話しできるはずです。", volume=None):
        if not self.cast:
            print("エラー: デバイスに接続されていません。find_device()を先に呼び出してください。")
            return

        if volume is None:
            volume = settings.google_home_volume

        # 音量が0から1の範囲内であることを確認
        safe_volume = max(0.0, min(1.0, volume))
        self.cast.set_volume(safe_volume)

        # Text-to-Speechで喋らせる
        self.cast.media_controller.play_media(
            'http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=ja&q=' + text_to_speak,
            'audio/mp3'
        )
        self.cast.media_controller.block_until_active()
        print(f"「{text_to_speak}」と発話しました。")

    def stop_discovery(self):
        """デバイス検索を停止します。アプリケーション終了時に呼び出します。"""
        pychromecast.discovery.stop_discovery(self.browser)


def load_notification_history():
    """通知履歴をファイルから読み込みます。

    Returns:
        list: 通知履歴のリスト。各要素は{'message': str, 'timestamp': str, 'hash': str}の辞書
    """
    if not os.path.exists(settings.NOTIFICATION_HISTORY_FILE):
        return []

    try:
        with open(settings.NOTIFICATION_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"履歴ファイルの読み込みエラー: {e}")
        return []


def save_notification_history(history):
    """通知履歴をファイルに保存します。

    Args:
        history (list): 保存する通知履歴のリスト
    """
    try:
        with open(settings.NOTIFICATION_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"履歴ファイルの保存エラー: {e}")


def clean_old_notifications(history, hours=12):
    """指定時間より古い通知を履歴から削除します。

    Args:
        history (list): 通知履歴のリスト
        hours (int): 保持する時間（時間単位）

    Returns:
        list: クリーンアップされた履歴
    """
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cleaned_history = []

    for entry in history:
        try:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if entry_time > cutoff_time:
                cleaned_history.append(entry)
        except (ValueError, KeyError):
            # 不正なエントリはスキップ
            continue

    return cleaned_history


def get_message_hash(message):
    """メッセージのハッシュ値を生成します。

    Args:
        message (str): メッセージ文字列

    Returns:
        str: メッセージのMD5ハッシュ値
    """
    return hashlib.md5(message.encode('utf-8')).hexdigest()


def is_duplicate_notification(message, hours=12):
    """指定時間内に同じ通知が行われたかチェックします。

    Args:
        message (str): チェックするメッセージ
        hours (int): チェックする時間範囲（時間単位）

    Returns:
        bool: 重複している場合True、そうでない場合False
    """
    history = load_notification_history()
    history = clean_old_notifications(history, hours)

    message_hash = get_message_hash(message)

    for entry in history:
        if entry.get('hash') == message_hash:
            # 同じメッセージが見つかった
            timestamp = datetime.fromisoformat(entry['timestamp'])
            elapsed = datetime.now() - timestamp
            print(f"同じ通知が{elapsed.seconds // 3600}時間{(elapsed.seconds % 3600) // 60}分前に行われています。")
            return True

    return False


def add_notification_to_history(message):
    """通知を履歴に追加します。

    Args:
        message (str): 追加するメッセージ
    """
    history = load_notification_history()
    history = clean_old_notifications(history, hours=12)

    new_entry = {
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'hash': get_message_hash(message)
    }

    history.append(new_entry)
    save_notification_history(history)


def notify_with_duplicate_check(message, friendly_name=None, volume=None, hours=12):
    """重複チェック付きでGoogleHomeに通知します。

    12時間以内に同じ通知が行われていた場合は通知をスキップします。

    Args:
        message (str): 通知するメッセージ
        friendly_name (str): GoogleHomeのデバイス名（Noneの場合はsettingsから取得）
        volume (float): 音量（0.0～1.0、Noneの場合はsettingsから取得）
        hours (int): 重複チェックする時間範囲（時間単位）

    Returns:
        bool: 通知を実行した場合True、スキップした場合False
    """
    if friendly_name is None:
        friendly_name = settings.google_home_device_name
    if volume is None:
        volume = settings.google_home_volume

    # 重複チェック
    if is_duplicate_notification(message, hours):
        print(f"通知をスキップしました: {message}")
        return False

    # GoogleHomeで通知
    google_home = GoogleHome()
    if not google_home.find_device(friendly_name):
        print("デバイスが見つからないため通知できませんでした。")
        return False

    try:
        google_home.speak_to_google_home(message, volume)
        # 通知成功したら履歴に追加
        add_notification_to_history(message)
        return True
    except Exception as e:
        print(f"通知エラー: {e}")
        return False
    finally:
        google_home.stop_discovery()

def main():
    notify_with_duplicate_check("テスト通知です。これは重複チェック付きの通知機能のテストです。")
    # google_home = GoogleHome()
    # if google_home.find_device():
    #     google_home.speak_to_google_home()
    #     google_home.stop_discovery()

if __name__ == '__main__':
    main()