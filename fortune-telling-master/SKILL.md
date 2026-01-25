---
name: fortune-telling-master
description: >
  Professional-grade Eastern fortune-telling system with AUTOMATED CALCULATION and REAL-TIME INTERPRETATION. Combines Four Pillars (四柱推命) and Name Analysis (姓名判断). Features: (1) Auto-calculate 干支/通変星/十二運 with astronomical precision, (2) Generate 100-year fortune tables, (3) Tengel.net integration for real-time professional interpretations (authorized), (4) Multi-perspective analysis with intentional contradictions, (5) Professional interpretation database matching commercial software. Use for birth chart analysis, name readings, integrated destiny readings, name recommendations, compatibility analysis, and detailed life forecasts. When uncertain, automatically fetches expert interpretations from tengel.net. Supports Kumazaki and modern stroke methods.
---

# Fortune-Telling Master: Professional Divination System

**🎉 MAJOR UPDATE - Research-Based Improvements!**

**New Features (Based on Deep Research):**
- ✅ **Individual Highlight Period Calculation**: No longer fixed at 34-55 years
- ✅ **Complete Undertension Table**: All 10 heavenly stems with detailed monthly/hourly data
- ✅ **Comprehensive Compatibility System**: 三合・六合・相冲・相刑・相害 fully implemented
- ✅ **Enhanced Special Stars Database**: Multiple judgment methods, conversion strategies
- ✅ **Theoretical Foundations**: Research-backed explanations for all calculations

**Critical Discoveries from Research:**
1. **34-55 Age Highlight**: Not a universal rule in classical texts - it's a modern interpretation based on:
   - 日柱 age domain (33-48 years)
   - 3rd-5th大運 cycles (typically 30s-50s)
   - Individual variation based on命式 and 大運
   
2. **"Undertension" Term**: Not traditional四柱推命 terminology - corresponds to weak十二運 stages (衰・病・死・墓・絶)

3. **White Tiger (白虎)**: Has BOTH positive and negative aspects - can be converted to success through "活人業" (life-saving professions)

**🚀 REVOLUTIONARY FEATURES:**
- **Automated Four Pillars Calculation**: Python scripts for precise 干支 calculation
- **100-Year Fortune Table Generator**: Automatic generation of detailed life-span analysis
- **Tengel.net Integration** ⭐: Real-time interpretation from professional site (authorized)
  - Fetch interpretations when uncertain
  - Parse and analyze professional-grade text
  - Auto-update database with new patterns
- **Professional-Grade Interpretations**: Rich database matching commercial software output
- **Comprehensive Analysis**: Multiple perspectives with intentional contradictions (as per traditional practice)

**⚠️ CRITICAL PRINCIPLE: INDIVIDUAL-FOCUSED APPROACH**
This skill provides references and examples to teach you methodology and professional standards.
**DO NOT copy reference text.** Generate original interpretations based on each person's unique chart.
Every chart configuration is different and deserves a personalized reading.

Perform professional Eastern divination analyses combining Four Pillars of Destiny (四柱推命/Shichūsuimei) and Name Analysis (姓名判断/Seimei Handan) at a level matching commercial fortune-telling software.

---

## 🚀 クイックスタート（統合スクリプト使用）

### 基本的な使用方法

**推奨**: 統合スクリプト `fortune_teller.py` を使用（引数で任意の生年月日を指定可能）

```bash
cd /mnt/skills/user/fortune-telling-master/scripts

# 基本実行（JSON出力）
python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male

# 別の生年月日で実行
python3 fortune_teller.py -d 1990-07-15 -t 08:30 -g female -n "佐藤花子"

# 相性判定も含める
python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male \
  --partner-date 1985-07-15 --partner-time 08:30 --partner-gender female

# 詳細なヘルプ
python3 fortune_teller.py --help
```

**出力オプション**:
- `--output json` : JSON形式（デフォルト、プログラムで処理可能）
- `--output text` : テキスト形式（人間が読みやすい）
- `--output docx` : Word文書作成の指示を表示
- `--output all` : すべての形式

