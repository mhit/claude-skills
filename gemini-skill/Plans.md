# Gemini Skill 改良計画

## 現状

実装済み:
- SKILL.md にコマンド使用法を定義
- gemini-call.sh でタスク別モデル自動選択
- @ファイル含める機能

## 改良概要

| 改良点 | 現状 | 改良後 |
|--------|------|--------|
| 環境変数 | 暗黙的使用 | 明示的ドキュメント + GEMINI_DEFAULT_MODEL |
| stdin対応 | なし | --stdin オプション追加 |
| CLAUDE.mdテンプレート | なし | プロジェクト用設定例を提供 |
| MCP化 | なし | 将来拡張として文書化 |

---

## Phase 1: 環境変数対応 `cc:done`

**目的**: 設定の外出しと明示化

- [x] gemini-call.sh に GEMINI_DEFAULT_MODEL 対応追加
- [x] SKILL.md に環境変数セクション追加

### 環境変数仕様

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `GEMINI_API_KEY` | Yes | Gemini APIキー |
| `GEMINI_DEFAULT_MODEL` | No | デフォルトモデル（未指定時: gemini-2.5-flash） |
| `GEMINI_TIMEOUT` | No | タイムアウト秒（未指定時: 900 = 15分） |

---

## Phase 2: stdin対応 `cc:done`

**目的**: パイプで大量テキストを渡せるようにする

- [x] gemini-call.sh に --stdin オプション追加
- [x] SKILL.md にパイプ使用例追加

### 実装仕様

```bash
# パイプで渡す
cat large-log.txt | gemini-call.sh --stdin "このログを分析して"

# ファイル内容とプロンプトを組み合わせ
git diff | gemini-call.sh --stdin --task review "この変更をレビューして"
```

---

## Phase 3: CLAUDE.mdテンプレート `cc:done`

**目的**: プロジェクト単位でGemini連携をカスタマイズ

- [x] templates/CLAUDE.gemini.md 作成
- [x] SKILL.md にテンプレート使用方法追加

### テンプレート内容

```markdown
# Gemini連携設定

## コマンド定義
- `gemini "質問"` → `gemini-call.sh --task quick "質問"`
- `gemini-review <file>` → `cat <file> | gemini-call.sh --stdin --task review "レビューして"`
- `gemini-search "キーワード"` → `gemini -m gemini-2.5-flash "@search キーワード"`

## 自動判断ルール
- ファイルサイズ > 100KB → Gemini使用
- 「最新の」を含む質問 → Gemini検索使用
- PDF/画像ファイル → Gemini OCR使用
```

---

## Phase 4: ドキュメント整備 `cc:done`

- [x] SKILL.md を全体的に更新（環境変数、stdin、テンプレート）
- [ ] references/ 配下の詳細ドキュメント更新（スキップ - 既存で十分）

---

## Phase 5: MCP化（将来拡張） `cc:SKIP`

**目的**: CLI操作を隠蔽し、ネイティブ統合

**状態**: 設計検討中（高度な拡張として将来対応）

### 概念設計

```
Claude Code → MCP Server → Gemini API
                ↓
           gemini-mcp-server
           - tools: search, ocr, analyze, review, design
           - resources: model-list, usage-stats
```

---

## 更新履歴

- 2026-01-22: Phase 1-4 実装完了
- 2026-01-22: 改良計画作成
