#!/usr/bin/env python3
"""
100歳運勢表生成スクリプト

生年月日から100歳までの年運と大運を計算し、
Word文書の表形式で出力します。
"""

from shichusui_calculator import calc_kanshi, get_tsuuhensei, get_juuniun, GOGYOU
from datetime import datetime
from typing import List, Dict

def generate_100year_table(birth_year: int, birth_month: int, birth_day: int,
                           nikkan: str, taiun_list: List[Dict]) -> List[Dict]:
    """
    100歳運勢表のデータを生成
    
    各年について:
    - 年齢
    - 大運（10年周期）
    - 年運（その年の干支）
    - 年運の通変星
    - 年運の十二運
    - 特記事項
    """
    current_year = birth_year
    result = []
    
    for age in range(1, 101):
        year = birth_year + age - 1
        
        # 年運の干支
        year_kan, year_shi = calc_kanshi(year)
        
        # 大運の特定（10年ごと）
        taiun_idx = (age - 1) // 10
        if taiun_idx < len(taiun_list):
            taiun = taiun_list[taiun_idx]
            taiun_kan = taiun['kan']
            taiun_shi = taiun['shi']
        else:
            taiun_kan = '-'
            taiun_shi = '-'
        
        # 通変星と十二運
        nenun_tsuuhensei = get_tsuuhensei(nikkan, year_kan)
        nenun_juuniun = get_juuniun(nikkan, year_shi)
        
        # 年運の五行
        nenun_gogyou = GOGYOU[year_kan]
        
        # 特記事項の判定（簡易版）
        notes = []
        
        # 重要な年齢
        if age in [3, 13, 23, 33, 43, 53, 63, 73, 83, 93]:
            notes.append('大運切替')
        
        if age in [34, 35, 36]:
            notes.append('人生のハイライト開始')
        
        if age in [54, 55]:
            notes.append('人生のハイライト終了')
        
        # 帝旺・建禄の年
        if nenun_juuniun in ['帝旺', '建禄']:
            notes.append('エネルギー最高潮')
        
        # 絶・墓・死の年
        if nenun_juuniun in ['絶', '墓', '死']:
            notes.append('慎重期間')
        
        # 喜神・忌神（簡略版: 実際は命式全体から判断）
        # ここでは例として火が強い場合を想定
        if nenun_gogyou == '水':
            notes.append('喜神')
        elif nenun_gogyou == '火':
            notes.append('要注意')
        
        result.append({
            'age': age,
            'year': year,
            'taiun_kan': taiun_kan,
            'taiun_shi': taiun_shi,
            'nenun_kan': year_kan,
            'nenun_shi': year_shi,
            'tsuuhensei': nenun_tsuuhensei,
            'juuniun': nenun_juuniun,
            'notes': ', '.join(notes) if notes else '-'
        })
    
    return result


def format_table_for_word(data: List[Dict], items_per_table: int = 20) -> List[List[Dict]]:
    """データを表に分割（1表あたり20行程度）"""
    tables = []
    for i in range(0, len(data), items_per_table):
        tables.append(data[i:i+items_per_table])
    return tables


def main():
    """使用例"""
    birth_year = 1982
    birth_month = 2
    birth_day = 25
    nikkan = '甲'  # 日干
    
    # 大運リスト（実際は shichusui_calculator.calc_taiun から取得）
    taiun_list = [
        {'age_range': '3-12', 'kan': '壬', 'shi': '寅'},
        {'age_range': '13-22', 'kan': '癸', 'shi': '卯'},
        {'age_range': '23-32', 'kan': '甲', 'shi': '辰'},
        {'age_range': '33-42', 'kan': '乙', 'shi': '巳'},
        {'age_range': '43-52', 'kan': '丙', 'shi': '午'},
        {'age_range': '53-62', 'kan': '丁', 'shi': '未'},
        {'age_range': '63-72', 'kan': '戊', 'shi': '申'},
        {'age_range': '73-82', 'kan': '己', 'shi': '酉'},
        {'age_range': '83-92', 'kan': '庚', 'shi': '戌'},
        {'age_range': '93-102', 'kan': '辛', 'shi': '亥'},
    ]
    
    # 100歳運勢表を生成
    table_data = generate_100year_table(birth_year, birth_month, birth_day, 
                                       nikkan, taiun_list)
    
    # 表を分割
    tables = format_table_for_word(table_data, 20)
    
    print(f"=== 100歳運勢表（{len(table_data)}行, {len(tables)}表に分割) ===\n")
    
    # 最初の20行を表示
    print("年齢 | 西暦 | 大運 | 年運 | 通変星 | 十二運 | 特記事項")
    print("-" * 80)
    for row in table_data[:20]:
        print(f"{row['age']:3d} | {row['year']} | "
              f"{row['taiun_kan']}{row['taiun_shi']} | "
              f"{row['nenun_kan']}{row['nenun_shi']} | "
              f"{row['tsuuhensei']:4s} | "
              f"{row['juuniun']:4s} | "
              f"{row['notes']}")


if __name__ == '__main__':
    main()