### 📊 Word文書作成（必須手順）

**🔴 重要**: Word文書作成時は**必ずdocxスキル**を使用してください。
**Pythonのpython-docxライブラリは使わない**（表現や段落がおかしくなる）

#### ステップ1: 計算実行

```bash
# JSON形式で計算結果を保存
python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male \
  --output json --output-file /mnt/user-data/outputs/results.json
```

#### ステップ2: docxスキルとレポート構造を読む

```bash
# 1. docxスキルを読み込む
cat /mnt/skills/public/docx/SKILL.md

# 2. docx-js.mdを完全に読む（範囲指定なし！）
cat /mnt/skills/public/docx/docx-js.md

# 3. 標準レポート構造を確認
cat /mnt/skills/user/fortune-telling-master/references/standard_report_structure.md
```

#### ステップ3: JavaScriptでWord文書を作成

docx-js.mdの指示に従って、Document, Paragraph, TextRun コンポーネントを使用。
詳細は `references/standard_report_structure.md` を参照。

#### ステップ4: 文書を保存

```javascript
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/mnt/user-data/outputs/鑑定書.docx', buffer);
  console.log('Document created successfully!');
});
```

### 🎯 個別スクリプトの使用（上級者向け）

特定の機能だけを使いたい場合:

```python
# 四柱計算のみ
from shichusui_calculator import calculate_pillars
chart = calculate_pillars((1982, 2, 25), (12, 0))

# ハイライト期間のみ
from highlight_period_calculator import calculate_highlight_period
period = calculate_highlight_period(birth_date, birth_time, gender, chart, dayun_list, yongshen)

# アンダーテンションのみ
from undertension_calculator import get_undertension_period
undertension = get_undertension_period('己')

# 相性判定のみ
from compatibility_calculator import judge_compatibility
result = judge_compatibility(person1_branches, person2_branches)
```

---

## Core Capabilities

1. **Four Pillars Analysis** - Birth chart interpretation with 10 Heavenly Stems, 12 Earthly Branches
2. **Name Analysis** - Five-grid calculation using traditional (Kumazaki) or modern stroke methods
3. **Integrated Reading** - Correlate innate destiny (birth) with acquired destiny (name)
4. **Name Optimization** - Recommend names that complement birth charts
5. **Compatibility Analysis** - Assess relationships between two individuals

## Quick Start Workflow

### Option 1: Integrated Reading (Recommended)

