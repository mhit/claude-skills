#!/usr/bin/env python3
"""
神殺判定スクリプト

命式に現れる神殺（吉神・凶神）を自動判定します。
"""

from typing import Dict, List, Tuple

# 十干
JIKKAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 十二支
JUNISHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


# 天乙貴人の判定表
TENSUI_KIJIN_MAP = {
    '甲': ['丑', '未'],
    '乙': ['子', '申'],
    '丙': ['亥', '酉'],
    '丁': ['亥', '酉'],
    '戊': ['丑', '未'],
    '己': ['子', '申'],
    '庚': ['寅', '午'],
    '辛': ['寅', '午'],
    '壬': ['巳', '卯'],
    '癸': ['巳', '卯']
}

# 天徳貴人の判定表（月支から天干を判定）
TENTOKU_KIJIN_MAP = {
    '子': '丁',
    '丑': '甲',
    '寅': '癸',
    '卯': '庚',
    '辰': '辛',
    '巳': '丙',
    '午': '乙',
    '未': '戊',
    '申': '己',
    '酉': '壬',
    '戌': '辛',
    '亥': '甲'
}

# 月徳貴人の判定表
GETTOKU_KIJIN_MAP = {
    '寅': '丙', '午': '丙', '戌': '丙',
    '申': '壬', '子': '壬', '辰': '壬',
    '巳': '庚', '酉': '庚', '丑': '庚',
    '亥': '甲', '卯': '甲', '未': '甲'
}

# 福星貴人の判定表
FUKUSEI_KIJIN_MAP = {
    '甲': '寅',
    '乙': '卯',
    '丙': '巳',
    '丁': '午',
    '戊': '巳',
    '己': '午',
    '庚': '申',
    '辛': '酉',
    '壬': '亥',
    '癸': '子'
}

# 文昌貴人の判定表
BUNSHOU_KIJIN_MAP = {
    '甲': '巳', '乙': '巳',
    '丙': '午', '丁': '午',
    '戊': '申', '己': '申',
    '庚': '酉', '辛': '酉',
    '壬': '亥', '癸': '亥'
}

# 羊刃の判定表
YOUJIN_MAP = {
    '甲': '卯',
    '乙': '寅',
    '丙': '午',
    '丁': '巳',
    '戊': '午',
    '己': '巳',
    '庚': '酉',
    '辛': '申',
    '壬': '子',
    '癸': '亥'
}

# 孤辰の判定表
KOSHIN_MAP = {
    '寅': '寅', '午': '寅', '戌': '寅',
    '申': '申', '子': '申', '辰': '申',
    '巳': '巳', '酉': '巳', '丑': '巳',
    '亥': '亥', '卯': '亥', '未': '亥'
}

# 寡宿の判定表
KASHUKU_MAP = {
    '寅': '戌', '午': '戌', '戌': '戌',
    '申': '辰', '子': '辰', '辰': '辰',
    '巳': '丑', '酉': '丑', '丑': '丑',
    '亥': '未', '卯': '未', '未': '未'
}

# 駅馬の判定表
EKIBA_MAP = {
    '寅': '申', '午': '申', '戌': '申',
    '申': '寅', '子': '寅', '辰': '寅',
    '巳': '亥', '酉': '亥', '丑': '亥',
    '亥': '巳', '卯': '巳', '未': '巳'
}

# 亡神の判定表
BOUSHIN_MAP = {
    '寅': '亥', '午': '亥', '戌': '亥',
    '申': '巳', '子': '巳', '辰': '巳',
    '巳': '申', '酉': '申', '丑': '申',
    '亥': '寅', '卯': '寅', '未': '寅'
}

# 劫殺の判定表
GOUSATSU_MAP = {
    '寅': '巳', '午': '巳', '戌': '巳',
    '申': '亥', '子': '亥', '辰': '亥',
    '巳': '寅', '酉': '寅', '丑': '寅',
    '亥': '申', '卯': '申', '未': '申'
}

# 桃花の判定表
TOUKA_MAP = {
    '寅': '卯', '午': '卯', '戌': '卯',
    '申': '酉', '子': '酉', '辰': '酉',
    '巳': '午', '酉': '午', '丑': '午',
    '亥': '子', '卯': '子', '未': '子'
}


