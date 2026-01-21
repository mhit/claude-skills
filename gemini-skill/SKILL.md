---
name: using-gemini
description: "Integrates Gemini CLI for tasks beyond Claude's context limits. Fetches latest information via web search, performs OCR on images/PDFs, analyzes large files (100KB+), reviews code for second opinions, and assists with UI/UX design. Use when users need: (1) Large file analysis, (2) Latest information, (3) PDF/image reading, (4) UI/UX design, (5) Code review second opinion. Commands: /gemini, /gemini-search, /gemini-ocr, /gemini-analyze, /gemini-review, /gemini-design"
---

# Gemini CLI Integration Skill

**私（Claude）がGeminiを自発的に使うためのスキル。**

## 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|-----------|------|
| `GEMINI_API_KEY` | Yes | - | Gemini APIキー |
| `GEMINI_DEFAULT_MODEL` | No | `gemini-2.5-flash` | デフォルトモデル |
| `GEMINI_TIMEOUT` | No | `900` (15分) | タイムアウト秒 |

```bash
# 必須
export GEMINI_API_KEY="your-api-key"

# オプション
export GEMINI_DEFAULT_MODEL="gemini-2.5-pro"
export GEMINI_TIMEOUT="600"
```

## 私がGeminiを使うべき場面

| 場面 | なぜGemini? | 使うコマンド |
|------|------------|-------------|
| **大きなファイル（100KB+）** | 私のコンテキストに収まらない | `/gemini-analyze` |
| **最新情報が必要** | 私の知識は古い場合がある | `/gemini-search` |
| **PDF/画像を読む** | Geminiの画像認識が優秀 | `/gemini-ocr` |
| **UI/UX設計** | Gemini 3がデザイン得意 | `/gemini-design` |
| **自分の回答を検証** | 別視点でダブルチェック | `/gemini-review` |

## モデル選択

| タスク | モデル | 理由 |
|--------|-------|------|
| 画像/PDF OCR | `gemini-3-pro-preview` | マルチモーダル最強 |
| UI/UX設計 | `gemini-3-flash-preview` | デザイン得意 |
| コードレビュー | `gemini-2.5-pro` | 思考モデル |
| 大規模分析 | `gemini-2.5-flash` | コスパ最高 |
| ウェブ検索 | `gemini-2.5-flash` | 高速 |
| 簡単な質問 | `gemini-2.5-flash-lite` | 最速 |

## コマンド

### /gemini-search [質問]

**最新情報をウェブから取得**。私の知識が古い可能性がある時に使う。

```bash
# Gemini内蔵の検索機能を使う
gemini -m gemini-2.5-flash "@search 2026年の最新のReact状態管理ライブラリ"

# または直接質問（Geminiが必要に応じて検索）
gemini -m gemini-2.5-flash "最新のTypeScript 5.x の新機能を調べて"
```

**使う場面**:
- 「最新の〇〇」を聞かれた時
- 技術の現在のベストプラクティスを確認したい時
- 私の知識と現状が違う可能性がある時

### /gemini-ocr [ファイル]

**PDF/画像からテキスト抽出**。Gemini 3 Proのマルチモーダル機能を使う。

```bash
# @でファイルを直接含める（推奨）
gemini -m gemini-3-pro-preview "@./screenshot.png この画像の内容を読み取って"

# stdinで渡す
gemini -m gemini-3-pro-preview "この画像を読み取って" < image.png
```

**使う場面**:
- ユーザーがスクリーンショットを提供した時
- PDFの内容を読み取る必要がある時
- 画像内のコードを抽出したい時

### /gemini-analyze [ファイル群]

**大規模ファイル/ログの一括分析**。100万トークンのコンテキストを活用。

```bash
# @でファイルを含める（推奨）
gemini -m gemini-2.5-flash "@./src/ このコードベースのアーキテクチャを分析して"

# 複数ファイルをパイプ
cat logs/*.log | gemini -m gemini-2.5-flash "エラーパターンを特定して"
```

**使う場面**:
- ファイルが100KB以上の時
- 複数の大きなファイルを比較する時
- 私のコンテキストに収まらない時

### /gemini-review

**コードレビュー（セカンドオピニオン）**。Gemini 2.5 Proの思考モデルで深い分析。

```bash
# 変更をレビュー
git diff | gemini -m gemini-2.5-pro "この変更をレビューして。バグ、セキュリティ、改善点を指摘して"

# 私の回答を検証
echo "私の回答: ..." | gemini -m gemini-2.5-pro "この回答を検証して。誤りや不足があれば指摘して"
```