```
1. Collect user information:
   - Name (family + given, specify kanji)
   - Birth date and time
   - Birth location
   - Gender (for determining Taiu direction)
   - Method preference (Kumazaki/Modern for name analysis)

2. Calculate Four Pillars → AUTOMATED SCRIPTS AVAILABLE!
   - Run scripts/shichusui_calculator.py for automatic calculation
   - Build four pillars (year/month/day/hour)
   - Determine通変星 and 十二運 automatically
   - Determine day stem strength (身強/身弱)
   - Identify favorable elements (喜神/忌神)
   - Manual verification: See references/shichusui_guide.md

3. Generate 100-Year Fortune Table → AUTOMATED!
   - Run scripts/unsei_table_generator.py
   - Automatically generates fortune table up to age 100
   - Includes: 大運, 年運, 通変星, 十二運, special notes
   - Format ready for Word document insertion

4. Calculate Five Grids → See references/meihan_guide.md
   - Count strokes per character
   - Calculate: 天格, 人格, 地格, 外格, 総格
   - Analyze yin-yang pattern and three-talents configuration

5. Analyze the unique chart configuration:
   **⚠️ CRITICAL: Avoid copying reference examples. Generate original interpretations.**
   
   a) **Identify the individual's unique pattern:**
      - What is the specific combination of 通変星 in this chart?
      - Which 十二運 appear at key positions?
      - What are the elemental strengths/weaknesses?
      - Are there special configurations (三合, 方合, 冲, 刑, etc.)?
   
   b) **Build interpretation from fundamentals:**
      - Start from the MEANING of each 通変星 (not example text)
      - Consider the INTERACTION between multiple stars
      - Analyze the BALANCE of five elements
      - Assess 身強/身弱 and its implications
   
   c) **Reference usage (for structure ONLY):**
      - references/detailed_interpretations.md → Learn the APPROACH to interpretation
      - references/tengel_real_data_analysis.md → Understand STYLE and TONE
      - references/multifaceted_analysis_guide.md → Learn how to write with nuance
      - **DO NOT copy phrases or expressions from references**
   
   d) **When uncertain about rare patterns:**
      - Use scripts/tengel_connector.py to fetch from tengel.net
      - Parse response with scripts/tengel_parser.py
      - Analyze with scripts/tengel_analyzer.py
      - Extract the REASONING, not just the text
   
   e) **Synthesize original interpretation:**
      - Write personality analysis based on THIS person's star combination
      - Derive職業適性 from the specific strengths shown
      - Infer 健康運 from elemental imbalances unique to this chart
      - Create 財運 analysis from actual configuration
      - Include contradictions naturally (身強 vs 身弱 indicators)
      - Use fresh expressions that fit this individual

6. Integrate findings (birth chart + name):
   - Compare favorable elements from birth chart with five-element distribution in name
   - Identify actual synergies and conflicts in THIS case
   - Explain how the name complements or challenges the birth destiny
   - Provide specific examples from the configuration
   - Avoid generic statements

7. Generate professional report:
   **⚠️ Write original content. References show structure, not text to copy.**
   
   - Review references/output_template.md for STRUCTURE only
   - Create sections based on actual findings:
     * 基本情報 (actual calculation results)
     * 命式分析 (THIS person's unique pattern)
     * 性格・才能 (derived from actual 通変星 combination)
     * 運勢傾向 (based on specific 大運 transitions)
     * 適職・キャリア (inferred from configuration)
     * 対人関係・恋愛 (based on actual star positions)
     * 健康運 (from elemental analysis)
     * 開運アドバイス (specific to this chart)
   - Include 100-year fortune table (auto-generated data)
   - Format as Word document with professional layout
   - Save to `/mnt/user-data/outputs/fortune_reading.docx`
   
   **Quality check before finalizing:**
   - Does this reading sound unique to this person?
   - Are interpretations derived from actual calculations?
   - Have I avoided copying reference text?
   - Is the advice actionable and specific?
```

### Option 2: Four Pillars Only

Use when user has only birth information. See `references/shichusui_guide.md` for complete procedures.

### Option 3: Name Analysis Only

Use when user has only name information. See `references/meihan_guide.md` for complete procedures.

## Key Decision Points

### When to Search References (for learning, not copying)

**⚠️ IMPORTANT: References are for understanding approach, not for copying text.**

- **Theory questions** → `references/shichusui_theory.md` or `references/meihan_theory.md`
  - Learn the fundamental principles
  - Understand the meaning of each element
  
- **Data lookups** → `references/data_tables.md`
  - Stem/branch attributes, stroke meanings, etc.
  - Factual information only
  
- **Interpretation approach** → `references/detailed_interpretations.md`
  - Learn HOW to think about each 通変星
  - Understand the logic behind interpretations
  - **DO NOT copy the example text**
  
- **Multi-perspective analysis** → `references/multifaceted_analysis_guide.md`
  - Learn how to write with intentional contradictions
  - Understand professional fortune-telling style
  - See how to balance multiple viewpoints
  
- **Professional tone and structure** → `references/tengel_real_data_analysis.md`
  - Study the overall structure
  - Learn the narrative flow
  - Observe how sections connect
  - **DO NOT reuse specific phrases**
  
- **Examples** → `references/examples.md`
  - See complete workflow in action
  - Understand end-to-end process
  - **These are specific to other people, not templates**
  
- **Step-by-step procedures** → `references/shichusui_guide.md` or `references/meihan_guide.md`
  - Follow calculation methods exactly
  - Verify your calculations

**Key Principle:**
References teach you "what to look for" and "how to think," not "what to write."
Generate original interpretations based on actual calculations for each individual.

