# 気象庁天気予報アプリケーション（DB版）

## 概要
気象庁のAPIから取得した天気情報をSQLiteデータベースに格納し、APIと数据ベースの両方から天気情報を取得できるアプリケーションです。

## DB設計

### スキーマ設計

#### テーブル1: `areas`（地域情報テーブル）
地域の基本情報を管理します。

| カラム名 | データ型 | 説明 | 制約 |
|---------|---------|------|------|
| area_code | TEXT | 地域コード（気象庁の地域コード） | PRIMARY KEY |
| area_name | TEXT | 地域名 | NOT NULL |
| created_at | TIMESTAMP | 記録日時 | DEFAULT CURRENT_TIMESTAMP |

**設計の考え方:**
- `area_code`をプライマリーキーにすることで、地域の重複を防ぐ
- 気象庁のAPIから地域情報を取得した時点で自動的に挿入

#### テーブル2: `forecasts`（天気予報テーブル）
天気予報のデータを管理します。

| カラム名 | データ型 | 説明 | 制約 |
|---------|---------|------|------|
| forecast_id | INTEGER | 予報レコードの一意なID | PRIMARY KEY AUTOINCREMENT |
| area_code | TEXT | 地域コード | FOREIGN KEY |
| forecast_date | DATE | 予報の日付 | NOT NULL |
| forecast_time | TEXT | 予報の時刻 | NOT NULL |
| weather_description | TEXT | 天気の説明 | NOT NULL |
| retrieved_at | TIMESTAMP | 取得日時 | DEFAULT CURRENT_TIMESTAMP |

**ユニーク制約:**
- `(area_code, forecast_date, forecast_time)`の組み合わせをユニークとすることで、同じ日時の同じ地域の予報の重複を防ぐ
- UPDATEする際には`INSERT OR REPLACE`を使用

**設計の考え方:**
- `forecast_id`を自動採番のプライマリーキーにすることで、各レコードを一意に識別
- `area_code`は外部キー制約で`areas`テーブルと関連付ける
- 複合ユニーク制約により、同じ時刻の予報の重複を防止
- `retrieved_at`で取得した時刻を記録することで、データの新しさを判断可能

### 正規化
- **第1正規形（1NF）:** すべてのカラムがアトミック（分割不可能）な値を含む
- **第2正規形（2NF）:** テーブル内にすべての非キー属性がプライマリーキーに完全従属している
- **第3正規形（3NF）:** 非キー属性が他の非キー属性に従属していない
  - `areas`テーブルで地域情報を分離することで達成

## 機能

### APIから取得
- 気象庁のAPIから最新の天気情報を取得
- 取得したデータを自動的にDBに保存
- 地域情報も同時にDBに保存

### DBから取得
- 以前に保存した天気情報をDBから取得
- データベースには複数日の予報を保存可能

## 使用方法

```bash
# アプリケーションの実行
python weather_app_with_db.py
```

### 操作フロー
1. 地域をドロップダウンから選択
2. 「APIから取得」ボタン: 最新の天気情報をAPIから取得してDBに保存
3. 「DBから取得」ボタン: 保存済みの天気情報をDBから表示

## ファイル構成
- `weather_app_with_db.py`: メインのアプリケーション
- `weather_data.db`: SQLiteデータベース（初回実行時に自動作成）

## 今後の拡張案（オプション）

### 1. 日付選択機能
複数日の予報データを保存し、日付を選択して過去/将来の予報を表示

```python
def get_available_dates(area_code):
    # DBから利用可能な日付を取得
    cursor.execute('''
        SELECT DISTINCT forecast_date FROM forecasts
        WHERE area_code = ?
        ORDER BY forecast_date DESC
    ''', (area_code,))
    return [row[0] for row in cursor.fetchall()]
```

### 2. 複数時間の予報表示
`forecast_time`を活用して、複数時間の予報を一覧表示

### 3. 天気統計
期間内の天気パターンを分析し、統計情報を表示

### 4. エクスポート機能
DBから特定期間のデータをCSV/JSONでエクスポート