**使う場面**:
- 重要な変更を本番デプロイする前
- 自分の回答に自信がない時
- 別の視点が欲しい時

### /gemini-design

**UI/UX設計**。Gemini 3 Flashのデザイン能力を活用。

```bash
gemini -m gemini-3-flash-preview "以下の要件でUIを設計して: ダッシュボード、モバイルファースト、ダークモード"
```

**使う場面**:
- UI/UXの設計を相談された時
- デザインのアイデアが欲しい時
- コンポーネント設計の提案が必要な時

## Gemini CLI Tips

| 機能 | 使い方 | 説明 |
|------|-------|------|
| ファイル含める | `@./file.txt` | catより効率的 |
| ディレクトリ含める | `@./src/` | 複数ファイル一括 |
| ウェブ検索 | `@search クエリ` | 最新情報取得 |
| サンドボックス | `-s` | 安全な実行環境 |
| JSON出力 | `-o json` | 構造化データ |
| 自動承認 | `--yolo` | 確認スキップ（注意） |

## ワークフロー例

### 例1: 最新技術情報の確認

```
ユーザー: 「最新のNext.js 15の新機能は？」
私: 私の知識は古い可能性がある → Geminiに検索させる
→ gemini -m gemini-2.5-flash "@search Next.js 15 新機能 2025"
→ 結果を受け取り、ユーザーに回答
```

### 例2: 大きなログの分析

```
ユーザー: 「このログファイルを分析して」（500KB）
私: 私のコンテキストに収まらない → Geminiに任せる
→ gemini -m gemini-2.5-flash "@./large.log エラーパターンを特定して"
→ 結果を受け取り、具体的な修正を提案
```

### 例3: 本番デプロイ前のダブルチェック

```
私: コード実装完了
私: 重要な変更なので検証したい → Geminiにレビューさせる
→ git diff | gemini -m gemini-2.5-pro "レビューして"
→ 指摘があれば修正してからデプロイ
```

## 自発的判断のポイント

**以下を検知したら、積極的にGeminiを使う**:

1. **ファイルサイズ**: `wc -c` で確認、100KB超えたらGemini
2. **「最新の」「現在の」**: 知識が古い可能性 → `/gemini-search`
3. **画像/PDF**: 内容読み取り → `/gemini-ocr`
4. **UI/UX相談**: デザイン系 → `/gemini-design`
5. **重要な変更**: 本番前 → `/gemini-review`

## パイプ（stdin）対応

`gemini-call.sh` は `--stdin` オプションでパイプ入力に対応:

```bash
# ログをパイプで渡して分析
cat production.log | gemini-call.sh --stdin --task analyze "エラーを特定して"

# git diff をレビュー
git diff | gemini-call.sh --stdin --task review "この変更をレビューして"

# 複数ファイルを結合して渡す
cat src/*.ts | gemini-call.sh --stdin "このコードの問題点は？"
```

## gemini-call.sh オプション

| オプション | 説明 |
|-----------|------|
| `-m, --model MODEL` | モデル指定 |
| `--task TASK` | タスクタイプ（ocr/design/review/analyze/quick） |
| `-f, --file FILE` | ファイルを含める（複数可） |
| `--stdin` | 標準入力から読み込み |
| `-t, --timeout SECS` | タイムアウト秒（デフォルト: 900秒=15分） |
| `-j, --json` | JSON出力 |
| `-y, --yolo` | 自動承認 |

## CLAUDE.md テンプレート

プロジェクト単位でGemini連携をカスタマイズするには:

```bash
# テンプレートをプロジェクトにコピー
cp templates/CLAUDE.gemini.md your-project/CLAUDE.md
```

テンプレートには以下が含まれます:
- コマンド定義（gemini, gemini-review, gemini-search等）
- 自動判断ルール
- タスク別モデル選択
- 使用例

詳細: [templates/CLAUDE.gemini.md](templates/CLAUDE.gemini.md)

## scripts/

- `gemini-call.sh` - Gemini CLI呼び出しラッパー

## templates/

- [CLAUDE.gemini.md](templates/CLAUDE.gemini.md) - プロジェクト用設定テンプレート

## references/

- [ocr-workflow.md](references/ocr-workflow.md) - OCR詳細
- [analyze-workflow.md](references/analyze-workflow.md) - 大規模分析詳細
- [review-workflow.md](references/review-workflow.md) - レビュー詳細
- [design-workflow.md](references/design-workflow.md) - UI設計詳細
