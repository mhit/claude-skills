#!/usr/bin/env python3
"""
相性判定スクリプト

三合・半会・六合・相冲・相刑・相害に基づいて干支の相性を判定します。
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class CompatibilityResult:
    """相性判定結果"""
    score: int  # -10〜10の相性スコア
    type: str  # 相性のタイプ
    description: str
    recommendations: List[str]


# 三合（会局）
SANHE_COMBINATIONS = {
    ('申', '子', '辰'): {'element': '水', 'name': '申子辰水局', 'score': 8},
    ('亥', '卯', '未'): {'element': '木', 'name': '亥卯未木局', 'score': 8},
    ('寅', '午', '戌'): {'element': '火', 'name': '寅午戌火局', 'score': 8},
    ('巳', '酉', '丑'): {'element': '金', 'name': '巳酉丑金局', 'score': 8}
}

# 半会（二つで成立）
BANHUI_COMBINATIONS = [
    (('申', '子'), {'element': '水', 'score': 4}),
    (('子', '辰'), {'element': '水', 'score': 4}),
    (('亥', '卯'), {'element': '木', 'score': 4}),
    (('卯', '未'), {'element': '木', 'score': 4}),
    (('寅', '午'), {'element': '火', 'score': 4}),
    (('午', '戌'), {'element': '火', 'score': 4}),
    (('巳', '酉'), {'element': '金', 'score': 4}),
    (('酉', '丑'), {'element': '金', 'score': 4})
]

# 方合
FANGHE_COMBINATIONS = {
    ('寅', '卯', '辰'): {'direction': '東', 'element': '木', 'name': '東方木局', 'score': 6},
    ('巳', '午', '未'): {'direction': '南', 'element': '火', 'name': '南方火局', 'score': 6},
    ('申', '酉', '戌'): {'direction': '西', 'element': '金', 'name': '西方金局', 'score': 6},
    ('亥', '子', '丑'): {'direction': '北', 'element': '水', 'name': '北方水局', 'score': 6}
}

# 六合
LIUHE_PAIRS = {
    ('子', '丑'): {'transform': '土', 'score': 3},
    ('寅', '亥'): {'transform': '木', 'score': 3},
    ('卯', '戌'): {'transform': '火', 'score': 3},
    ('辰', '酉'): {'transform': '金', 'score': 3},
    ('巳', '申'): {'transform': '水', 'score': 3},
    ('午', '未'): {'transform': '火/土', 'score': 3}
}

# 相冲（対冲）
XIANGCHONG_PAIRS = {
    ('子', '午'): -5,
    ('丑', '未'): -5,
    ('寅', '申'): -5,
    ('卯', '酉'): -5,
    ('辰', '戌'): -5,
    ('巳', '亥'): -5
}

# 相刑
XIANGXING = {
    ('寅', '巳', '申'): {'name': '無恩之刑', 'score': -4},
    ('丑', '戌', '未'): {'name': '持勢之刑', 'score': -4},
    ('子', '卯'): {'name': '無礼之刑', 'score': -3}
}

# 自刑
SELF_PUNISHMENT = ['辰', '午', '酉', '亥']

# 相害
XIANGHHAI_PAIRS = {
    ('子', '未'): -3,
    ('丑', '午'): -3,
    ('寅', '巳'): -3,
    ('卯', '辰'): -3,
    ('申', '亥'): -3,
    ('酉', '戌'): -3
}


def normalize_pair(shi1: str, shi2: str) -> Tuple[str, str]:
    """ペアを正規化（順序統一）"""
    return tuple(sorted([shi1, shi2]))


def check_sanhe(branches: List[str]) -> Dict:
    """三合の判定"""
    result = {'found': False, 'info': None}
    
    for combo, info in SANHE_COMBINATIONS.items():
        if all(b in branches for b in combo):
            result['found'] = True
            result['info'] = info
            result['info']['branches'] = combo
            break
    
    return result


def check_banhui(shi1: str, shi2: str) -> Dict:
    """半会の判定"""
    pair = tuple(sorted([shi1, shi2]))
    
    for comb_pair, info in BANHUI_COMBINATIONS:
        if pair == tuple(sorted(comb_pair)):
            return {'found': True, 'info': info}
    
    return {'found': False}


def check_fanghe(branches: List[str]) -> Dict:
    """方合の判定"""
    result = {'found': False, 'info': None}
    
    for combo, info in FANGHE_COMBINATIONS.items():
        if all(b in branches for b in combo):
            result['found'] = True
            result['info'] = info
            result['info']['branches'] = combo
            break
    
    return result


def check_liuhe(shi1: str, shi2: str) -> Dict:
    """六合の判定"""
    pair = normalize_pair(shi1, shi2)
    
    for liuhe_pair, info in LIUHE_PAIRS.items():
        if pair == normalize_pair(*liuhe_pair):
            return {'found': True, 'info': info, 'pair': liuhe_pair}
    
    return {'found': False}


def check_xiangchong(shi1: str, shi2: str) -> Dict:
    """相冲の判定"""
    pair = normalize_pair(shi1, shi2)
    
    for chong_pair, score in XIANGCHONG_PAIRS.items():
        if pair == normalize_pair(*chong_pair):
            return {'found': True, 'score': score, 'pair': chong_pair}
    
    return {'found': False}


def check_xiangxing(branches: List[str]) -> Dict:
    """相刑の判定"""
    # 三刑
    for xing_combo, info in XIANGXING.items():
        if len(xing_combo) == 3:
            if all(b in branches for b in xing_combo):
                return {'found': True, 'info': info, 'type': 'triple'}
        elif len(xing_combo) == 2:
            if all(b in branches for b in xing_combo):
                return {'found': True, 'info': info, 'type': 'pair'}
    
    # 自刑
    for shi in SELF_PUNISHMENT:
        if branches.count(shi) >= 2:
            return {'found': True, 'info': {'name': f'{shi}の自刑', 'score': -2}, 'type': 'self'}
    
    return {'found': False}


def check_xianghhai(shi1: str, shi2: str) -> Dict:
    """相害の判定"""
    pair = normalize_pair(shi1, shi2)
    
    for hai_pair, score in XIANGHHAI_PAIRS.items():
        if pair == normalize_pair(*hai_pair):
            return {'found': True, 'score': score, 'pair': hai_pair}
    
    return {'found': False}


def judge_compatibility(person1_branches: List[str], person2_branches: List[str]) -> CompatibilityResult:
    """
    二人の相性を総合判定
    
    Args:
        person1_branches: 人物1の地支リスト [年支, 月支, 日支, 時支]
        person2_branches: 人物2の地支リスト [年支, 月支, 日支, 時支]
    
    Returns:
        CompatibilityResult
    """
    score = 0
    findings = []
    recommendations = []
    
    # 全ての地支を統合
    all_branches = person1_branches + person2_branches
    
    # 三合チェック
    sanhe = check_sanhe(all_branches)
    if sanhe['found']:
        score += sanhe['info']['score']
        findings.append(f"三合（{sanhe['info']['name']}）成立: 強力な協力関係")
    
    # 方合チェック
    fanghe = check_fanghe(all_branches)
    if fanghe['found']:
        score += fanghe['info']['score']
        findings.append(f"方合（{fanghe['info']['name']}）成立: 方向性の一致")
    
    # 二人の年支の相性（特に重要）
    year_shi1 = person1_branches[0]
    year_shi2 = person2_branches[0]
    
    # 六合チェック（年支）
    liuhe = check_liuhe(year_shi1, year_shi2)
    if liuhe['found']:
        score += liuhe['info']['score'] * 1.5  # 年支は重要なので1.5倍
        findings.append(f"年支六合（{year_shi1}と{year_shi2}）: 自然な調和")
    
    # 相冲チェック（年支）
    xiangchong = check_xiangchong(year_shi1, year_shi2)
    if xiangchong['found']:
        score += xiangchong['score'] * 1.5  # 年支は重要なので1.5倍
        findings.append(f"年支相冲（{year_shi1}と{year_shi2}）: 対立・衝突の可能性")
        recommendations.append("相冲がある場合は、互いの違いを尊重し、距離感を大切にする")
    
    # 相刑チェック
    xiangxing = check_xiangxing(all_branches)
    if xiangxing['found']:
        score += xiangxing['info']['score']
        findings.append(f"相刑（{xiangxing['info']['name']}）: 内部的な摩擦")
        recommendations.append("相刑がある場合は、感情的な衝突を避け、理性的な対話を心がける")
    
    # 相害チェック（年支）
    xianghhai = check_xianghhai(year_shi1, year_shi2)
    if xianghhai['found']:
        score += xianghhai['score']
        findings.append(f"相害（{year_shi1}と{year_shi2}）: 隠れた障害")
    
    # 日支の相性も確認
    day_shi1 = person1_branches[2]
    day_shi2 = person2_branches[2]
    
    day_liuhe = check_liuhe(day_shi1, day_shi2)
    if day_liuhe['found']:
        score += day_liuhe['info']['score']
        findings.append(f"日支六合（{day_shi1}と{day_shi2}）: 日常的な調和")
    
    day_xiangchong = check_xiangchong(day_shi1, day_shi2)
    if day_xiangchong['found']:
        score += day_xiangchong['score']
        findings.append(f"日支相冲（{day_shi1}と{day_shi2}）: 生活習慣の違い")
    
    # 相性タイプの判定
    if score >= 8:
        compat_type = "非常に良好"
        description = "互いに支え合い、共に成長できる最高の相性です。"
    elif score >= 4:
        compat_type = "良好"
        description = "協力し合える良い相性です。努力次第でさらに良い関係を築けます。"
    elif score >= 0:
        compat_type = "普通"
        description = "標準的な相性です。互いに理解し合う努力が必要です。"
    elif score >= -4:
        compat_type = "やや難"
        description = "いくつかの課題があります。相互理解と妥協が重要です。"
    else:
        compat_type = "困難"
        description = "相性の課題が多い組み合わせです。慎重に関係を築く必要があります。"
    
    # 基本的な推奨事項
    if not recommendations:
        if score >= 4:
            recommendations.append("良い相性を活かして、積極的に協力し合いましょう")
        else:
            recommendations.append("互いの違いを認め、コミュニケーションを大切にしましょう")
    
    # 詳細な説明
    if findings:
        full_description = description + "\n\n【詳細】\n" + "\n".join(f"• {f}" for f in findings)
    else:
        full_description = description + "\n\n特筆すべき相性要素はありません。一般的な相性です。"
    
    return CompatibilityResult(
        score=min(10, max(-10, score)),  # -10〜10の範囲に制限
        type=compat_type,
        description=full_description,
        recommendations=recommendations
    )


def main():
    """使用例"""
    # 例: 1982年2月25日生まれ（壬戌年）と午年生まれの相性
    person1_branches = ['戌', '寅', '巳', '午']  # 壬戌・壬寅・己巳・庚午
    person2_branches = ['午', '子', '卯', '辰']  # 午年生まれ（例）
    
    print("=== 相性判定 ===\n")
    print("人物1の地支:", person1_branches)
    print("人物2の地支:", person2_branches)
    print()
    
    result = judge_compatibility(person1_branches, person2_branches)
    
    print(f"相性スコア: {result.score}/10")
    print(f"相性タイプ: {result.type}")
    print(f"\n{result.description}")
    
    if result.recommendations:
        print("\n【アドバイス】")
        for rec in result.recommendations:
            print(f"• {rec}")


if __name__ == '__main__':
    main()
