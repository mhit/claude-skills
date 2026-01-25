#!/usr/bin/env python3
"""
人生のハイライト期間計算スクリプト

34-55歳を固定値ではなく、個人の命式と大運に基づいて計算します。

理論的根拠:
1. 日柱の年齢域（33-48歳）が壮年期の中核
2. 大運の3～5回目（約30代～50代）が社会的成功期
3. 身強・身弱と用神・忌神の関係
4. 十二運（建禄・帝旺）の配置
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class HighlightPeriod:
    """ハイライト期間の結果"""
    start_age: int
    end_age: int
    peak_age: int  # 最もスコアが高い年齢
    score: float
    reason: str
    dayun_info: List[Dict]


# 十二運のスコア（強い順）
SHIER_YUN_SCORES = {
    '帝旺': 8,
    '建禄': 6,
    '冠帯': 3,
    '長生': 2,
    '養': 1,
    '胎': 0,
    '絶': -6,
    '墓': -4,
    '死': -4,
    '病': -2,
    '衰': -2,
    '沐浴': 0
}

# 通変星と用神の関係スコア
TSUHEN_SEI_SCORE = {
    '用神一致': 15,
    '忌神': -15,
    '喜神': 10,
    '閑神': 0
}


def calculate_dayun_start_age(birth_year: int, birth_month: int, birth_day: int, 
                              gender: str) -> int:
    """
    大運の開始年齢を計算
    
    簡易版: 性別と生年月の陰陽によって決定
    厳密版は節気からの日数を3日=1歳で換算
    
    Args:
        birth_year: 生年
        birth_month: 生月
        birth_day: 生日
        gender: 性別 ('male' or 'female')
    
    Returns:
        大運開始年齢
    """
    # 簡易計算（実際は節気との距離で計算）
    # 男性: 陽年生まれは順行、陰年生まれは逆行
    # 女性: 陰年生まれは順行、陽年生まれは逆行
    
    is_yang_year = birth_year % 2 == 0  # 偶数年は陽
    
    if gender == 'male':
        is_forward = is_yang_year
    else:
        is_forward = not is_yang_year
    
    # 簡易版: 3〜10歳の範囲で設定
    # 実際は節気からの日数÷3で計算
    base_age = 6  # 平均的な開始年齢
    
    return base_age


def evaluate_dayun_quality(dayun_kan: str, dayun_shi: str, 
                           chart: Dict, yongshen: List[str]) -> float:
    """
    大運の質を評価
    
    Args:
        dayun_kan: 大運の天干
        dayun_shi: 大運の地支
        chart: 命式
        yongshen: 用神のリスト
    
    Returns:
        大運のスコア
    """
    score = 0.0
    
    # 1. 用神・忌神との関係
    if dayun_kan in yongshen or dayun_shi in yongshen:
        score += TSUHEN_SEI_SCORE['用神一致']
    
    # 2. 十二運のスコア
    # （日干×大運支の十二運を計算）
    nikkan = chart['day'][0]
    shier_yun = calculate_shier_yun(nikkan, dayun_shi)
    score += SHIER_YUN_SCORES.get(shier_yun, 0)
    
    # 3. 合・冲・刑・害のスコア
    # 三合成立: +5
    # 六合成立: +3
    # 六冲: -5
    # 三刑: -4
    # 相害: -3
    
    # 簡易版（実装省略）
    
    return score


def calculate_shier_yun(nikkan: str, shi: str) -> str:
    """
    日干と地支から十二運を計算
    
    簡易版（詳細は別ファイル参照）
    """
    # 実装省略（shichusui_calculator.pyを参照）
    return '建禄'  # プレースホルダー


def calculate_highlight_period(birth_date: Tuple[int, int, int],
                               birth_time: Tuple[int, int],
                               gender: str,
                               chart: Dict,
                               dayun_list: List[Dict],
                               yongshen: List[str]) -> HighlightPeriod:
    """
    個人の命式に基づいてハイライト期間を計算
    
    Args:
        birth_date: (年, 月, 日)
        birth_time: (時, 分)
        gender: 'male' or 'female'
        chart: 命式の辞書
        dayun_list: 大運のリスト
        yongshen: 用神のリスト
    
    Returns:
        HighlightPeriod オブジェクト
    """
    birth_year, birth_month, birth_day = birth_date
    
    # 大運開始年齢を計算
    dayun_start_age = calculate_dayun_start_age(
        birth_year, birth_month, birth_day, gender
    )
    
    # 各年齢のスコアを計算
    age_scores = {}
    
    for age in range(20, 71):  # 20歳から70歳まで
        score = 0.0
        
        # 日柱の年齢域（33-48歳）にボーナス
        if 33 <= age <= 48:
            score += 40
        elif 34 <= age <= 55:
            score += 30
        
        # 大運のスコア
        dayun_index = (age - dayun_start_age) // 10
        if 0 <= dayun_index < len(dayun_list):
            dayun = dayun_list[dayun_index]
            dayun_score = evaluate_dayun_quality(
                dayun['kan'], dayun['shi'], chart, yongshen
            )
            score += dayun_score
        
        age_scores[age] = score
    
    # スムージング（移動平均で滑らかに）
    smoothed_scores = {}
    window = 5
    for age in age_scores:
        neighbors = [age_scores.get(a, 0) for a in range(age - window, age + window + 1)]
        smoothed_scores[age] = sum(neighbors) / len(neighbors)
    
    # 閾値以上の連続した期間を抽出
    threshold = sum(smoothed_scores.values()) / len(smoothed_scores) + 5
    
    highlight_ages = [age for age, score in smoothed_scores.items() if score >= threshold]
    
    if not highlight_ages:
        # デフォルト値
        highlight_ages = list(range(34, 56))
    
    # ピーク年齢
    peak_age = max(smoothed_scores, key=smoothed_scores.get)
    
    # 理由の生成
    reason_parts = []
    
    start_age = min(highlight_ages)
    end_age = max(highlight_ages)
    
    # 日柱域との重複
    if 33 <= start_age <= 48 or 33 <= end_age <= 48:
        reason_parts.append("日柱の年齢域（33-48歳）と重なり、人生の中核期間")
    
    # 大運の影響
    peak_dayun_index = (peak_age - dayun_start_age) // 10
    if 0 <= peak_dayun_index < len(dayun_list):
        peak_dayun = dayun_list[peak_dayun_index]
        reason_parts.append(f"第{peak_dayun_index + 1}回大運（{peak_dayun['kan']}{peak_dayun['shi']}）で最も運気が高まる")
    
    reason = "、".join(reason_parts)
    
    return HighlightPeriod(
        start_age=start_age,
        end_age=end_age,
        peak_age=peak_age,
        score=smoothed_scores[peak_age],
        reason=reason,
        dayun_info=[dayun_list[i] for i in range(len(dayun_list)) 
                   if dayun_start_age + i * 10 <= end_age]
    )


def explain_highlight_period(period: HighlightPeriod) -> str:
    """
    ハイライト期間の解釈文を生成
    
    Args:
        period: HighlightPeriod オブジェクト
    
    Returns:
        解釈文
    """
    text = f"""
