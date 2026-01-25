#!/usr/bin/env python3
"""
天使ネット解釈抽出・分析スクリプト

天使ネット(tengel)から取得した解釈文を分析し、
データベースに追加する新しい表現やパターンを抽出します。
"""

import re
from typing import Dict, List, Set

class TengelAnalyzer:
    """天使ネット解釈文の分析クラス"""
    
    def __init__(self):
        self.interpretations = {
            'tsuuhensei': {},  # 通変星の解釈
            'juuniun': {},     # 十二運の解釈
            'shinsatsu': {},   # 神殺の解釈
            'general': []      # 総合的な表現
        }
        
    def extract_keywords(self, text: str) -> Set[str]:
        """解釈文から重要なキーワードを抽出"""
        # 職業関連
        career_pattern = r'(職業|適性|仕事|業務|経営|リーダー|独立|自営)'
        # 性格関連
        personality_pattern = r'(性格|気質|傾向|特性|個性|人柄)'
        # 対人関係
        relationship_pattern = r'(対人|人間関係|社交|友人|上司|部下)'
        # 財運
        finance_pattern = r'(財運|金銭|蓄財|収入|支出|貯蓄)'
        # 健康
        health_pattern = r'(健康|病気|体質|注意)'
        
        keywords = set()
        for pattern in [career_pattern, personality_pattern, 
                       relationship_pattern, finance_pattern, health_pattern]:
            matches = re.findall(pattern, text)
            keywords.update(matches)
        
        return keywords
    
    def analyze_structure(self, text: str) -> Dict:
        """解釈文の構造を分析"""
        lines = text.split('\n')
        structure = {
            'paragraphs': len([l for l in lines if l.strip()]),
            'has_bullets': '・' in text or '○' in text,
            'has_warnings': '注意' in text or '！' in text,
            'tone': self._analyze_tone(text),
            'length': len(text)
        }
        return structure
    
    def _analyze_tone(self, text: str) -> str:
        """文章のトーンを分析"""
        if '～である' in text or '～する人' in text:
            return 'assertive'  # 断定的
        elif '～傾向' in text or '～ことが多い' in text:
            return 'moderate'   # 穏健
        elif '～かもしれない' in text or '～可能性' in text:
            return 'tentative'  # 控えめ
        else:
            return 'neutral'
    
    def extract_contradictions(self, text: str) -> List[str]:
        """矛盾する記述を抽出"""
        contradictions = []
        
        # 「しかし」「ただし」「一方」などの接続詞を探す
        contradiction_markers = ['しかし', 'ただし', '一方', 'が、', 'だが']
        
        sentences = text.split('。')
        for i, sentence in enumerate(sentences):
            for marker in contradiction_markers:
                if marker in sentence:
                    # 前後の文を取得
                    if i > 0:
                        prev = sentences[i-1].strip()
                        curr = sentence.strip()
                        contradictions.append({
                            'before': prev,
                            'after': curr,
                            'marker': marker
                        })
        
        return contradictions
    
    def compare_with_existing(self, new_text: str, 
                             existing_db: str) -> Dict:
        """既存のデータベースと比較して新規表現を抽出"""
        new_keywords = self.extract_keywords(new_text)
        existing_keywords = self.extract_keywords(existing_db)
        
        unique_keywords = new_keywords - existing_keywords
        
        return {
            'new_keywords': list(unique_keywords),
            'coverage': len(new_keywords & existing_keywords) / len(new_keywords) if new_keywords else 0
        }
    
    def generate_database_entry(self, star_name: str, 
                                interpretation: str) -> str:
        """新しいデータベースエントリを生成"""
        keywords = self.extract_keywords(interpretation)
        structure = self.analyze_structure(interpretation)
        contradictions = self.extract_contradictions(interpretation)
        
        entry = f"""
### {star_name}

**基本解釈**:
{interpretation}

**抽出されたキーワード**:
{', '.join(keywords)}

**文章構造**:
- 段落数: {structure['paragraphs']}
- 箇条書き: {'あり' if structure['has_bullets'] else 'なし'}
- 警告文: {'あり' if structure['has_warnings'] else 'なし'}
- トーン: {structure['tone']}
- 文字数: {structure['length']}

**矛盾表現**:
{len(contradictions)}箇所
"""
        
        for i, contra in enumerate(contradictions, 1):
            entry += f"\n{i}. {contra['before']} {contra['marker']} {contra['after']}"
        
        return entry


def main():
    """使用例"""
    analyzer = TengelAnalyzer()
    
    # サンプル解釈文（実際にはユーザーから取得）
    sample_text = """
    職業的には、専門知識、技術、制作、職人、技芸芸術、
    マニアック、オタク的な職業適性を持つ。
    物事を実直正確に拘わりを持って、信用と真面目さを基調に処理する人。
    しかし、複数の物事を同時に行う時や、指示命令が的確でない場合は
    パニックに陥り、事の責任を追求されると、他力本願な言い訳や
    他人に頼り、責任から逃れる傾向も持つ。
    """
    
    print("=== 天使ネット解釈分析 ===\n")
    
    # キーワード抽出
    keywords = analyzer.extract_keywords(sample_text)
    print(f"キーワード: {keywords}\n")
    
    # 構造分析
    structure = analyzer.analyze_structure(sample_text)
    print(f"構造: {structure}\n")
    
    # 矛盾抽出
    contradictions = analyzer.extract_contradictions(sample_text)
    print(f"矛盾箇所: {len(contradictions)}個")
    for contra in contradictions:
        print(f"  {contra['marker']} で接続")


if __name__ == '__main__':
    main()
