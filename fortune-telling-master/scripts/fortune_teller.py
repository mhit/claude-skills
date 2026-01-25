#!/usr/bin/env python3
"""
四柱推命・姓名判断 統合実行スクリプト

使用方法:
    python3 fortune_teller.py --birth-date 1982-02-25 --birth-time 12:00 --gender male --name "山田太郎"
    python3 fortune_teller.py -d 1985-07-15 -t 08:30 -g female -n "佐藤花子"

出力:
    - JSON形式で全ての計算結果
    - テキスト形式の詳細レポート（オプション）
    - Word文書形式のレポート（オプション、docxスキル使用）
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# サブスクリプトのインポート
try:
    from shichusui_calculator import calc_pillar, calc_taiun
    from special_stars_calculator import calc_special_stars
    from highlight_period_calculator import calculate_highlight_period
    from undertension_calculator import get_undertension_period, get_current_status
    from compatibility_calculator import judge_compatibility
    from unsei_table_generator import generate_100year_table
except ImportError as e:
    print(f"Error: サブスクリプトのインポートに失敗しました: {e}", file=sys.stderr)
    print("scripts/ ディレクトリから実行してください。", file=sys.stderr)
    sys.exit(1)


def parse_arguments():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='四柱推命・姓名判断の統合実行システム',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な実行
  python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male

  # 名前付き
  python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male -n "山田太郎"

  # Word文書出力（docxスキル使用）
  python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male -o docx

  # 相性判定（2人分の生年月日が必要）
  python3 fortune_teller.py -d 1982-02-25 -t 12:00 -g male --partner-date 1985-07-15 --partner-time 08:30 --partner-gender female
        """
    )
    
    # 必須引数
    parser.add_argument(
        '-d', '--birth-date',
        required=True,
        help='生年月日 (YYYY-MM-DD形式, 例: 1982-02-25)'
    )
    
    parser.add_argument(
        '-t', '--birth-time',
        required=True,
        help='生まれた時刻 (HH:MM形式, 例: 12:00)'
    )
    
    parser.add_argument(
        '-g', '--gender',
        required=True,
        choices=['male', 'female', 'm', 'f'],
        help='性別 (male/m または female/f)'
    )
    
    # オプション引数
    parser.add_argument(
        '-n', '--name',
        help='名前（姓名判断用、オプション）'
    )
    
    parser.add_argument(
        '-o', '--output',
        choices=['json', 'text', 'docx', 'all'],
        default='json',
        help='出力形式 (デフォルト: json)'
    )
    
    parser.add_argument(
        '--output-file',
        help='出力ファイル名（指定しない場合は標準出力）'
    )
    
    # 相性判定用（オプション）
    parser.add_argument(
        '--partner-date',
        help='相手の生年月日 (YYYY-MM-DD形式)'
    )
    
    parser.add_argument(
        '--partner-time',
        help='相手の生まれた時刻 (HH:MM形式)'
    )
    
    parser.add_argument(
        '--partner-gender',
        choices=['male', 'female', 'm', 'f'],
        help='相手の性別'
    )
    
    # その他
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細なログを表示'
    )
    
    parser.add_argument(
        '--include-100year-table',
        action='store_true',
        help='100年運勢表を含める（処理時間が増加します）'
    )
    
    return parser.parse_args()


