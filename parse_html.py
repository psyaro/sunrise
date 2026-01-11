from bs4 import BeautifulSoup

def extract_e5489_vacancy_core(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    try:
        date = soup.find('span', class_='route-options-header__date').get_text(strip=True)
    except:
        print(soup.get_text().strip().replace(' ', '').replace('\n', ''))
        raise
    # 1. 列車ごとのブロックを取得
    # クラス名 'route-train-list' が各列車の情報をまとめている
    train_sections = soup.find_all('div', class_='route-train-list')

    for section in train_sections:
        train_time_dept_arr = section.find_all('p', class_='route-train-list__time')
        train_time_dept_arr: str = " - ".join([t.get_text(strip=True) for t in train_time_dept_arr])
        train_sta_dept_arr = section.find_all('h4', class_='route-train-list__heading')
        train_sta_dept_arr: str = " → ".join([s.get_text(strip=True) for s in train_sta_dept_arr])
        # 列車名の取得
        train_name_tag = section.find('div', class_='route-train-list__train-name')
        if train_name_tag:
            # <p>タグ内のテキストを取得 (例: 特急サンライズ出雲)
            train_name = train_name_tag.get_text(strip=True)
        else:
            train_name = "不明な列車"

        # 座席・空席情報のテーブルを取得
        table = section.find('table', class_='seat-facility')
        if not table:
            continue

        # ヘッダー(th)から設備の詳細（B寝台、禁煙個室など）を取得
        # data-search-id をキーにして情報を保存
        seat_definitions = {}
        headers = table.find_all('th')
        for th in headers:
            search_id = th.get('data-search-id')
            # 設備アイコン（imgタグ）のalt属性をつなげて設備名にする
            # 例: <img alt="B寝台"> <img alt="禁煙個室"> -> "B寝台 禁煙個室"
            imgs = th.find_all('img')
            seat_name = " ".join([img.get('alt', '') for img in imgs if img.get('alt')])
            seat_definitions[search_id] = seat_name

        # ボディ(td)から空席状況を取得
        # tdタグの data-search-id が thタグのものと対応している
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            for cell in cells:
                search_id = cell.get('data-search-id')
                
                # 空席状況アイコンのalt属性を取得 (例: "残席なし", "空席あり")
                status_img = cell.find('img')
                if status_img:
                    status = status_img.get('alt', '')
                else:
                    status = cell.get_text(strip=True)

                # 対応する設備名を取得
                seat_name = seat_definitions.get(search_id, "不明な設備")

                # 結果リストに追加
                results.append({
                    'date': date,
                    'train': train_name,
                    'seat': seat_name,
                    'status': status,
                    'time': train_time_dept_arr,
                    'route': train_sta_dept_arr,
                })

    return results

def extract_e5489_vacancy(path="form.html", html_data=None):
    """e5489の空席情報を抽出する"""
    file_path = path  # 保存したHTMLファイル名を指定

    try:
        if html_data is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_data = f.read()
            
        vacancy_info = extract_e5489_vacancy_core(html_data)

    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    return vacancy_info

def main():
    vacancy_info = extract_e5489_vacancy(path="form.html")
    for info in vacancy_info:
        print(f'=== {info["date"]} {info["time"]} {info["route"]} ===')
        print(f"{info['train']}/{info['seat']}: {info['status']}")

if __name__ == "__main__":
    main()