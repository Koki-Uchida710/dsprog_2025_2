import flet as ft
import requests
import sqlite3
from datetime import datetime
from pathlib import Path

# 定数：気象庁API
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"
DB_PATH = "weather_data.db"


class WeatherDatabase:
    """SQLiteを使用した天気データベースの管理"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベーススキーマを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # テーブル1: 地域情報
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS areas (
                area_code TEXT PRIMARY KEY,
                area_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # テーブル2: 天気予報
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecasts (
                forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT NOT NULL,
                forecast_date DATE NOT NULL,
                forecast_time TEXT NOT NULL,
                weather_description TEXT NOT NULL,
                retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (area_code) REFERENCES areas(area_code),
                UNIQUE(area_code, forecast_date, forecast_time)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """データベース接続を取得"""
        return sqlite3.connect(self.db_path)
    
    def insert_area(self, area_code: str, area_name: str):
        """地域情報をDBに挿入"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO areas (area_code, area_name)
                VALUES (?, ?)
            ''', (area_code, area_name))
            conn.commit()
        except Exception as e:
            print(f"Error inserting area: {e}")
        finally:
            conn.close()
    
    def insert_forecast(self, area_code: str, forecast_date: str, forecast_time: str, weather: str):
        """天気予報をDBに挿入"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO forecasts 
                (area_code, forecast_date, forecast_time, weather_description)
                VALUES (?, ?, ?, ?)
            ''', (area_code, forecast_date, forecast_time, weather))
            conn.commit()
        except Exception as e:
            print(f"Error inserting forecast: {e}")
        finally:
            conn.close()
    
    def get_forecast(self, area_code: str, forecast_date: str = None):
        """DBから天気予報を取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if forecast_date:
            cursor.execute('''
                SELECT forecast_time, weather_description, retrieved_at
                FROM forecasts
                WHERE area_code = ? AND forecast_date = ?
                ORDER BY forecast_time
            ''', (area_code, forecast_date))
        else:
            # 最新の日付のデータを取得
            cursor.execute('''
                SELECT DISTINCT forecast_date FROM forecasts
                WHERE area_code = ?
                ORDER BY forecast_date DESC
                LIMIT 1
            ''', (area_code,))
            result = cursor.fetchone()
            
            if result:
                latest_date = result[0]
                cursor.execute('''
                    SELECT forecast_time, weather_description, retrieved_at
                    FROM forecasts
                    WHERE area_code = ? AND forecast_date = ?
                    ORDER BY forecast_time
                ''', (area_code, latest_date))
            else:
                return []
        
        forecasts = cursor.fetchall()
        conn.close()
        return forecasts
    
    def get_available_dates(self, area_code: str):
        """特定の地域の利用可能な日付を取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT forecast_date FROM forecasts
            WHERE area_code = ?
            ORDER BY forecast_date DESC
        ''', (area_code,))
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates


def main(page: ft.Page):
    # 1. ページの設定
    page.title = "気象庁天気予報アプリ（DB版）"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 0
    
    # データベース初期化
    db = WeatherDatabase()
    
    # 背景コンテナ
    bg_container = ft.Container(
        bgcolor="#e3f2fd",
        expand=True,
        content=ft.Column(
            controls=[],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        padding=30,
    )
    
    # --------------------------------------------------
    # データ取得ロジック（関数）
    # --------------------------------------------------
    def get_area_options():
        """地域リストを取得し、Dropdownの選択肢(Option)のリストとして返す"""
        try:
            response = requests.get(AREA_URL)
            response.raise_for_status()
            data = response.json()
            offices = data['offices']
            
            # FletのDropdown用オプションを作成
            options = []
            for code, info in offices.items():
                options.append(ft.dropdown.Option(key=code, text=info['name']))
                # DBに地域情報を保存
                db.insert_area(code, info['name'])
            return options
        except Exception as e:
            return [ft.dropdown.Option(key="error", text="地域リスト取得失敗")]
    
    def get_weather_forecast_api(area_code):
        """気象庁APIから天気を取得してDBに保存"""
        url = FORECAST_URL_TEMPLATE.format(area_code)
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # データ構造から直近の天気を抽出
            time_series = data[0]['timeSeries'][0]
            weather_area = time_series['areas'][0]
            
            area_name = weather_area['area']['name']
            weather = weather_area['weathers'][0]
            
            # 今日の日付
            today = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M')
            
            # DBに保存
            db.insert_forecast(area_code, today, current_time, weather)
            
            # 天気に応じてアイコンを選択
            if "晴" in weather:
                icon = ft.Icons.WB_SUNNY
                icon_color = "#ffeb3b"
            elif "雨" in weather:
                icon = ft.Icons.UMBRELLA
                icon_color = "#2196f3"
            elif "雪" in weather:
                icon = ft.Icons.AC_UNIT
                icon_color = "#e3f2fd"
            elif "曇" in weather:
                icon = ft.Icons.CLOUD
                icon_color = "#9e9e9e"
            else:
                icon = ft.Icons.WB_CLOUDY
                icon_color = "#757575"
            
            return {
                "area_name": area_name,
                "weather": weather,
                "icon": icon,
                "icon_color": icon_color,
                "source": "API"
            }
        except Exception as e:
            return {
                "area_name": "不明",
                "weather": "予報の取得に失敗しました。",
                "icon": ft.Icons.ERROR,
                "icon_color": "#f44336",
                "source": "error"
            }
    
    def get_weather_from_db(area_code):
        """DBから天気情報を取得"""
        forecasts = db.get_forecast(area_code)
        
        if not forecasts:
            return None
        
        # 最新の予報を取得
        latest_forecast = forecasts[0]
        forecast_time, weather, retrieved_at = latest_forecast
        
        # 天気情報を取得
        cursor = db.get_connection().cursor()
        cursor.execute('SELECT area_name FROM areas WHERE area_code = ?', (area_code,))
        result = cursor.fetchone()
        area_name = result[0] if result else "不明"
        cursor.connection.close()
        
        # 天気に応じてアイコンを選択
        if "晴" in weather:
            icon = ft.Icons.WB_SUNNY
            icon_color = "#ffeb3b"
        elif "雨" in weather:
            icon = ft.Icons.UMBRELLA
            icon_color = "#2196f3"
        elif "雪" in weather:
            icon = ft.Icons.AC_UNIT
            icon_color = "#e3f2fd"
        elif "曇" in weather:
            icon = ft.Icons.CLOUD
            icon_color = "#9e9e9e"
        else:
            icon = ft.Icons.WB_CLOUDY
            icon_color = "#757575"
        
        return {
            "area_name": area_name,
            "weather": weather,
            "icon": icon,
            "icon_color": icon_color,
            "source": "DB",
            "retrieved_at": retrieved_at
        }
    
    # --------------------------------------------------
    # イベントハンドラ
    # --------------------------------------------------
    def on_click_get_weather(e):
        # 地域が選択されていない場合
        if not region_dropdown.value:
            result_text.value = "地域を選択してください！"
            result_icon.icon = ft.Icons.WARNING
            result_icon.color = "#ff9800"
            page.update()
            return
        
        # ローディング表示に変更
        result_text.value = "データを取得中..."
        result_icon.icon = ft.Icons.HOURGLASS_EMPTY
        result_icon.color = "#2196f3"
        page.update()
        
        # 天気取得（APIから取得してDBに保存）
        area_code = region_dropdown.value
        weather_data = get_weather_forecast_api(area_code)
        
        # 結果表示
        result_text.value = f"【{weather_data['area_name']}】の天気\n{weather_data['weather']}\n(ソース: {weather_data['source']})"
        result_icon.icon = weather_data['icon']
        result_icon.color = weather_data['icon_color']
        page.update()
    
    def on_click_load_from_db(e):
        # 地域が選択されていない場合
        if not region_dropdown.value:
            result_text.value = "地域を選択してください！"
            result_icon.icon = ft.Icons.WARNING
            result_icon.color = "#ff9800"
            page.update()
            return
        
        area_code = region_dropdown.value
        weather_data = get_weather_from_db(area_code)
        
        if weather_data:
            result_text.value = f"【{weather_data['area_name']}】の天気\n{weather_data['weather']}\n(ソース: {weather_data['source']})\n取得: {weather_data['retrieved_at']}"
            result_icon.icon = weather_data['icon']
            result_icon.color = weather_data['icon_color']
        else:
            result_text.value = "DBにデータがありません。\nAPIから取得してください。"
            result_icon.icon = ft.Icons.STORAGE
            result_icon.color = "#9e9e9e"
        
        page.update()
    
    # --------------------------------------------------
    # UIパーツの作成
    # --------------------------------------------------
    # タイトル
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon=ft.Icons.WB_SUNNY, size=40, color="#ffeb3b"),
                ft.Text("天気予報アプリ（DB版）", size=30, weight=ft.FontWeight.BOLD, color="#1976d2"),
                ft.Icon(icon=ft.Icons.CLOUD, size=40, color="#9e9e9e"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.Alignment.CENTER,
        padding=10,
    )
    
    # 地域選択ドロップダウン
    region_options = get_area_options()
    region_dropdown = ft.Dropdown(
        label="地域を選択",
        hint_text="予報を見たい地域を選んでください",
        options=region_options,
        width=300,
        border_color="#1976d2",
    )
    
    # ボタン
    api_btn = ft.Button(
        content="APIから取得",
        on_click=on_click_get_weather,
        style=ft.ButtonStyle(bgcolor="#1976d2", color="white"),
    )
    
    db_btn = ft.Button(
        content="DBから取得",
        on_click=on_click_load_from_db,
        style=ft.ButtonStyle(bgcolor="#43a047", color="white"),
    )
    
    # 入力エリアをRowで横並び
    input_row = ft.Row(
        controls=[region_dropdown, api_btn, db_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )
    
    # 結果表示エリア
    result_icon = ft.Icon(icon=ft.Icons.WB_SUNNY, size=50, color="#ffeb3b")
    result_text = ft.Text(value="ここに結果が表示されます", size=20, color="#424242")
    result_row = ft.Row(
        controls=[result_icon, result_text],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )
    result_card = ft.Card(
        content=ft.Container(
            content=result_row,
            padding=20,
            width=600,
            height=150,
            alignment=ft.Alignment.CENTER,
        ),
        elevation=5,
        shadow_color="#1976d2",
    )
    
    # --------------------------------------------------
    # ページへの追加
    # --------------------------------------------------
    bg_container.content.controls.extend([
        header,
        ft.Divider(height=20, color="#1976d2"),
        input_row,
        ft.Divider(height=20, color="#1976d2"),
        ft.Container(content=result_card, alignment=ft.Alignment.CENTER),
    ])
    
    page.add(bg_container)


ft.run(main)