def validate_date(date_str: str) -> tuple:
    """日付文字列を検証してタプルに変換"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return (dt.year, dt.month, dt.day)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")


def validate_time(time_str: str) -> tuple:
    """時刻文字列を検証してタプルに変換"""
    try:
        dt = datetime.strptime(time_str, '%H:%M')
        return (dt.hour, dt.minute)
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Use HH:MM.")


def normalize_gender(gender: str) -> str:
    """性別を正規化"""
    if gender.lower() in ['m', 'male']:
        return 'male'
    elif gender.lower() in ['f', 'female']:
        return 'female'
    else:
        raise ValueError(f"Invalid gender: {gender}")


def run_fortune_telling(args):
    """
    四柱推命を実行
    
    Returns:
        dict: 全ての計算結果を含む辞書
    """
    if args.verbose:
        print("=== 四柱推命・姓名判断 実行開始 ===", file=sys.stderr)
    
    # 入力の検証と変換
    birth_date = validate_date(args.birth_date)
    birth_time = validate_time(args.birth_time)
    gender = normalize_gender(args.gender)
    
    if args.verbose:
        print(f"生年月日: {birth_date}", file=sys.stderr)
        print(f"時刻: {birth_time}", file=sys.stderr)
        print(f"性別: {gender}", file=sys.stderr)
    
    results = {
        'input': {
            'birth_date': args.birth_date,
            'birth_time': args.birth_time,
            'gender': gender,
            'name': args.name
        },
        'calculations': {}
    }
    
    # 1. 四柱計算
    if args.verbose:
        print("\n[1/6] 四柱を計算中...", file=sys.stderr)
    
    year, month, day = birth_date
    hour, minute = birth_time
    chart = calc_pillar(year, month, day, hour)
    results['calculations']['chart'] = chart
    
    # 2. 大運計算
    if args.verbose:
        print("[2/6] 大運を計算中...", file=sys.stderr)
    
    month_kan = chart['month'][0]  # タプルの最初の要素
    month_shi = chart['month'][1]  # タプルの2番目の要素
    dayun_list = calc_taiun(year, month, day, gender, month_kan, month_shi)
    results['calculations']['dayun'] = dayun_list
    
    # 3. 神殺判定
    if args.verbose:
        print("[3/6] 神殺を判定中...", file=sys.stderr)
    
    try:
        nikkan = chart['day'][0]
        special_stars = calc_special_stars(chart, nikkan)
        results['calculations']['special_stars'] = special_stars
    except Exception as e:
        if args.verbose:
            print(f"  神殺判定でエラー: {e}", file=sys.stderr)
        results['calculations']['special_stars'] = {}
    
    # 4. ハイライト期間計算
    if args.verbose:
        print("[4/6] ハイライト期間を計算中...", file=sys.stderr)
    
    try:
        # 用神の簡易推定（実際はより詳細な分析が必要）
        nikkan = chart['day'][0]
        yongshen = []  # TODO: 実際の用神判定ロジックを実装
        
        highlight = calculate_highlight_period(
            birth_date, birth_time, gender, chart, dayun_list, yongshen
        )
        results['calculations']['highlight_period'] = {
            'start_age': highlight.start_age,
            'end_age': highlight.end_age,
            'peak_age': highlight.peak_age,
            'score': highlight.score,
            'reason': highlight.reason
        }
    except Exception as e:
        if args.verbose:
            print(f"  ハイライト期間計算でエラー: {e}", file=sys.stderr)
        # デフォルト値
        results['calculations']['highlight_period'] = {
            'start_age': 34,
            'end_age': 55,
            'peak_age': 44,
            'score': 0,
            'reason': '標準的な期間（個別計算エラー）'
        }
    
    # 5. アンダーテンション期間
    if args.verbose:
        print("[5/6] アンダーテンション期間を計算中...", file=sys.stderr)
    
    try:
        undertension = get_undertension_period(nikkan)
        results['calculations']['undertension'] = {
            'strong_months': undertension.strong_months,
            'weak_months': undertension.weak_months,
            'strong_hours': undertension.strong_hours,
            'reason': undertension.reason
        }
        
        # 現在の状態もチェック
        now = datetime.now()
        current_status = get_current_status(nikkan, now.month, now.hour)
        results['calculations']['current_undertension_status'] = current_status
    except Exception as e:
        if args.verbose:
            print(f"  アンダーテンション計算でエラー: {e}", file=sys.stderr)
        results['calculations']['undertension'] = {}
        results['calculations']['current_undertension_status'] = {}
    
    # 6. 100年運勢表（オプション）
    if args.include_100year_table:
        if args.verbose:
            print("[6/6] 100年運勢表を生成中（時間がかかります）...", file=sys.stderr)
        
        fortune_table = generate_100year_table(birth_date, gender, chart, dayun_list)
        results['calculations']['fortune_table'] = fortune_table
    
    # 7. 相性判定（オプション）
    if args.partner_date and args.partner_time and args.partner_gender:
        if args.verbose:
            print("\n[追加] 相性判定を実行中...", file=sys.stderr)
        
        partner_date = validate_date(args.partner_date)
        partner_time = validate_time(args.partner_time)
        partner_gender = normalize_gender(args.partner_gender)
        
        p_year, p_month, p_day = partner_date
        p_hour, p_minute = partner_time
        partner_chart = calc_pillar(p_year, p_month, p_day, p_hour)
        
        # 地支のリストを抽出
        person1_branches = [chart['year'][1], chart['month'][1], chart['day'][1], chart['hour'][1]]
        person2_branches = [partner_chart['year'][1], partner_chart['month'][1], 
                          partner_chart['day'][1], partner_chart['hour'][1]]
        
        compatibility = judge_compatibility(person1_branches, person2_branches)
        results['calculations']['compatibility'] = {
            'score': compatibility.score,
            'type': compatibility.type,
            'description': compatibility.description,
            'recommendations': compatibility.recommendations
        }
    
    if args.verbose:
        print("\n=== 計算完了 ===\n", file=sys.stderr)
    
    return results


def output_json(results, output_file=None):
    """JSON形式で出力"""
    json_str = json.dumps(results, ensure_ascii=False, indent=2)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"JSON出力: {output_file}", file=sys.stderr)
    else:
        print(json_str)


def output_text(results, output_file=None):
    """テキスト形式で出力"""
    text = generate_text_report(results)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"テキスト出力: {output_file}", file=sys.stderr)
    else:
        print(text)


def generate_text_report(results: dict) -> str:
    """テキストレポートを生成"""
    lines = []
    
    lines.append("=" * 60)
    lines.append("四柱推命・姓名判断 詳細レポート")
    lines.append("=" * 60)
    lines.append("")
    
    # 基本情報
    inp = results['input']
    lines.append("【基本情報】")
    lines.append(f"生年月日: {inp['birth_date']}")
    lines.append(f"生まれた時刻: {inp['birth_time']}")
    lines.append(f"性別: {inp['gender']}")
    if inp.get('name'):
        lines.append(f"名前: {inp['name']}")
    lines.append("")
    
    # 四柱
    calc = results['calculations']
    chart = calc['chart']
    lines.append("【四柱】")
    lines.append(f"年柱: {chart['year'][0]}{chart['year'][1]}")
    lines.append(f"月柱: {chart['month'][0]}{chart['month'][1]}")
    lines.append(f"日柱: {chart['day'][0]}{chart['day'][1]}")
    lines.append(f"時柱: {chart['hour'][0]}{chart['hour'][1]}")
    lines.append("")
    
    # ハイライト期間
    highlight = calc['highlight_period']
    lines.append("【人生のハイライト期間】")
    lines.append(f"期間: {highlight['start_age']}歳 〜 {highlight['end_age']}歳")
    lines.append(f"ピーク: {highlight['peak_age']}歳")
    lines.append(f"理由: {highlight['reason']}")
    lines.append("")
    
    # アンダーテンション
    under = calc['undertension']
    lines.append("【アンダーテンション期間】")
    lines.append(f"強アンダー月: {under['strong_months']}")
    lines.append(f"弱アンダー月: {under['weak_months']}")
    lines.append(f"理由: {under['reason']}")
    lines.append("")
    
    # 神殺
    if calc.get('special_stars'):
        stars = calc['special_stars']
        lines.append("【神殺】")
        if stars.get('吉神'):
            lines.append(f"吉神: {', '.join(stars['吉神'])}")
        if stars.get('凶神'):
            lines.append(f"凶神: {', '.join(stars['凶神'])}")
        lines.append("")
    
    # 相性判定
    if calc.get('compatibility'):
        compat = calc['compatibility']
        lines.append("【相性判定】")
        lines.append(f"スコア: {compat['score']}/10")
        lines.append(f"タイプ: {compat['type']}")
        lines.append(f"{compat['description']}")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("※ このレポートはプログラムによる自動生成です。")
    lines.append("※ 詳細な解釈はdocx形式のレポートをご参照ください。")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def output_docx_instructions(results, output_file=None):
    """
    Word文書作成の指示を出力
    
    注意: 実際のWord文書作成は、docxスキルを使ってClaudeに依頼する必要があります。
    このスクリプトは計算結果を提供するのみです。
    """
    instructions = f"""
