---
name: kintone-skill
description: "KINTONE REST API を操作するスキル。レコードの取得・追加・更新・削除、検索、スキーマ確認、添付ファイル操作が可能。ユーザーが「KINTONE」「kintone」「キントーン」について言及した場合、またはレコード操作・データベース操作を KINTONE で行いたい場合に使用します。トリガー: (1) KINTONE のレコードを取得/追加/更新/削除したい (2) KINTONE で検索したい (3) KINTONE のスキーマ/フィールド定義を確認したい (4) KINTONE の添付ファイルを操作したい"
---

# KINTONE Skill

KINTONE REST API を Claude から直接操作するスキルです。

## 私（Claude）が使うべき場面

| 場面 | なぜこのスキル？ | 使うコマンド |
|------|-----------------|-------------|
| **「KINTONEのデータを見たい」** | 直接 API を叩ける | `/kintone get` `/kintone search` |
| **「KINTONEに追加して」** | JSON 形式で投入 | `/kintone add` |
| **「KINTONEを更新して」** | レコード ID 指定で更新 | `/kintone update` |
| **「このファイルをKINTONEに添付」** | ファイルアップロード→レコード紐付け | `/kintone file` |
| **「フィールド構成を確認」** | スキーマをキャッシュして即座に参照 | `/kintone schema` |

## 事前設定

以下の環境変数が必要です：

```bash
# 必須
export KINTONE_DOMAIN="xxx.cybozu.com"
export KINTONE_API_TOKEN="your-api-token"

# オプション
export KINTONE_DEFAULT_APP="123"           # デフォルトアプリID
export KINTONE_CACHE_DIR="~/.cache/kintone-skill"
export KINTONE_CACHE_TTL="3600"            # キャッシュ有効期限（秒）
```

## コマンド一覧

### /kintone schema - スキーマ確認

アプリのフィールド定義を表示します。結果はキャッシュされます。

```bash
# 基本
scripts/kintone.sh schema 123

# キャッシュを更新
scripts/kintone.sh schema 123 --refresh

# JSON 出力
scripts/kintone.sh schema 123 --json
```

### /kintone get - レコード取得

```bash
# 1件取得
scripts/kintone.sh get 123 1

# JSON 出力
scripts/kintone.sh get 123 1 --json
```

### /kintone search - レコード検索

```bash
# 全件取得（最大100件）
scripts/kintone.sh search 123

# クエリ指定
scripts/kintone.sh search 123 'ステータス = "完了"'

# 自然言語風クエリ
scripts/kintone.sh query "ステータスが完了"
# → ステータス = "完了" に変換される

# ページネーション
scripts/kintone.sh search 123 --limit 50 --offset 100
```

**クエリ構文（自然言語変換サポート）**:

| 自然言語 | 変換後 |
|---------|--------|
| `名前が田中` | `名前 = "田中"` |
| `ステータスが完了または進行中` | `ステータス in ("完了", "進行中")` |
| `作成日が今日` | `作成日 = TODAY()` |
| `担当者が自分` | `担当者 = LOGINUSER()` |
| `メモが空でない` | `メモ != ""` |
| `金額が10000以上` | `金額 >= "10000"` |

### /kintone add - レコード追加

```bash
# JSON で追加
scripts/kintone.sh add 123 '{"タイトル": "新規タスク", "担当者": "田中"}'

# ファイルから追加
scripts/kintone.sh add 123 --file record.json
```

### /kintone update - レコード更新

```bash
scripts/kintone.sh update 123 1 '{"ステータス": "完了"}'
```

### /kintone delete - レコード削除

```bash
# カンマ区切りで複数指定可能
scripts/kintone.sh delete 123 1,2,3
```

### /kintone file - 添付ファイル操作

```bash
# アップロード
scripts/kintone.sh file upload ./document.pdf
# → fileKey が返される

# ダウンロード
scripts/kintone.sh file download abc123def456 --output ./downloaded.pdf

# レコードの添付ファイル一覧
scripts/kintone.sh file list --app 123 --record 1 --field 添付ファイル
```

## スキーマキャッシュの仕組み

1. 初回アクセス時に API からスキーマ取得
2. `~/.cache/kintone-skill/schemas/app_XXX.json` に保存
3. 次回以降はキャッシュから読み込み（高速）
4. `--refresh` でキャッシュ更新
5. デフォルト有効期限: 1時間

**メリット**: 私（Claude）がフィールド名・型を即座に把握し、正しいクエリ・データ形式を提案できます。

## Python API（直接利用）

スクリプトを Python から直接インポートして使うこともできます：

```python
from kintone_client import KintoneClient
from kintone_schema import SchemaManager
from kintone_search import query, parse_natural_query

# クライアント
client = KintoneClient()
response = client.get_record(app_id=123, record_id=1)

# スキーマ管理
schema_mgr = SchemaManager()
schema = schema_mgr.get_schema(app_id=123)

# クエリビルダー
q = query().equals("ステータス", "完了").order_by("更新日時", "desc").limit(10)
print(q.build())  # ステータス = "完了" order by 更新日時 desc limit 10
```

## エラーハンドリング

| エラー | 原因 | 対処 |
|--------|------|------|
| `KINTONE_DOMAIN not found` | 環境変数未設定 | `export KINTONE_DOMAIN=...` |
| `401 Unauthorized` | API トークン無効 | トークンを再発行 |
| `403 Forbidden` | 権限不足 | アプリの API トークン権限を確認 |
| `404 Not Found` | アプリ/レコードが存在しない | ID を確認 |
| `400 Bad Request` | リクエスト形式エラー | フィールド名・型を確認 |

## 参考リファレンス

- [references/query-syntax.md](references/query-syntax.md) - 検索クエリ構文の詳細
- [references/authentication.md](references/authentication.md) - 認証方法の詳細
