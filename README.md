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
claude plugin install meeting-minutes-analyzer@claude-skills
claude plugin install spi3-analyzer@claude-skills
claude plugin install fortune-telling-master@claude-skills
claude plugin install syakaihoken-roumushi@claude-skills
```

### 方法2: 手動インストール

```bash
# .skillファイルをダウンロードしてスキルディレクトリにコピー
cp *.skill ~/.claude/skills/

# 解凍
cd ~/.claude/skills
for f in *.skill; do
  python3 -c "import zipfile; zipfile.ZipFile('$f', 'r').extractall('.')"
done
```

## スキル一覧

| スキル | 説明 |
|--------|------|
| [gemini-skill](#gemini-skill) | Gemini CLI連携（大規模ファイル分析、検索、OCR） |
| [kintone-skill](#kintone-skill) | KINTONE REST API連携（CRUD、検索、添付ファイル） |
| [meeting-minutes-analyzer](#meeting-minutes-analyzer) | 会議音声から高度な議事録を作成 |
| [spi3-analyzer](#spi3-analyzer) | SPI3-G採用適性検査の分析レポート作成 |
| [fortune-telling-master](#fortune-telling-master) | 四柱推命・姓名判断の専門鑑定 |
| [syakaihoken-roumushi](#syakaihoken-roumushi) | 就業規則・労働規程の作成支援 |

---

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

---

### kintone-skill

KINTONE REST API連携スキル。レコードのCRUD、検索、スキーマキャッシュ、添付ファイル操作が可能。

**環境変数**:
```bash
export KINTONE_DOMAIN="xxx.cybozu.com"
export KINTONE_API_TOKEN="your-api-token"
```

| 機能 | 説明 |
|------|------|
| `/kintone apps` | アクセス可能なアプリ一覧 |
| `/kintone schema` | フィールド定義を表示 |
| `/kintone search` | レコードを検索（自然言語対応） |
| `/kintone add/update/delete` | レコード操作 |
| `/kintone file` | 添付ファイル操作 |

---

### meeting-minutes-analyzer

音声トランスクリプトから高度な会議議事録を作成するスキル。

**特徴**:
- タイムスタンプあり/なし、話者名あり/なしの複数形式に対応
- SWOT分析、意思決定ツリー、感情分析など8種類のフレームワーク
- 固有名詞の確認プロセス
- Word(.docx)形式で出力

**対応会議タイプ**:
- プロジェクト会議
- 戦略会議
- ブレインストーミング
- クライアント打ち合わせ
- 採用面接

---

### spi3-analyzer

SPI3-G（総合検査）の採用適性検査結果を分析し、包括的なレポートを作成。

**分析内容**:
- 能力検査（言語・非言語能力）
- 性格検査14項目
- 組織適応性（4つの風土タイプ）
- 「素直さ」の多角的評価
- ゼークトの組織論による分類
- 面接での確認事項（STAR法）

**出力**:
- 12セクションの詳細レポート
- 採用推奨度（5段階）
- 面接質問リスト

---

### fortune-telling-master

プロフェッショナルレベルの東洋占術システム。四柱推命と姓名判断を統合。

**機能**:
- 四柱（年・月・日・時）の自動計算
- 通変星・十二運の算出
- 100年運勢表の自動生成
- 相性判定（三合・六合・相冲など）
- 特殊星（吉神・凶神）の判定

**スクリプト**:
```bash
# 統合スクリプト
python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male

# 相性判定付き
python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male \
  --partner-date 1985-07-15 --partner-time 08:30 --partner-gender female
```

---

### syakaihoken-roumushi

中小企業向けの就業規則・各種規程の作成支援スキル。

**対応規程**:
- 就業規則（本則）
- 賃金規程
- 育児・介護休業規程
- パートタイマー就業規則
- テレワーク規程

**特徴**:
- 労働基準法などの法令に基づく
- 対話形式で企業の実態に合わせた規程作成
- 最新の法改正（2024年4月、2025年4月）に対応
- GMOサインでの電子契約締結サポート
- Word/Googleドキュメント形式で出力

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
