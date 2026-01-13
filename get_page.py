from datetime import datetime
import random
import time
import requests
import discord_notify
import parse_html
import settings
import google_home_notify
import logging

# 駅名と列車種別の定義
STATIONS = {
    "東京": "%93%8C%8B%9E",
    "岡山": "%89%AA%8ER"
}


def make_url(from_city, to_city, date, hour, minute, train):
    """URLを生成"""
    base = "https://e5489.jr-odekake.net/e5489/cspc/CBDayTimeArriveSelRsvMyDiaPC"
    
    params = [
        f"inputDepartStName={STATIONS[from_city]}",
        f"inputArriveStName={STATIONS[to_city]}",
        "inputType=0",
        f"inputDate={date}",
        f"inputHour={hour:02d}",
        f"inputMinute={minute:02d}",
        "inputUniqueDepartSt=1",
        "inputUniqueArriveSt=1",
        "inputSearchType=2",
        f"inputTransferDepartStName1={STATIONS[from_city]}",
        f"inputTransferArriveStName1={STATIONS[to_city]}",
        "inputTransferDepartStUnique1=1",
        "inputTransferArriveStUnique1=1",
        "inputTransferTrainType1=0001",
        "inputSpecificTrainType1=2",
        f"inputSpecificBriefTrainKana1={train}",
        "SequenceType=0",
        "inputReturnUrl=goyoyaku/campaign/sunriseseto_izumo/form.html",
        "RTURL=https://www.jr-odekake.net/goyoyaku/campaign/sunriseseto_izumo/form.html",
        "undefined="
    ]
    
    return base + "?" + "&".join(params)

def get_html(url, use_tor=False):
    """指定したURLのHTMLを取得"""
    session = settings.get_session(use_tor)
    response = session.get(url)
    response.encoding = 'utf-8'
    return response.text

def search_main(direction, date, hour, minute, train, url_print=False):
    """空席検索のメイン処理"""
    logger = logging.getLogger(__name__)
    fh = logging.FileHandler('sunrise_search.log', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    if train == 1:
        train_name = r"%BB%B2%BD%D3%BB000"
    elif train == 2:
        train_name = r"%BB%BE%C4%BB%20000"
    elif train == 3:
        train_name = r"%BB%BE%C4%20%20000"
    elif train == 4:
        train_name = r"%BB%B2%BD%D3%20000"
    depsta = "東京" if direction == 1 else "岡山"
    arrsta = "岡山" if direction == 1 else "東京"
    url = make_url(depsta, arrsta, date, hour, minute, train_name)
    if url_print:
        print(f"URL: {url}")
    html_data = get_html(url, use_tor=False)
    try:
        vacancy_info = parse_html.extract_e5489_vacancy(html_data=html_data)
    except Exception as e:
        print(f"HTML解析エラー: {e}")
        logger.error(f"HTML解析エラー: {e}")
    else:
        for i, info in enumerate(vacancy_info):
            if i == 0:
                print(f'=== {info["date"]} {info["time"]} {info["route"]} ===')
            print(f"{info['train']}/{info['seat']}:{info['status']}")
            if info['status'] != "残席なし" and 'B寝台' in info['seat']:
                try:
                    message = f"【空席あり】 {info['date']} {info['time']} {info['route']}"
                    discord_notify.simple_notify(message)
                    discord_notify.notify_with_duplicate_check(message)
                except Exception as e:
                    print(f"Discord通知エラー: {e}")
                    logger.error(f"Discord通知エラー: {e}")
                try:
                    google_home_notify.notify_with_duplicate_check("空席があります。 確認してください。")
                except Exception as e:
                    print(f"Google Home通知エラー: {e}")
                    logger.error(f"Google Home通知エラー: {e}")
    time.sleep(random.randint(5, 20))  # サーバーへの負荷を避けるために少し待機

def main():
    search_main(1, datetime(2026, 1, 24).strftime("%Y%m%d"), 21, 00, 1)
    search_main(1, datetime(2026, 1, 24).strftime("%Y%m%d"), 21, 00, 2)
    search_main(2, datetime(2026, 1, 27).strftime("%Y%m%d"), 21, 00, 1)
    search_main(2, datetime(2026, 1, 27).strftime("%Y%m%d"), 21, 00, 2)
    search_main(1, datetime(2026, 2, 4).strftime("%Y%m%d"), 21, 00, 1)
    search_main(1, datetime(2026, 2, 4).strftime("%Y%m%d"), 21, 00, 2)
    search_main(1, datetime(2026, 2, 5).strftime("%Y%m%d"), 21, 00, 1)
    search_main(1, datetime(2026, 2, 5).strftime("%Y%m%d"), 21, 00, 2)
    search_main(2, datetime(2026, 2, 6).strftime("%Y%m%d"), 21, 00, 1)
    search_main(2, datetime(2026, 2, 6).strftime("%Y%m%d"), 21, 00, 2)
    search_main(2, datetime(2026, 2, 7).strftime("%Y%m%d"), 21, 00, 1)
    search_main(2, datetime(2026, 2, 7).strftime("%Y%m%d"), 21, 00, 2)
    search_main(1, datetime(2026, 2, 12).strftime("%Y%m%d"), 21, 00, 1)
    search_main(1, datetime(2026, 2, 12).strftime("%Y%m%d"), 21, 00, 2)
    search_main(1, datetime(2026, 2, 13).strftime("%Y%m%d"), 21, 00, 1)
    search_main(1, datetime(2026, 2, 13).strftime("%Y%m%d"), 21, 00, 2)
    search_main(1, datetime(2026, 2, 14).strftime("%Y%m%d"), 21, 00, 1)
    search_main(1, datetime(2026, 2, 14).strftime("%Y%m%d"), 21, 00, 2)


if __name__ == "__main__":
    main()