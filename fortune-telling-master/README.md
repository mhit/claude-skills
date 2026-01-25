# Fortune-Telling Master - Professional Divination System

## 🎉 Major Update - Research-Based Improvements

このバージョンは、Deep Researchによる包括的な調査に基づいて大幅に改善されています。

### 主要な改善点

#### 1. 個人別ハイライト期間計算
- ❌ **旧**: 34-55歳に固定
- ✅ **新**: 個人の命式と大運に基づいて動的に計算
- スクリプト: `scripts/highlight_period_calculator.py`

#### 2. 完全なアンダーテンション期間テーブル
- 全10干（甲・乙・丙・丁・戊・己・庚・辛・壬・癸）の詳細データ
- 強アンダー（死・墓・絶）と弱アンダー（衰・病）の区別
- 月別・時間帯別のエネルギーレベル
- スクリプト: `scripts/undertension_calculator.py`

#### 3. 包括的な相性判定システム
- 三合、半会、方合、六合（吉）
- 相冲、相刑、相害（凶）
- スコアリングシステムと推奨事項
- スクリプト: `scripts/compatibility_calculator.py`

#### 4. 強化された神殺データベース
- 複数の判定方法をサポート（流派の違いに対応）
- 吉凶の相互作用分析
- 白虎・血刃の吉転方法（活人業への転換）
- スクリプト: `scripts/special_stars_calculator.py`（更新）

### リサーチに基づく重要な発見

#### 1. 34-55歳ハイライト期間の真実
古典的な四柱推命の文献には明確な記載がなく、現代的解釈です：
- **日柱の年齢域**（33-48歳）が中核
- **大運の3〜5回目**（約30代〜50代）が社会的成功期
- **個人差**が大きい（大運開始年齢、身強身弱、用神）

#### 2. アンダーテンション＝十二長生の弱運期
「アンダーテンション」は伝統的な用語ではなく、十二運の弱い段階を指します：
- 衰（やや弱）
- 病（やや弱）
- 死（強く弱）
- 墓（強く弱）
- 絶（強く弱）

#### 3. 白虎の両面性
凶神としてだけでなく、吉神としても機能：
- **凶作用**: 怪我、事故、病気
- **吉作用**: 強い推進力、決断力（活人業で吉転）
- **活人業**: 医師、警察、裁判官、宗教家など

## 使用方法

### 基本的な占い実行

1. **CRITICAL_IMPROVEMENTS.mdを必ず最初に読む**
   ```bash
   cat CRITICAL_IMPROVEMENTS.md
   ```

2. **スキルを読み込む**
   ```bash
   cat SKILL.md
   ```

3. **計算スクリプトを使用**
   ```python
   # 四柱計算
   from scripts.shichusui_calculator import calculate_pillars
   
   # ハイライト期間
   from scripts.highlight_period_calculator import calculate_highlight_period
   
   # アンダーテンション
   from scripts.undertension_calculator import get_undertension_period
   
   # 相性判定
   from scripts.compatibility_calculator import judge_compatibility
   
   # 神殺判定
   from scripts.special_stars_calculator import calc_special_stars
   ```

### ファイル構成

```
fortune-telling-master/
├── SKILL.md                          # メインスキルファイル
├── CRITICAL_IMPROVEMENTS.md          # 必読の改善ポイント
├── scripts/                          # Python計算スクリプト
│   ├── shichusui_calculator.py
│   ├── unsei_table_generator.py
│   ├── special_stars_calculator.py   # ⭐更新
│   ├── highlight_period_calculator.py # ⭐新規
│   ├── undertension_calculator.py    # ⭐新規
│   ├── compatibility_calculator.py   # ⭐新規
│   ├── tengel_connector.py
│   ├── tengel_parser.py
│   └── tengel_analyzer.py
├── references/                       # 参考資料（コピペ禁止）
│   ├── shichusui_theory.md
│   ├── shichusui_guide.md
│   ├── meihan_theory.md
│   ├── meihan_guide.md
│   ├── data_tables.md
│   ├── detailed_interpretations.md
│   ├── tengel_real_data_analysis.md
│   ├── multifaceted_analysis_guide.md
│   ├── output_template.md
│   ├── examples.md
│   └── special_stars.md              # ⭐更新
└── research/                         # Deep Researchソース
    ├── research_report_1.txt
    ├── research_report_2.txt
    └── research_report_3.txt
```

## 品質保証

### 前回の反省点（必読）

**CRITICAL_IMPROVEMENTS.md**に詳細が記載されています：

1. **参考資料のコピペ禁止**
   - 参考資料は「考え方」を学ぶためのもの
   - 文章は完全にオリジナルで書く

2. **個人に合わせた解釈**
   - 一般論ではなく、この人固有の命式に基づく
   - 具体的な年齢、時期、組み合わせを明示

3. **深い分析**
   - 通変星の意味を並べるだけではダメ
   - なぜその組み合わせでその結果になるのか説明
   - 矛盾を条件付きで説明

### 品質チェックリスト

各セクションを書いた後、以下を確認：

- [ ] この人固有の通変星の組み合わせに言及しているか？
- [ ] 「〜を持つ人は」という一般論になっていないか？
- [ ] 参考資料の表現をコピペしていないか？
- [ ] 矛盾がある場合、その条件を説明しているか？
- [ ] 五行のバランスから具体的に導いているか？
- [ ] 具体的な年齢・時期を示しているか？

## 理論的根拠

全ての計算と解釈は、以下の文献とリサーチに基づいています：

- 140以上の専門文献を調査
- 古典四柱推命の理論
- 現代の実践的解釈
- プロの鑑定師の手法
- 天使ネット（tengel.net）の実データ分析

詳細は `research/` ディレクトリのファイルを参照してください。

## ライセンスと倫理

- 参考資料は学習用であり、コピペ禁止
- 天使ネット（tengel.net）の使用は運営者の許可を得ています
- 占い結果は「傾向」であり、絶対的な運命ではありません
- 医療・法律問題は専門家への相談を推奨

## サポート

質問や改善提案がある場合は、使用者に直接お問い合わせください。

---

**重要**: 占いを実行する前に、必ず `CRITICAL_IMPROVEMENTS.md` を読んでください。