=== Word文書作成指示 ===

計算結果が完了しました。以下の手順でWord文書を作成してください:

【重要】docxスキルを使用してください:
1. /mnt/skills/public/docx/SKILL.md を読む
2. docx-js.md を完全に読む（NEVER set range limits）
3. JavaScriptでWord文書を作成

【推奨される文書構造】

1. 表紙
   - タイトル: 四柱推命・姓名判断 鑑定書
   - 生年月日: {results['input']['birth_date']}
   - 生まれた時刻: {results['input']['birth_time']}
   - 作成日: {datetime.now().strftime('%Y年%m月%d日')}

2. 命式表
   - 四柱の表（年柱・月柱・日柱・時柱）
   - 通変星
   - 十二運
   - 神殺

3. 基本性格
   - 日干の特性
   - 通変星からの分析
   - 多面的な性格描写（矛盾含む）

4. 人生のハイライト期間
   - {results['calculations']['highlight_period']['start_age']}歳〜{results['calculations']['highlight_period']['end_age']}歳
   - ピーク: {results['calculations']['highlight_period']['peak_age']}歳
   - 理由と背景

5. 年代別運勢
   - 10年ごとの大運分析
   - 各時期の特徴と注意点

6. アンダーテンション期間
   - エネルギー低下時期
   - 対策と活用法

7. 開運アドバイス
   - 吉方位
   - ラッキーカラー
   - 適職

8. 総合評価
   - 命式の総合的な解釈
   - 人生の課題と成長の方向性

【計算結果JSONファイル】
{output_file or 'stdout'}

【次のステップ】
1. このJSONファイルを読み込む
2. docx-js.mdの指示に従ってJavaScriptファイルを作成
3. Word文書を生成
4. /mnt/user-data/outputs/ に保存
"""
    
    print(instructions)
    
    if output_file:
        json_file = output_file.replace('.docx', '.json')
        output_json(results, json_file)
        print(f"\n計算結果を保存しました: {json_file}")


def main():
    """メイン処理"""
    try:
        args = parse_arguments()
        
        # 占いを実行
        results = run_fortune_telling(args)
        
        # 出力形式に応じて出力
        if args.output in ['json', 'all']:
            output_file = args.output_file if args.output_file else None
            output_json(results, output_file)
        
        if args.output in ['text', 'all']:
            output_file = args.output_file.replace('.json', '.txt') if args.output_file else None
            output_text(results, output_file)
        
        if args.output == 'docx':
            output_docx_instructions(results, args.output_file)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
