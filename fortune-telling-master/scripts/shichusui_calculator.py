#!/usr/bin/env python3
"""
四柱推命自動計算スクリプト

生年月日時から四柱（年月日時の干支）、通変星、十二運、
大運（100歳まで）を自動計算します。
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# 十干
JIKKAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
JIKKAN_EN = ['kou', 'otsu', 'hei', 'tei', 'bo', 'ki', 'kou', 'shin', 'jin', 'ki']

# 十二支
JUNISHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
JUNISHI_EN = ['ne', 'ushi', 'tora', 'u', 'tatsu', 'mi', 'uma', 'hitsuji', 'saru', 'tori', 'inu', 'i']

# 五行属性
GOGYOU = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

# 陰陽
INNYOU = {
    '甲': '陽', '乙': '陰',
    '丙': '陽', '丁': '陰',
    '戊': '陽', '己': '陰',
    '庚': '陽', '辛': '陰',
    '壬': '陽', '癸': '陰'
}

# 蔵干（本気のみ簡略版）
ZOUKAN = {
    '子': ['癸'], '丑': ['己'], '寅': ['甲'], '卯': ['乙'],
    '辰': ['戊'], '巳': ['丙'], '午': ['丁'], '未': ['己'],
    '申': ['庚'], '酉': ['辛'], '戌': ['戊'], '亥': ['壬']
}

# 通変星計算マトリクス
def get_tsuuhensei(nikkan: str, target: str) -> str:
    """日干と対象干から通変星を計算"""
    gogyou_nikkan = GOGYOU[nikkan]
    gogyou_target = GOGYOU[target]
    innyou_nikkan = INNYOU[nikkan]
    innyou_target = INNYOU[target]
    
    # 五行関係
    gogyou_order = {'木': 0, '火': 1, '土': 2, '金': 3, '水': 4}
    nikkan_idx = gogyou_order[gogyou_nikkan]
    target_idx = gogyou_order[gogyou_target]
    diff = (target_idx - nikkan_idx) % 5
    
    same_innyou = (innyou_nikkan == innyou_target)
    
    if diff == 0:  # 同五行
        return '比肩' if same_innyou else '劫財'
    elif diff == 1:  # 日干が生じる
        return '食神' if same_innyou else '傷官'
    elif diff == 2:  # 日干が剋す
        return '偏財' if same_innyou else '正財'
    elif diff == 3:  # 日干が剋される
        return '偏官' if same_innyou else '正官'
    else:  # diff == 4, 日干が生じられる
        return '偏印' if same_innyou else '印綬'

# 十二運計算
JUUNIUN_MAP = {
    ('甲', '亥'): '長生', ('甲', '子'): '沐浴', ('甲', '丑'): '冠帯',
    ('甲', '寅'): '建禄', ('甲', '卯'): '帝旺', ('甲', '辰'): '衰',
    ('甲', '巳'): '病', ('甲', '午'): '死', ('甲', '未'): '墓',
    ('甲', '申'): '絶', ('甲', '酉'): '胎', ('甲', '戌'): '養',
    
    ('乙', '午'): '長生', ('乙', '巳'): '沐浴', ('乙', '辰'): '冠帯',
    ('乙', '卯'): '建禄', ('乙', '寅'): '帝旺', ('乙', '丑'): '衰',
    ('乙', '子'): '病', ('乙', '亥'): '死', ('乙', '戌'): '墓',
    ('乙', '酉'): '絶', ('乙', '申'): '胎', ('乙', '未'): '養',
    
    ('丙', '寅'): '長生', ('丙', '卯'): '沐浴', ('丙', '辰'): '冠帯',
    ('丙', '巳'): '建禄', ('丙', '午'): '帝旺', ('丙', '未'): '衰',
    ('丙', '申'): '病', ('丙', '酉'): '死', ('丙', '戌'): '墓',
    ('丙', '亥'): '絶', ('丙', '子'): '胎', ('丙', '丑'): '養',
    
    ('丁', '酉'): '長生', ('丁', '申'): '沐浴', ('丁', '未'): '冠帯',
    ('丁', '午'): '建禄', ('丁', '巳'): '帝旺', ('丁', '辰'): '衰',
    ('丁', '卯'): '病', ('丁', '寅'): '死', ('丁', '丑'): '墓',
    ('丁', '子'): '絶', ('丁', '亥'): '胎', ('丁', '戌'): '養',
    
    ('戊', '寅'): '長生', ('戊', '卯'): '沐浴', ('戊', '辰'): '冠帯',
    ('戊', '巳'): '建禄', ('戊', '午'): '帝旺', ('戊', '未'): '衰',
    ('戊', '申'): '病', ('戊', '酉'): '死', ('戊', '戌'): '墓',
    ('戊', '亥'): '絶', ('戊', '子'): '胎', ('戊', '丑'): '養',
    
    ('己', '酉'): '長生', ('己', '申'): '沐浴', ('己', '未'): '冠帯',
    ('己', '午'): '建禄', ('己', '巳'): '帝旺', ('己', '辰'): '衰',
    ('己', '卯'): '病', ('己', '寅'): '死', ('己', '丑'): '墓',
    ('己', '子'): '絶', ('己', '亥'): '胎', ('己', '戌'): '養',
    
    ('庚', '巳'): '長生', ('庚', '午'): '沐浴', ('庚', '未'): '冠帯',
    ('庚', '申'): '建禄', ('庚', '酉'): '帝旺', ('庚', '戌'): '衰',
    ('庚', '亥'): '病', ('庚', '子'): '死', ('庚', '丑'): '墓',
    ('庚', '寅'): '絶', ('庚', '卯'): '胎', ('庚', '辰'): '養',
    
    ('辛', '子'): '長生', ('辛', '亥'): '沐浴', ('辛', '戌'): '冠帯',
    ('辛', '酉'): '建禄', ('辛', '申'): '帝旺', ('辛', '未'): '衰',
    ('辛', '午'): '病', ('辛', '巳'): '死', ('辛', '辰'): '墓',
    ('辛', '卯'): '絶', ('辛', '寅'): '胎', ('辛', '丑'): '養',
    
    ('壬', '申'): '長生', ('壬', '酉'): '沐浴', ('壬', '戌'): '冠帯',
    ('壬', '亥'): '建禄', ('壬', '子'): '帝旺', ('壬', '丑'): '衰',
    ('壬', '寅'): '病', ('壬', '卯'): '死', ('壬', '辰'): '墓',
    ('壬', '巳'): '絶', ('壬', '午'): '胎', ('壬', '未'): '養',
    
    ('癸', '卯'): '長生', ('癸', '寅'): '沐浴', ('癸', '丑'): '冠帯',
    ('癸', '子'): '建禄', ('癸', '亥'): '帝旺', ('癸', '戌'): '衰',
    ('癸', '酉'): '病', ('癸', '申'): '死', ('癸', '未'): '墓',
    ('癸', '午'): '絶', ('癸', '巳'): '胎', ('癸', '辰'): '養',
}

def get_juuniun(nikkan: str, shi: str) -> str:
    """日干と地支から十二運を計算"""
    return JUUNIUN_MAP.get((nikkan, shi), '未定')


def calc_kanshi(year: int, base_year: int = 1984, base_kan: int = 0, base_shi: int = 0) -> Tuple[str, str]:
    """年の干支を計算（1984年=甲子を基準）"""
    diff = year - base_year
    kan_idx = (base_kan + diff) % 10
    shi_idx = (base_shi + diff) % 12
    return JIKKAN[kan_idx], JUNISHI[shi_idx]


def calc_pillar(birth_year: int, birth_month: int, birth_day: int, birth_hour: int) -> Dict:
    """
    四柱を計算
    簡易版: 正確な節入りは考慮せず、近似値を使用
    """
    # 年柱（立春を考慮せず簡略化）
    year_kan, year_shi = calc_kanshi(birth_year)
    
    # 月柱（簡略化: 寅月を1月として計算）
    # 実際は節入りを考慮する必要あり
    month_offset = (birth_month - 2) % 12  # 2月=寅月(0)
    month_base_kan = JIKKAN.index(year_kan) * 2 % 10  # 年干から月干を導出
    month_kan = JIKKAN[(month_base_kan + month_offset) % 10]
    month_shi = JUNISHI[month_offset]
    
    # 日柱（1900年1月1日を基準に簡易計算）
    # 実際の四柱推命では万年暦を使用
    base_date = datetime(1900, 1, 1)
    birth_date = datetime(birth_year, birth_month, birth_day)
    days_diff = (birth_date - base_date).days
    day_offset = days_diff % 60
    day_kan = JIKKAN[day_offset % 10]
    day_shi = JUNISHI[day_offset % 12]
    
    # 時柱
    hour_shi_idx = ((birth_hour + 1) // 2) % 12  # 23-1時=子時
    hour_shi = JUNISHI[hour_shi_idx]
    # 日干から時干を導出
    day_kan_idx = JIKKAN.index(day_kan)
    hour_kan_base = day_kan_idx * 2 % 10
    hour_kan = JIKKAN[(hour_kan_base + hour_shi_idx) % 10]
    
    return {
        'year': (year_kan, year_shi),
        'month': (month_kan, month_shi),
        'day': (day_kan, day_shi),
        'hour': (hour_kan, hour_shi)
    }


def calc_taiun(birth_year: int, birth_month: int, birth_day: int, 
               gender: str, month_kan: str, month_shi: str) -> List[Dict]:
    """
    大運を計算（簡略版）
    gender: 'male' or 'female'
    """
    # 陽年・陰年の判定
    year_kan, _ = calc_kanshi(birth_year)
    year_innyou = INNYOU[year_kan]
    
    # 順行・逆行の判定
    if (year_innyou == '陽' and gender == 'male') or (year_innyou == '陰' and gender == 'female'):
        forward = True
    else:
        forward = False
    
    # 立運年齢（簡略版: 3歳と仮定）
    start_age = 3
    
    # 大運の干支を生成
    month_kan_idx = JIKKAN.index(month_kan)
    month_shi_idx = JUNISHI.index(month_shi)
    
    taiun_list = []
    for i in range(10):  # 100歳まで（10年×10期）
        age_start = start_age + i * 10
        if forward:
            kan_idx = (month_kan_idx + i + 1) % 10
            shi_idx = (month_shi_idx + i + 1) % 12
        else:
            kan_idx = (month_kan_idx - i - 1) % 10
            shi_idx = (month_shi_idx - i - 1) % 12
        
        taiun_list.append({
            'age_range': f'{age_start}-{age_start+9}',
            'kan': JIKKAN[kan_idx],
            'shi': JUNISHI[shi_idx]
        })
    
    return taiun_list


def analyze_meishiki(pillars: Dict, gender: str) -> Dict:
    """命式の総合分析"""
    nikkan = pillars['day'][0]  # 日干
    
    # 各柱の通変星
    tsuuhensei = {
        'year_kan': get_tsuuhensei(nikkan, pillars['year'][0]),
        'month_kan': get_tsuuhensei(nikkan, pillars['month'][0]),
        'hour_kan': get_tsuuhensei(nikkan, pillars['hour'][0]),
    }
    
    # 月支元命（月支の蔵干から導出）
    month_shi = pillars['month'][1]
    month_zoukan = ZOUKAN[month_shi][0]
    getsushi_ganmei = get_tsuuhensei(nikkan, month_zoukan)
    
    # 各柱の十二運
    juuniun = {
        'year': get_juuniun(nikkan, pillars['year'][1]),
        'month': get_juuniun(nikkan, pillars['month'][1]),
        'day': get_juuniun(nikkan, pillars['day'][1]),
        'hour': get_juuniun(nikkan, pillars['hour'][1])
    }
    
    return {
        'nikkan': nikkan,
        'nikkan_gogyou': GOGYOU[nikkan],
        'nikkan_innyou': INNYOU[nikkan],
        'tsuuhensei': tsuuhensei,
        'getsushi_ganmei': getsushi_ganmei,
        'juuniun': juuniun
    }


def main():
    """使用例"""
    # 例: 1982年2月25日 10時生まれ、男性
    birth_year = 1982
    birth_month = 2
    birth_day = 25
    birth_hour = 10
    gender = 'male'
    
    print("=== 四柱推命 自動計算 ===\n")
    
    # 四柱を計算
    pillars = calc_pillar(birth_year, birth_month, birth_day, birth_hour)
    
    print("【命式】")
    print(f"年柱: {pillars['year'][0]}{pillars['year'][1]}")
    print(f"月柱: {pillars['month'][0]}{pillars['month'][1]}")
    print(f"日柱: {pillars['day'][0]}{pillars['day'][1]} ← 日干")
    print(f"時柱: {pillars['hour'][0]}{pillars['hour'][1]}\n")
    
    # 分析
    analysis = analyze_meishiki(pillars, gender)
    
    print("【分析】")
    print(f"日干: {analysis['nikkan']} ({analysis['nikkan_innyou']}{analysis['nikkan_gogyou']})")
    print(f"月支元命: {analysis['getsushi_ganmei']}")
    print(f"\n通変星:")
    for key, value in analysis['tsuuhensei'].items():
        print(f"  {key}: {value}")
    print(f"\n十二運:")
    for key, value in analysis['juuniun'].items():
        print(f"  {key}: {value}")
    
    # 大運
    print("\n【大運】")
    taiun = calc_taiun(birth_year, birth_month, birth_day, gender, 
                       pillars['month'][0], pillars['month'][1])
    for t in taiun[:5]:  # 最初の5期のみ表示
        print(f"{t['age_range']}歳: {t['kan']}{t['shi']}")


if __name__ == '__main__':
    main()
