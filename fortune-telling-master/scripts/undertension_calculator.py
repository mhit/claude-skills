#!/usr/bin/env python3
"""
アンダーテンション期間計算スクリプト

十二長生の弱運期（衰・病・死・墓・絶）に基づいてエネルギー低下期間を計算します。

理論的根拠:
- 日干の五行が弱まる月・時間帯
- 十二運で「衰・病・死・墓・絶」に該当する期間
- 五行の相生相剋理論
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class UndertensionPeriod:
    """アンダーテンション期間"""
    strong_months: List[int]  # 強アンダー月（死・墓・絶）
    weak_months: List[int]    # 弱アンダー月（衰・病）
    strong_hours: List[Tuple[int, int]]  # 強アンダー時間帯
    reason: str


# 全日干のアンダーテンション月と時間帯（リサーチ結果より）
UNDERTENSION_TABLE = {
    # 木（甲・乙）
    '甲': {
        'strong_months': [6, 7, 8],      # 午・未・申月（死・墓・絶）
        'weak_months': [4, 5],           # 辰・巳月（衰・病）
        'strong_hours': [(11, 13), (13, 15), (15, 17)],  # 午・未・申時
        'reason': '木が金に剋される秋季、木の十二運で死→墓→絶に該当'
    },
    '乙': {
        'strong_months': [6, 7, 8],
        'weak_months': [4, 5],
        'strong_hours': [(11, 13), (13, 15), (15, 17)],
        'reason': '木が金に剋される秋季、木の十二運で死→墓→絶に該当'
    },
    
    # 火（丙・丁）
    '丙': {
        'strong_months': [9, 10, 11],    # 酉・戌・亥月（死・墓・絶）
        'weak_months': [7, 8],           # 申・未月（衰・病）
        'strong_hours': [(17, 19), (19, 21), (21, 23)],  # 酉・戌・亥時
        'reason': '火が水に剋される冬季、火の十二運で死→墓→絶に該当'
    },
    '丁': {
        'strong_months': [9, 10, 11],
        'weak_months': [7, 8],
        'strong_hours': [(17, 19), (19, 21), (21, 23)],
        'reason': '火が水に剋される冬季、火の十二運で死→墓→絶に該当'
    },
    
    # 土（戊・己）
    '戊': {
        'strong_months': [9, 10, 11],    # 酉・戌・亥月（死・墓・絶）
        'weak_months': [7, 8],           # 申・未月（衰・病）
        'strong_hours': [(17, 19), (19, 21), (21, 23)],  # 酉・戌・亥時
        'reason': '土は火系と同系列、木に剋される春季または火系の衰退期'
    },
    '己': {
        'strong_months': [1, 2, 3],      # 寅・卯・辰月（木旺の季節）
        'weak_months': [11, 12],         # 亥・子月
        'strong_hours': [(3, 5), (5, 7), (7, 9)],  # 寅・卯・辰時
        'reason': '土が木に剋される春季、土の十二運で死→墓→絶に該当'
    },
    
    # 金（庚・辛）
    '庚': {
        'strong_months': [12, 1, 2],     # 子・丑・寅月（死・墓・絶）
        'weak_months': [10, 11],         # 亥・戌月（衰・病）
        'strong_hours': [(23, 1), (1, 3), (3, 5)],  # 子・丑・寅時
        'reason': '金が火に剋される夏季、金の十二運で死→墓→絶に該当'
    },
    '辛': {
        'strong_months': [4, 5, 6],      # 夏季
        'weak_months': [3, 7],
        'strong_hours': [(9, 11), (11, 13)],  # 巳・午時
        'reason': '金が火に剋される夏季、金の十二運で死→墓→絶に該当'
    },
    
    # 水（壬・癸）
    '壬': {
        'strong_months': [4, 5, 6],      # 辰・巳・午月（死・墓・絶）
        'weak_months': [3, 7],           # 卯・未月（衰・病）
        'strong_hours': [(7, 9), (9, 11), (11, 13)],  # 辰・巳・午時
        'reason': '水が土に剋される季節変わり目、水の十二運で死→墓→絶に該当'
    },
    '癸': {
        'strong_months': [4, 5, 6],
        'weak_months': [3, 7],
        'strong_hours': [(7, 9), (9, 11), (11, 13)],
        'reason': '水が土に剋される季節変わり目、水の十二運で死→墓→絶に該当'
    }
}


def get_undertension_period(nikkan: str) -> UndertensionPeriod:
    """
    日干からアンダーテンション期間を取得
    
    Args:
        nikkan: 日干（甲・乙・丙・丁・戊・己・庚・辛・壬・癸）
    
    Returns:
        UndertensionPeriod オブジェクト
    """
    if nikkan not in UNDERTENSION_TABLE:
        raise ValueError(f"Invalid nikkan: {nikkan}")
    
    data = UNDERTENSION_TABLE[nikkan]
    
    return UndertensionPeriod(
        strong_months=data['strong_months'],
        weak_months=data['weak_months'],
        strong_hours=data['strong_hours'],
        reason=data['reason']
    )


def format_month_names(months: List[int]) -> str:
    """
    月番号を月名に変換
    
    Args:
        months: 月番号のリスト（1-12）
    
    Returns:
        月名の文字列
    """
    month_names = {
        1: '1月（丑月）', 2: '2月（寅月）', 3: '3月（卯月）',
        4: '4月（辰月）', 5: '5月（巳月）', 6: '6月（午月）',
        7: '7月（未月）', 8: '8月（申月）', 9: '9月（酉月）',
        10: '10月（戌月）', 11: '11月（亥月）', 12: '12月（子月）'
    }
    return '、'.join([month_names[m] for m in months])


def format_hours(hours: List[Tuple[int, int]]) -> str:
    """
    時間帯を文字列に変換
    
    Args:
        hours: 時間帯のリスト [(開始, 終了), ...]
    
    Returns:
        時間帯の文字列
    """
    hour_to_shi = {
        (23, 1): '子時（23-1時）',
        (1, 3): '丑時（1-3時）',
        (3, 5): '寅時（3-5時）',
        (5, 7): '卯時（5-7時）',
        (7, 9): '辰時（7-9時）',
        (9, 11): '巳時（9-11時）',
        (11, 13): '午時（11-13時）',
        (13, 15): '未時（13-15時）',
        (15, 17): '申時（15-17時）',
        (17, 19): '酉時（17-19時）',
        (19, 21): '戌時（19-21時）',
        (21, 23): '亥時（21-23時）'
    }
    return '、'.join([hour_to_shi.get(h, f'{h[0]}-{h[1]}時') for h in hours])


def explain_undertension(nikkan: str) -> str:
    """
    アンダーテンション期間の解釈文を生成
    
    Args:
        nikkan: 日干
    
    Returns:
        解釈文
    """
    period = get_undertension_period(nikkan)
    
    strong_months_str = format_month_names(period.strong_months)
    weak_months_str = format_month_names(period.weak_months)
    strong_hours_str = format_hours(period.strong_hours)
    
    text = f"""