def calc_special_stars(pillars: Dict, nikkan: str) -> Dict:
    """
    神殺を判定する
    
    Args:
        pillars: 四柱の辞書 {'year': (年干, 年支), 'month': (月干, 月支), ...}
        nikkan: 日干
    
    Returns:
        神殺の辞書
    """
    special_stars = {
        'kissen': [],   # 吉神
        'kyoushin': []  # 凶神
    }
    
    year_kan, year_shi = pillars['year']
    month_kan, month_shi = pillars['month']
    day_kan, day_shi = pillars['day']
    hour_kan, hour_shi = pillars['hour']
    
    # 全ての地支
    all_shi = [year_shi, month_shi, day_shi, hour_shi]
    
    # === 吉神の判定 ===
    
    # 天乙貴人（日干または年干から）
    tensui_targets = TENSUI_KIJIN_MAP.get(nikkan, [])
    for shi in all_shi:
        if shi in tensui_targets:
            pillar_name = _get_pillar_name_by_shi(pillars, shi)
            special_stars['kissen'].append({
                'name': '天乙貴人',
                'position': pillar_name,
                'description': '最高位の吉神。困難に遭っても援助者が現れ、中晩年に必ず発達する。'
            })
    
    # 天徳貴人（月支から天干を判定）
    tentoku_kan = TENTOKU_KIJIN_MAP.get(month_shi)
    if tentoku_kan:
        for pillar_name, (kan, shi) in pillars.items():
            if kan == tentoku_kan:
                special_stars['kissen'].append({
                    'name': '天徳貴人',
                    'position': pillar_name,
                    'description': '天の徳を受ける吉星。災厄を免れ、万事順調。'
                })
    
    # 月徳貴人（月支から天干を判定）
    gettoku_kan = GETTOKU_KIJIN_MAP.get(month_shi)
    if gettoku_kan:
        for pillar_name, (kan, shi) in pillars.items():
            if kan == gettoku_kan:
                special_stars['kissen'].append({
                    'name': '月徳貴人',
                    'position': pillar_name,
                    'description': '月の徳を受ける吉星。社会的評価が高い。'
                })
    
    # 福星貴人（日干から）
    fukusei_shi = FUKUSEI_KIJIN_MAP.get(nikkan)
    if fukusei_shi and fukusei_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, fukusei_shi)
        special_stars['kissen'].append({
            'name': '福星貴人',
            'position': pillar_name,
            'description': '福徳を授かる吉星。財運に恵まれる。'
        })
    
    # 文昌貴人（日干から）
    bunshou_shi = BUNSHOU_KIJIN_MAP.get(nikkan)
    if bunshou_shi and bunshou_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, bunshou_shi)
        special_stars['kissen'].append({
            'name': '文昌貴人',
            'position': pillar_name,
            'description': '学問・芸術の才能。知性に恵まれる。'
        })
    
    # === 凶神の判定 ===
    
    # 羊刃（日干から）
    youjin_shi = YOUJIN_MAP.get(nikkan)
    if youjin_shi and youjin_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, youjin_shi)
        special_stars['kyoushin'].append({
            'name': '羊刃',
            'position': pillar_name,
            'description': '激しい気性、衝動的。怪我や事故の危険。思慮分別に欠け、口が悪く、表現が荒い。'
        })
    
    # 孤辰（年支または日支から）
    koshin_shi = KOSHIN_MAP.get(year_shi)
    if koshin_shi and koshin_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, koshin_shi)
        special_stars['kyoushin'].append({
            'name': '孤辰',
            'position': pillar_name,
            'description': '孤独の暗示。身内の縁薄い。独立心が強い。'
        })
    
    # 寡宿（年支または日支から）
    kashuku_shi = KASHUKU_MAP.get(year_shi)
    if kashuku_shi and kashuku_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, kashuku_shi)
        special_stars['kyoushin'].append({
            'name': '寡宿',
            'position': pillar_name,
            'description': '配偶者との縁が薄い。精神的な孤立。'
        })
    
    # 駅馬（年支または日支から）
    ekiba_shi = EKIBA_MAP.get(year_shi)
    if ekiba_shi and ekiba_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, ekiba_shi)
        special_stars['kyoushin'].append({
            'name': '駅馬',
            'position': pillar_name,
            'description': '移動、変化、旅行。転職や引越しが多い。落ち着きがない。'
        })
    
    # 亡神（年支から）
    boushin_shi = BOUSHIN_MAP.get(year_shi)
    if boushin_shi and boushin_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, boushin_shi)
        special_stars['kyoushin'].append({
            'name': '亡神',
            'position': pillar_name,
            'description': '突発的な災難。金銭損失。計画の失敗。'
        })
    
    # 劫殺（年支から）
    gousatsu_shi = GOUSATSU_MAP.get(year_shi)
    if gousatsu_shi and gousatsu_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, gousatsu_shi)
        special_stars['kyoushin'].append({
            'name': '劫殺',
            'position': pillar_name,
            'description': '突発的なトラブル。盗難に注意。'
        })
    
    # 桃花（年支または日支から）
    touka_shi = TOUKA_MAP.get(year_shi)
    if touka_shi and touka_shi in all_shi:
        pillar_name = _get_pillar_name_by_shi(pillars, touka_shi)
        special_stars['kyoushin'].append({
            'name': '桃花',
            'position': pillar_name,
            'description': '異性縁が強い。魅力的だが、酒色に溺れる傾向。色情の過ち。'
        })
    
    return special_stars


