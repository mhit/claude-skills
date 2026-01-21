# Claude Skills

Claude Code用のカスタムスキル集。

## インストール

### 方法1: プラグインとして（推奨）

```bash
# マーケットプレイスとして登録
claude plugin marketplace add mhit/claude-skills

# スキルをインストール
claude plugin install gemini-skill@claude-skills
```

### 方法2: 手動インストール

```bash
# .skillファイルをダウンロードしてスキルディレクトリにコピー
cp gemini-skill.skill ~/.claude/skills/

# 解凍
cd ~/.claude/skills
python3 -c "import zipfile; zipfile.ZipFile('gemini-skill.skill', 'r').extractall('.')"
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

## スキル構造

各スキルは以下の構造に従う：

```
skill-name/
├── SKILL.md           # メイン定義（必須）
├── scripts/           # 実行スクリプト（オプション）
├── references/        # 詳細ドキュメント（オプション）
└── assets/            # テンプレート等（オプション）
```

## 今後の予定

- [ ] 追加スキルの作成

## ライセンス

MIT
