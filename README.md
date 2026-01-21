# Claude Skills

Claude Code用のカスタムスキル集。

## スキル一覧

| スキル | 説明 | 状態 |
|--------|------|------|
| [gemini-skill](./gemini-skill/) | Gemini CLI連携（大規模分析、OCR、検索、UI設計、レビュー） | ✅ 完成 |

## インストール方法

```bash
# .skillファイルをスキルディレクトリにコピー
cp gemini-skill.skill ~/.claude/skills/

# 解凍
cd ~/.claude/skills
python3 -c "import zipfile; zipfile.ZipFile('gemini-skill.skill', 'r').extractall('.')"
```

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
