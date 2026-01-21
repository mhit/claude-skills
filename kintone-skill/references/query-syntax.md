# KINTONE 検索クエリ構文

KINTONE REST API のクエリ構文の詳細リファレンスです。

## 基本構文

```
フィールドコード 演算子 "値" [and|or 条件...] [order by ...] [limit N] [offset N]
```

## 演算子一覧

| 演算子 | 意味 | 例 |
|--------|------|-----|
| `=` | 等しい | `ステータス = "完了"` |
| `!=` | 等しくない | `ステータス != "完了"` |
| `>` | より大きい | `金額 > 10000` |
| `<` | より小さい | `金額 < 10000` |
| `>=` | 以上 | `金額 >= 10000` |
| `<=` | 以下 | `金額 <= 10000` |
| `like` | 部分一致 | `タイトル like "報告"` |
| `not like` | 部分一致しない | `タイトル not like "テスト"` |
| `in` | リスト内に存在 | `ステータス in ("完了", "進行中")` |
| `not in` | リスト内に存在しない | `ステータス not in ("却下")` |

## 組み込み関数

| 関数 | 説明 | 例 |
|------|------|-----|
| `LOGINUSER()` | ログインユーザー | `担当者 = LOGINUSER()` |
| `PRIMARY_ORGANIZATION()` | 所属組織 | `部署 in (PRIMARY_ORGANIZATION())` |
| `NOW()` | 現在日時 | `期限 < NOW()` |
| `TODAY()` | 今日 | `作成日 = TODAY()` |
| `THIS_MONTH()` | 今月初日 | `作成日 >= THIS_MONTH()` |
| `LAST_MONTH()` | 先月初日 | `作成日 >= LAST_MONTH()` |
| `THIS_YEAR()` | 今年初日 | `作成日 >= THIS_YEAR()` |

## ソート・ページネーション

```
# ソート（複数可）
order by 更新日時 desc, 作成日時 asc

# 件数制限（最大500）
limit 100

# オフセット
offset 50

# 組み合わせ（順序は固定: order by → limit → offset）
ステータス = "完了" order by 更新日時 desc limit 100 offset 0
```

## 複合条件

```
# AND 条件
ステータス = "進行中" and 担当者 = LOGINUSER()

# OR 条件
ステータス = "完了" or ステータス = "却下"

# 括弧でグルーピング
(ステータス = "完了" or ステータス = "進行中") and 担当者 = LOGINUSER()
```

## フィールド型別の注意点

### 日付・日時フィールド

```
# 日付フィールド
作成日 = "2024-01-15"
作成日 >= "2024-01-01" and 作成日 < "2024-02-01"

# 日時フィールド（ISO 8601形式）
更新日時 >= "2024-01-15T00:00:00Z"
```

### 数値フィールド

```
# クォートなしでも可
金額 >= 10000
金額 > "10000"  # これも有効
```

### ユーザー選択フィールド

```
# ログイン名を指定
担当者 in ("user1", "user2")

# 関数を使用
担当者 = LOGINUSER()
```

### チェックボックスフィールド

```
# 選択されている値を指定
オプション in ("オプションA", "オプションB")
```

### ドロップダウン・ラジオボタン

```
優先度 = "高"
ステータス in ("完了", "進行中", "未着手")
```

## クエリビルダー（Python）

スクリプト `kintone_search.py` にはクエリビルダーが含まれています：

```python
from kintone_search import query

# メソッドチェーンでクエリ構築
q = (query()
    .equals("ステータス", "進行中")
    .and_where("担当者", "=", "田中")
    .or_where("優先度", "=", "高")
    .order_by("期限", "asc")
    .limit(50))

print(q.build())
# → ステータス = "進行中" and 担当者 = "田中" or 優先度 = "高" order by 期限 asc limit 50
```

## 自然言語変換

`parse_natural_query()` 関数で日本語からクエリに変換：

```python
from kintone_search import parse_natural_query

parse_natural_query("名前が田中")
# → 名前 = "田中"

parse_natural_query("ステータスが完了または進行中")
# → ステータス in ("完了", "進行中")

parse_natural_query("作成日が今日")
# → 作成日 = TODAY()
```
