# Claude Skills

Claude Code用のカスタムスキル集。

## インストール

### 方法1: プラグインとして（推奨）

```bash
# マーケットプレイスとして登録
claude plugin marketplace add mhit/claude-skills

# スキルをインストール
claude plugin install gemini-skill@claude-skills
claude plugin install kintone-skill@claude-skills
```

### 方法2: 手動インストール

```bash
# .skillファイルをダウンロードしてスキルディレクトリにコピー
cp gemini-skill.skill ~/.claude/skills/
cp kintone-skill.skill ~/.claude/skills/

# 解凍
cd ~/.claude/skills
python3 -c "import zipfile; zipfile.ZipFile('gemini-skill.skill', 'r').extractall('.')"
python3 -c "import zipfile; zipfile.ZipFile('kintone-skill.skill', 'r').extractall('.')"
```

## スキル一覧

### gemini-skill

Gemini CLI連携スキル。Claudeがコンテキスト制限を克服するためにGeminiを自発的に活用する。

**環境変数**:
```bash
export GEMINI_API_KEY="your-api-key"           # 必須
export GEMINI_DEFAULT_MODEL="gemini-2.5-flash" # オプション
export GEMINI_TIMEOUT="900"                    # オプション（秒）
```

| 機能 | 説明 | 推奨モデル |
|------|------|-----------|
| `/gemini-search` | 最新情報をウェブ検索 | gemini-2.5-flash |
| `/gemini-ocr` | PDF/画像からテキスト抽出 | gemini-3-pro-preview |
| `/gemini-analyze` | 大規模ファイル分析（100万トークン） | gemini-2.5-flash |
| `/gemini-review` | コードレビュー（セカンドオピニオン） | gemini-2.5-pro |
| `/gemini-design` | UI/UX設計 | gemini-3-flash-preview |

**パイプ（stdin）対応**:

大量データをパイプで渡して処理可能:

```bash
# ログ分析
cat production.log | gemini-call.sh --stdin --task analyze "エラーを特定して"

# git diff レビュー
git diff | gemini-call.sh --stdin --task review "この変更をレビューして"

# 複数ファイル結合
cat src/*.ts | gemini-call.sh --stdin "このコードの問題点は？"
```

**gemini-call.sh オプション**:

| オプション | 説明 |
|-----------|------|
| `-m, --model MODEL` | モデル指定 |
| `--task TASK` | タスクタイプ（ocr/design/review/analyze/quick） |
| `-f, --file FILE` | ファイルを含める（複数可） |
| `--stdin` | 標準入力から読み込み |
| `-t, --timeout SECS` | タイムアウト秒（デフォルト: 900） |
| `-j, --json` | JSON出力 |
| `-y, --yolo` | 自動承認 |

**CLAUDE.mdテンプレート**: `gemini-skill/templates/CLAUDE.gemini.md` をプロジェクトにコピーしてカスタマイズ可能。

**Claudeが自発的に使う場面**:
- 大きなファイル（100KB+）→ Geminiに任せる
- 「最新の」「現在の」→ Geminiに検索させる
- 画像/PDF → Geminiに読ませる
- UI設計 → Geminiに相談
- 重要な変更 → Geminiにレビューさせる

---

### kintone-skill

KINTONE REST API連携スキル。レコードのCRUD、検索、スキーマキャッシュ、添付ファイル操作が可能。

**環境変数**:
```bash
# 必須
export KINTONE_DOMAIN="xxx.cybozu.com"
export KINTONE_API_TOKEN="your-api-token"

# オプション
export KINTONE_DEFAULT_APP="123"
export KINTONE_CACHE_DIR="~/.cache/kintone-skill"
export KINTONE_CACHE_TTL="3600"
```

**基本コマンド**:

| 機能 | 説明 |
|------|------|
| `/kintone apps` | アクセス可能なアプリ一覧 |
| `/kintone schema` | フィールド定義を表示（キャッシュ対応） |
| `/kintone get` | レコードを1件取得 |
| `/kintone search` | レコードを検索（自然言語クエリ対応） |
| `/kintone search --all` | 全件取得（Cursor API、500件制限なし） |
| `/kintone add` | レコードを追加（100件以上は自動分割） |
| `/kintone update` | レコードを更新 |
| `/kintone delete` | レコードを削除 |
| `/kintone file` | 添付ファイルのアップロード/ダウンロード |
| `/kintone status` | ステータス更新（ワークフロー） |
| `/kintone comment` | コメント追加/一覧/削除 |

**拡張機能**:

```bash
# アプリ一覧（名前でフィルタ）
scripts/kintone.sh apps --name "顧客"

# 全件取得（Cursor API）
scripts/kintone.sh search 123 --all

# ワークフローステータス更新
scripts/kintone.sh status 123 1 "承認"

# コメント追加
scripts/kintone.sh comment 123 1 add "確認しました"
```

**Auto-chunking**: 100件以上のレコード追加/更新時、自動的に100件ごとに分割してAPIコール。

**自然言語クエリ変換**:
| 入力 | 変換結果 |
|------|---------|
| `名前が田中` | `名前 = "田中"` |
| `ステータスが完了または進行中` | `ステータス in ("完了", "進行中")` |
| `作成日が今日` | `作成日 = TODAY()` |
| `担当者が自分` | `担当者 = LOGINUSER()` |
| `金額が10000以上` | `金額 >= "10000"` |

**API制限と対応**:

| API | 制限 | 対応 |
|-----|------|------|
| Get records | 500件/回 | `--all`（Cursor API） |
| Add/Update | 100件/回 | Auto-chunking |
| Bulk request | 20リクエスト | アトミック処理 |

**スキーマキャッシュ**:
- 初回アクセス時にアプリのフィールド定義を取得
- `~/.cache/kintone-skill/schemas/` にキャッシュ
- Claudeがフィールド名・型を即座に把握し、正確なクエリを生成可能

---

## スキル構造

各スキルは以下の構造に従う：

```
skill-name/
├── SKILL.md           # メイン定義（必須）
├── scripts/           # 実行スクリプト（オプション）
├── references/        # 詳細ドキュメント（オプション）
└── assets/            # テンプレート等（オプション）
```

## ライセンス

MIT