【アンダーテンション期間（エネルギー低下期）】

あなたの日干は「{nikkan}」です。

■ 強アンダー期間（特に注意が必要）
・月: {strong_months_str}
・時間帯: {strong_hours_str}

■ 弱アンダー期間（やや注意）
・月: {weak_months_str}

【理論的根拠】
{period.reason}

【この期間の過ごし方】
１．重要な決断は避ける
この時期は、肉体・精神・感情の制御能力が極度に弱まります。
重要な契約、転職、結婚、投資などの大きな決断は、
可能な限りエネルギーが高い時期に延期することをお勧めします。

２．充電・点検に集中
新しいことを始めるのではなく、休息と内省の時期と捉えてください。
- 健康チェック、定期検診
- スキルアップのための学習
- 人間関係の整理
- 計画の見直し

３．勘違い・誤解に注意
この時期は、人の評価を見誤ったり、言動の理解力が落ちたりします。
冷静さを保ち、即断即決を避けましょう。

４．悪い癖が出やすい
普段は抑えている欠点や悪癖が大きく突出しやすい時期です。
自己認識を高め、感情的な反応を控えることが重要です。

【ポジティブな活用法】
・深い思索や研究に向く
・精神世界への関心が高まる
・内面の成長のチャンス
・次の活動期への準備期間

【注意】
これはあくまで「傾向」です。個人の命式全体のバランスや
大運の影響によって、実際の影響は異なります。
過度に気にしすぎず、参考程度にしてください。
"""
    
    return text.strip()


def get_current_status(nikkan: str, current_month: int, current_hour: int) -> Dict:
    """
    現在の状態を判定
    
    Args:
        nikkan: 日干
        current_month: 現在の月（1-12）
        current_hour: 現在の時刻（0-23）
    
    Returns:
        状態の辞書
    """
    period = get_undertension_period(nikkan)
    
    status = {
        'is_strong_undertension_month': current_month in period.strong_months,
        'is_weak_undertension_month': current_month in period.weak_months,
        'is_strong_undertension_hour': False,
        'energy_level': 'normal'
    }
    
    # 時間帯チェック
    for start, end in period.strong_hours:
        if start <= current_hour < end or (start > end and (current_hour >= start or current_hour < end)):
            status['is_strong_undertension_hour'] = True
            break
    
    # エネルギーレベル判定
    if status['is_strong_undertension_month'] and status['is_strong_undertension_hour']:
        status['energy_level'] = 'very_low'
    elif status['is_strong_undertension_month'] or status['is_strong_undertension_hour']:
        status['energy_level'] = 'low'
    elif status['is_weak_undertension_month']:
        status['energy_level'] = 'slightly_low'
    
    return status


def main():
    """使用例"""
    nikkan = '己'
    
    print("=== アンダーテンション期間判定 ===\n")
    print(explain_undertension(nikkan))
    
    # 現在の状態をチェック（例: 6月15日 13時）
    print("\n" + "=" * 50)
    print("【現在の状態チェック】\n")
    
    current_month = 6
    current_hour = 13
    
    status = get_current_status(nikkan, current_month, current_hour)
    
    print(f"現在: {current_month}月 {current_hour}時")
    print(f"エネルギーレベル: {status['energy_level']}")
    
    if status['energy_level'] == 'very_low':
        print("⚠️ 非常に低いエネルギー期間です。重要な決断は避けましょう。")
    elif status['energy_level'] == 'low':
        print("⚠️ 低エネルギー期間です。慎重に行動しましょう。")
    elif status['energy_level'] == 'slightly_low':
        print("ℹ️ やや低エネルギー期間です。無理は禁物です。")
    else:
        print("✓ 通常のエネルギーレベルです。")


if __name__ == '__main__':
    main()