【人生のハイライト期間】

あなたの命式分析によると、人生のハイライト期間は{period.start_age}歳から{period.end_age}歳です。
特に{period.peak_age}歳前後が最も運気が高まる時期となります。

【理由】
{period.reason}

【この期間の特徴】
これまでの努力が実を結び、社会的にも最も活躍する時期です。
キャリア、家庭、人間関係など、人生の様々な面で充実感を得られるでしょう。

【注意点】
ハイライト期間だからといって何もしなくても成功するわけではありません。
この時期は「努力が最も報われやすい時期」と理解してください。
積極的に行動し、チャンスを掴むことが重要です。

【ハイライト前の準備期間（{period.start_age - 10}〜{period.start_age - 1}歳）】
ハイライト期間に備えて、スキルを磨き、人脈を築く重要な時期です。

【ハイライト後の安定期（{period.end_age + 1}歳以降）】
ハイライト期間で築いた基盤を活かし、安定した人生を送る時期です。
"""
    
    return text.strip()


def main():
    """使用例"""
    # テストデータ
    birth_date = (1982, 2, 25)
    birth_time = (12, 0)
    gender = 'male'
    
    # 簡易的な命式（実際はshichusui_calculator.pyで計算）
    from shichusui_calculator import calc_pillar
    chart = calc_pillar(1982, 2, 25, 12)
    
    # 簡易的な大運リスト（実際は自動計算）
    dayun_list = [
        {'kan': '癸', 'shi': '卯', 'start_age': 6},
        {'kan': '甲', 'shi': '辰', 'start_age': 16},
        {'kan': '乙', 'shi': '巳', 'start_age': 26},
        {'kan': '丙', 'shi': '午', 'start_age': 36},
        {'kan': '丁', 'shi': '未', 'start_age': 46},
        {'kan': '戊', 'shi': '申', 'start_age': 56},
    ]
    
    # 用神（簡易版）
    yongshen = ['木', '火', '丙', '丁', '甲', '乙']
    
    # ハイライト期間を計算
    period = calculate_highlight_period(
        birth_date, birth_time, gender, chart, dayun_list, yongshen
    )
    
    print("=== 人生のハイライト期間判定 ===\n")
    print(f"開始: {period.start_age}歳")
    print(f"終了: {period.end_age}歳")
    print(f"ピーク: {period.peak_age}歳")
    print(f"スコア: {period.score:.2f}")
    print(f"\n理由: {period.reason}")
    
    print("\n" + "=" * 50)
    print(explain_highlight_period(period))


if __name__ == '__main__':
    main()
