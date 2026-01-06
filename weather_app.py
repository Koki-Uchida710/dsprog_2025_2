import flet as ft
import requests

# 定数：気象庁API
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

def main(page: ft.Page):
    # 1. ページの設定
    page.title = "気象庁天気予報アプリ"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 0

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

    def get_area_options():
        """地域リストを取得し、Dropdownの選択肢(Option)のリストとして返す"""
        try:
            response = requests.get(AREA_URL)
            response.raise_for_status()
            data = response.json()
            offices = data['offices']
            
            options = []
            for code, info in offices.items():
                options.append(ft.dropdown.Option(key=code, text=info['name']))
            return options
        except Exception as e:
            return [ft.dropdown.Option(key="error", text="地域リスト取得失敗")]

    def get_weather_forecast(area_code):
        """指定された地域コードの天気を取得して辞書で返す"""
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
                "icon_color": icon_color
            }
        except Exception as e:
            return {
                "area_name": "不明",
                "weather": "予報の取得に失敗しました。",
                "icon": ft.Icons.ERROR,
                "icon_color": "#f44336"
            }

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

        # 天気取得
        area_code = region_dropdown.value
        weather_data = get_weather_forecast(area_code)
        
        # 結果表示
        result_text.value = f"【{weather_data['area_name']}】の天気\n{weather_data['weather']}"
        result_icon.icon = weather_data['icon']
        result_icon.color = weather_data['icon_color']
        page.update()

    # タイトル
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon=ft.Icons.WB_SUNNY, size=40, color="#ffeb3b"),
                ft.Text("天気予報アプリ", size=30, weight=ft.FontWeight.BOLD, color="#1976d2"),
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

    # 実行ボタン
    submit_btn = ft.TextButton(
        content="予報を取得", 
        on_click=on_click_get_weather,
        style=ft.ButtonStyle(bgcolor="#1976d2", color="white"),
    )

    # 入力エリアをRowで横並び
    input_row = ft.Row(
        controls=[region_dropdown, submit_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
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
            width=500,
            height=150,
            alignment=ft.Alignment.CENTER,
        ),
        elevation=5,
        shadow_color="#1976d2",
    )

    bg_container.content.controls.extend([
        header,
        ft.Divider(height=20, color="#1976d2"),
        input_row,
        ft.Divider(height=20, color="#1976d2"),
        ft.Container(content=result_card, alignment=ft.Alignment.CENTER),
    ])
    
    page.add(bg_container)

ft.run(main)