### When to Use Tengel.net Integration

**Use tengel_connector.py when:**
- Uncertain about specific interpretation patterns
- Need professional-grade text for rare configurations
- Want to verify calculation accuracy (1-second precision)
- Encountering unusual 通変星/十二運 combinations

**Process:**
1. Call `tengel_connector.fetch_interpretation(year, month, day, hour, minute, gender)`
2. Parse result with `tengel_parser.TengelDataParser(raw_text).parse()`
3. Analyze patterns with `tengel_analyzer.TengelAnalyzer()`
4. Apply learned patterns to current reading

**Note**: Site operator authorization obtained. Use respectfully and cite source when using interpretations.

- **Birth time unknown** → Use noon (12:00) and note reduced accuracy for hour pillar
- **Birth location unknown** → Use solar time without location adjustment, note limitation
- **Kanji unclear** → Confirm with user, as stroke count varies significantly

### Method Selection for Name Analysis

**Kumazaki Method (Traditional)**:
- Based on Kangxi Dictionary
- Special radical counting rules (氵=4 not 3, etc.)
- More authoritative in traditional circles

**Modern Method**:
- Based on actual written strokes
- Simpler, matches contemporary usage
- Ask user preference if not specified

## Output Format

Generate structured Word document with:
1. Basic information summary
2. Four Pillars analysis (if applicable)
3. Name analysis (if applicable)
4. Integrated diagnosis (if both)
5. Recommendations and advice
6. Name change suggestions (if needed)

Save to `/mnt/user-data/outputs/fortune_reading.docx`

Use formatting: headings, tables for charts/grids, bullet points for interpretations.

## Important Notes

**Ethical Guidelines**:
- Present readings as guidance, not absolute destiny
- Avoid alarming language for unfavorable results
- Emphasize personal agency and growth opportunities
- For medical/legal issues, recommend consulting professionals

**Cultural Sensitivity**:
- Explain Eastern philosophy context when needed
- Respect user's belief level
- Provide rational interpretation alongside traditional meaning

**Quality Standards**:
- Verify calculations twice for accuracy
- Cite specific data sources when interpreting
- Maintain professional, supportive tone
- Provide actionable advice, not just descriptions
- **Ensure each reading is unique to the individual:**
  - Interpretations must derive from actual calculations
  - Avoid generic or template-like expressions
  - Each chart combination produces different insights
  - Reference examples teach approach, not content
- **Check for originality:**
  - Have I written this based on the person's chart?
  - Would this reading apply to someone else? (If yes, revise)
  - Are my expressions fresh and specific?

## Bundled Resources

### Scripts (Automated Calculation)

- `fortune_teller.py` - **統合メインスクリプト（推奨）** ⭐NEW!
  - コマンドライン引数で任意の生年月日を指定可能
  - 全ての計算を一度に実行（四柱、大運、神殺、ハイライト期間、アンダーテンション、相性判定）
  - 複数の出力形式（JSON, テキスト, Word文書作成指示）
  - 使用例: `python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male`
  - ヘルプ: `python3 fortune_teller.py --help`

- `shichusui_calculator.py` - **Core calculation engine**
  - Automatically calculates 四柱 (year/month/day/hour pillars)
  - Computes 通変星 (10 transforming stars)
  - Computes 十二運 (12 life stages)
  - Calculates 大運 (10-year fortune cycles)
  - Usage: `python3 scripts/shichusui_calculator.py`

- `unsei_table_generator.py` - **100-year fortune table generator**
  - Generates complete fortune analysis from age 1 to 100
  - Includes 年運 (yearly fortune), 大運 (decade fortune)
  - Automatic special event detection
  - Ready for Word document insertion
  - Usage: Import and call `generate_100year_table()`

- `special_stars_calculator.py` - **神殺判定システム** ⭐UPDATED!
  - Automatic detection of special stars (吉神・凶神)
  - 天乙貴人, 白虎, 羊刃, 血刃, 孤辰・寡宿, 駅馬, etc.
  - Multiple judgment methods supported (三合局起点, 日柱干支, etc.)
  - Includes吉凶相互作用 analysis
  - Usage: `from special_stars_calculator import calc_special_stars`

