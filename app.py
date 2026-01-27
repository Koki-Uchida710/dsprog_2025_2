import flet as ft
import sqlite3

def main(page: ft.Page):
    page.title = "SUUMO賃貸データ検索アプリ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 800
    page.padding = 20

    # 1. データベースからデータを取る関数
    def get_data_from_db(keyword=""):
        conn = sqlite3.connect('suumo.db')
        cur = conn.cursor()
        
        if keyword:
            query = """
                SELECT name, station, price, age, floor_plan 
                FROM properties 
                WHERE station LIKE ? OR name LIKE ?
            """
            cur.execute(query, (f'%{keyword}%', f'%{keyword}%'))
        else:
            cur.execute("SELECT name, station, price, age, floor_plan FROM properties LIMIT 100")
            
        rows = cur.fetchall()
        conn.close()
        return rows

    # 2. データを画面の「表」に変換する関数
    def create_table_rows(data):
        rows = []
        for row in data:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row[0], size=12, weight="bold")), # 物件名
                        ft.DataCell(ft.Text(row[1], size=12)),                # 駅
                        ft.DataCell(ft.Text(f"{row[2]:,}円", color="blue")),  # 家賃
                        ft.DataCell(ft.Text(f"築{row[3]}年")),                # 築年数
                        ft.DataCell(ft.Text(row[4])),                         # 間取り
                    ]
                )
            )
        return rows

    # 3. 画面パーツの作成
    title_text = ft.Text("賃貸データ分析ダッシュボード", size=24, weight="bold", color="teal")
    status_text = ft.Text("データを読み込み中...", color="grey")

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("物件名")),
            ft.DataColumn(ft.Text("最寄駅")),
            ft.DataColumn(ft.Text("家賃"), numeric=True),
            ft.DataColumn(ft.Text("築年数"), numeric=True),
            ft.DataColumn(ft.Text("間取り")),
        ],
        rows=[],
        border=ft.border.all(1, "grey"),
        vertical_lines=ft.border.BorderSide(1, "grey"),
        heading_row_color="blueGrey50", 
        expand=True
    )

    # 4. イベント処理
    def search_click(e):
        keyword = search_field.value
        results = get_data_from_db(keyword)
        data_table.rows = create_table_rows(results)
        
        if len(results) == 0:
            status_text.value = "データが見つかりませんでした。"
            status_text.color = "red"
        else:
            status_text.value = f"検索結果: {len(results)} 件"
            status_text.color = "black"
            
        page.update()

    search_field = ft.TextField(
        label="駅名や物件名で検索（例: 新宿）", 
        width=400, 
        prefix_icon="search", 
        on_submit=search_click
    )
    
    search_button = ft.ElevatedButton(content=ft.Text("検索"), on_click=search_click)

    initial_data = get_data_from_db()
    data_table.rows = create_table_rows(initial_data)
    status_text.value = f"全データ表示中（最新100件）"

    page.add(
        ft.Column([
            title_text,
            ft.Divider(),
            ft.Row([search_field, search_button], alignment="center"),
            status_text,
            ft.Container(
                content=ft.Column([data_table], scroll=ft.ScrollMode.AUTO),
                height=500,
                border=ft.border.all(1, "grey50"),
                border_radius=10,
                padding=10
            )
        ])
    )

if __name__ == "__main__":
    ft.app(target=main)