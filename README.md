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

| 機能 | 説明 | 推奨モデル |
|------|------|-----------|
| `/gemini-search` | 最新情報をウェブ検索 | gemini-2.5-flash |
| `/gemini-ocr` | PDF/画像からテキスト抽出 | gemini-3-pro-preview |
| `/gemini-analyze` | 大規模ファイル分析（100万トークン） | gemini-2.5-flash |
| `/gemini-review` | コードレビュー（セカンドオピニオン） | gemini-2.5-pro |
| `/gemini-design` | UI/UX設計 | gemini-3-flash-preview |

**Claudeが自発的に使う場面**:
- 大きなファイル（100KB+）→ Geminiに任せる
- 「最新の」「現在の」→ Geminiに検索させる
- 画像/PDF → Geminiに読ませる
- UI設計 → Geminiに相談
- 重要な変更 → Geminiにレビューさせる

---

### kintone-skill

KINTONE REST API連携スキル。レコードのCRUD、検索、スキーマキャッシュ、添付ファイル操作が可能。

| 機能 | 説明 |
|------|------|
| `/kintone schema` | フィールド定義を表示（キャッシュ対応） |
| `/kintone get` | レコードを1件取得 |
| `/kintone search` | レコードを検索（自然言語クエリ対応） |
| `/kintone add` | レコードを追加 |
| `/kintone update` | レコードを更新 |
| `/kintone delete` | レコードを削除 |
| `/kintone file` | 添付ファイルのアップロード/ダウンロード |

**環境変数の設定が必要**:
```bash
export KINTONE_DOMAIN="xxx.cybozu.com"
export KINTONE_API_TOKEN="your-api-token"
```

**自然言語クエリ変換**:
| 入力 | 変換結果 |
|------|---------|
| `名前が田中` | `名前 = "田中"` |
| `ステータスが完了または進行中` | `ステータス in ("完了", "進行中")` |
| `作成日が今日` | `作成日 = TODAY()` |
| `金額が10000以上` | `金額 >= "10000"` |

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