def _get_pillar_name_by_shi(pillars: Dict, target_shi: str) -> str:
    """地支から柱の名前を取得"""
    for name, (kan, shi) in pillars.items():
        if shi == target_shi:
            if name == 'year':
                return '年柱'
            elif name == 'month':
                return '月柱'
            elif name == 'day':
                return '日柱'
            elif name == 'hour':
                return '時柱'
    return '不明'


def calc_highlight_period(birth_year: int, taiun_list: List[Dict]) -> Dict:
    """
    人生のハイライト期間を判定
    
    34-55歳が基本だが、大運の影響で前後する場合がある
    """
    # 基本は34-55歳
    base_start = 34
    base_end = 55
    
    # 大運の影響による調整（簡易版）
    # 実際には大運の通変星や十二運によって詳細な判定が必要
    
    return {
        'start_age': base_start,
        'end_age': base_end,
        'description': '人生のハイライト期間。これまでの努力が実を結び、社会的にも最も活躍する時期。'
    }


def calc_undertension_period(nikkan: str) -> Dict:
    """
    アンダーテンション期間を計算
    
    日干の五行によって、エネルギーが低下する月と時間帯が決まる
    """
    # 簡易版: 己（土）の場合
    # 実際には日干ごとに異なる
    
    if nikkan in ['戊', '己']:  # 土
        return {
            'months': [6, 7, 8],
            'hours': list(range(13, 20)),  # 13-19時
            'description': 'この時期は、一押しの事柄のスタートは出来ず、充電や点検に集中すべき。'
        }
    
    # 他の日干のパターンも実装が必要
    return {
        'months': [],
        'hours': [],
        'description': ''
    }


def main():
    """使用例"""
    # テスト用の命式
    pillars = {
        'year': ('壬', '戌'),
        'month': ('庚', '子'),
        'day': ('己', '巳'),
        'hour': ('庚', '午')
    }
    nikkan = '己'
    
    print("=== 神殺判定 ===\n")
    special_stars = calc_special_stars(pillars, nikkan)
    
    print("【吉神】")
    if special_stars['kissen']:
        for star in special_stars['kissen']:
            print(f"{star['name']} ({star['position']}): {star['description']}")
    else:
        print("なし")
    
    print("\n【凶神】")
    if special_stars['kyoushin']:
        for star in special_stars['kyoushin']:
            print(f"{star['name']} ({star['position']}): {star['description']}")
    else:
        print("なし")
    
    print("\n【人生のハイライト期間】")
    highlight = calc_highlight_period(1982, [])
    print(f"{highlight['start_age']}-{highlight['end_age']}歳: {highlight['description']}")
    
    print("\n【アンダーテンション期間】")
    undertension = calc_undertension_period(nikkan)
    if undertension['months']:
        print(f"月: {undertension['months']}")
        print(f"時間帯: {undertension['hours']}時")
        print(f"説明: {undertension['description']}")


if __name__ == '__main__':
    main()