- `highlight_period_calculator.py` - **人生ハイライト期間判定** ⭐NEW!
  - Individual-based highlight period calculation (not fixed 34-55)
  - Based on: 日柱年齢域 + 大運分析 + 身強身弱
  - Scoring algorithm with multiple factors
  - Customized period for each person
  - Usage: `from highlight_period_calculator import calculate_highlight_period`

- `undertension_calculator.py` - **アンダーテンション期間計算** ⭐NEW!
  - Complete table for all 10 heavenly stems
  - Strong undertension (死・墓・絶) and weak undertension (衰・病)
  - Monthly and hourly energy level calculation
  - Based on 十二長生 theory
  - Usage: `from undertension_calculator import get_undertension_period`

- `compatibility_calculator.py` - **相性判定システム** ⭐NEW!
  - Comprehensive compatibility analysis
  - 三合, 半会, 方合, 六合 (positive combinations)
  - 相冲, 相刑, 相害 (negative combinations)
  - Scoring system with recommendations
  - Usage: `from compatibility_calculator import judge_compatibility`

- `tengel_connector.py` - **天使ネット連携システム**
  - Real-time interpretation fetch from tengel.net (authorized use)
  - POST requests with birth data, returns professional interpretations
  - Usage: When uncertain about interpretation, call this to get expert analysis
  - Site: https://www.dumbonet.com/tengel/

- `tengel_parser.py` - **天使ネット解釈パーサー**
  - Parses and structures tengel.net interpretations
  - Extracts sections: career, personality, health, warnings, etc.
  - Generates structured Markdown from raw text
  - Usage: Process fetched interpretations into database format

- `tengel_analyzer.py` - **解釈分析ツール**
  - Analyzes interpretation text for keywords, contradictions, tone
  - Compares new interpretations with existing database
  - Identifies unique patterns and expressions
  - Usage: Improve database by learning from new interpretations

### References (Learning Resources - Not Templates)

- `shichusui_theory.md` - Complete Four Pillars theory and philosophy
- `shichusui_guide.md` - Step-by-step manual calculation procedures
- `detailed_interpretations.md` - **Interpretation approach guide**
  - Teaches how to analyze each 通変星
  - Explains career aptitudes, health considerations, relationship patterns
  - Shows professional reasoning process
  - **Use to learn the approach, not to copy text**
- `tengel_real_data_analysis.md` - **Professional writing style reference**
  - Structured breakdown of interpretation patterns
  - Examples of multi-perspective descriptions with contradictions
  - Professional tone and narrative flow
  - **Study the structure and style, write original content**
- `meihan_theory.md` - Complete Name Analysis theory
- `meihan_guide.md` - Step-by-step stroke counting and grid calculation
- `data_tables.md` - All lookup tables (stems, branches, stroke meanings, three-talents matrix)
- `examples.md` - Real case studies demonstrating complete workflow
  - **These are specific examples, not templates to reuse**
- `multifaceted_analysis_guide.md` - Guide to writing with intentional contradictions
  - **Learn the technique, apply to each unique case**
- `output_template.md` - Sample report structure (structure only, not content)
- `special_stars.md` - **Complete special stars database** ⭐UPDATED!
  - Detailed judgment methods for all 吉神 and 凶神
  - Multiple流派 supported (三合局, 日柱干支, etc.)
  - Includes interaction analysis and conversion methods
  - White Tiger (白虎), Blood Blade (血刃), etc. with full explanations
- `standard_report_structure.md` - **Standard Word document report structure** ⭐NEW!
  - **Mandatory sections and recommended order**
  - **Prevents inconsistent report formats**
  - **docx skill usage instructions**
  - Quality checklist for report creation
  - JavaScript implementation examples

**Usage Philosophy:**
Load these to understand the methodology, theory, and professional standards.
Then generate original interpretations based on each individual's unique calculations.
References are your teachers, not your scripts.
