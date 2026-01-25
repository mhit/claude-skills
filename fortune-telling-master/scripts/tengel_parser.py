#!/usr/bin/env python3
"""
天使ネットデータパーサー

提供された天使ネットの解釈文を解析し、
構造化されたデータベースに変換します。
"""

import re
from typing import List, Dict


class TengelDataParser:
    """天使ネットデータの解析クラス"""
    
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.sections = {}
    
    def parse(self) -> Dict:
        """テキストを解析してセクションごとに分割"""
        
        # セクションを識別するパターン
        sections = {
            'basic_info': self._extract_basic_info(),
            'career': self._extract_career_section(),
            'service_spirit': self._extract_service_section(),
            'freedom': self._extract_freedom_section(),
            'personality': self._extract_personality_section(),
            'health': self._extract_health_section(),
            'fortune': self._extract_fortune_section(),
            'warnings': self._extract_warnings(),
            'lucky_gods': self._extract_lucky_gods(),
            'unlucky_gods': self._extract_unlucky_gods()
        }
        
        return sections
    
    def _extract_basic_info(self) -> Dict:
        """基本情報を抽出"""
        info = {}
        
        # 生年月日
        date_match = re.search(r'(\d{4})年.*?(\d{1,2})月\s*(\d{1,2})日', self.raw_text)
        if date_match:
            info['year'] = date_match.group(1)
            info['month'] = date_match.group(2)
            info['day'] = date_match.group(3)
        
        # 性別
        if '男性' in self.raw_text:
            info['gender'] = 'male'
        elif '女性' in self.raw_text:
            info['gender'] = 'female'
        
        return info
    
    def _extract_career_section(self) -> str:
        """職業適性セクションを抽出"""
        # 「職業的には」で始まる段落を探す
        match = re.search(
            r'職業的には、.*?(?=\n\n|\n　[^\s]|$)',
            self.raw_text,
            re.DOTALL
        )
        
        if match:
            return match.group(0).strip()
        return ""
    
    def _extract_service_section(self) -> str:
        """奉仕・世話焼きセクションを抽出"""
        match = re.search(
            r'生来、人の世話焼きや.*?(?=\n\n|\n　[^\s]|$)',
            self.raw_text,
            re.DOTALL
        )
        
        if match:
            return match.group(0).strip()
        return ""
    
    def _extract_freedom_section(self) -> str:
        """自由主義セクションを抽出"""
        match = re.search(
            r'社会的な地位、名誉、権威.*?(?=\n\n|\n　[^\s]|$)',
            self.raw_text,
            re.DOTALL
        )
        
        if match:
            return match.group(0).strip()
        return ""
    
    def _extract_personality_section(self) -> List[str]:
        """性格セクションを抽出（複数段落）"""
        paragraphs = []
        
        # 性格に関連する段落を探す
        patterns = [
            r'物事に忠実で.*?(?=\n\n|\n　(?:例え|遺伝|この人)|$)',
            r'人当たりよく.*?(?=\n\n|$)',
            r'明敏で頑張り屋.*?(?=\n\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.raw_text, re.DOTALL)
            if match:
                paragraphs.append(match.group(0).strip())
        
        return paragraphs
    
    def _extract_health_section(self) -> str:
        """健康に関するセクションを抽出"""
        match = re.search(
            r'体質.*?病気.*?(?=\n\n|愛情|財運|$)',
            self.raw_text,
            re.DOTALL
        )
        
        if match:
            return match.group(0).strip()
        return ""
    
    def _extract_fortune_section(self) -> str:
        """財運セクションを抽出"""
        match = re.search(
            r'財運的には.*?(?=\n\n|幼少|$)',
            self.raw_text,
            re.DOTALL
        )
        
        if match:
            return match.group(0).strip()
        return ""
    
    def _extract_warnings(self) -> List[str]:
        """注意事項を抽出"""
        warnings = []
        
        # 「注意」を含む文を探す
        sentences = self.raw_text.split('。')
        for sentence in sentences:
            if '注意' in sentence or '！' in sentence:
                warnings.append(sentence.strip() + '。')
        
        return warnings
    
    def _extract_lucky_gods(self) -> str:
        """吉神セクションを抽出"""
        match = re.search(
            r'例え、親の遺産なくとも.*?(?=\n\n　この人は|以下は|$)',
            self.raw_text,
            re.DOTALL
        )
        
        if match:
            return match.group(0).strip()
        return ""
    
    def _extract_unlucky_gods(self) -> str:
        """凶神セクションを抽出"""
        match = re.search(
            r'以下は、留意すべきこの人の凶神です.*?(?=$)',
            self.raw_text,
            re.DOTALL
        )
        
        if match:
            return match.group(0).strip()
        return ""
    
    def generate_structured_markdown(self) -> str:
        """構造化されたMarkdown形式で出力"""
        sections = self.parse()
        
        md = "# 天使ネット解釈（実データ）\n\n"
        
        # 基本情報
        if sections['basic_info']:
            info = sections['basic_info']
            md += f"## 基本情報\n\n"
            md += f"- 生年月日: {info.get('year', '')}年{info.get('month', '')}月{info.get('day', '')}日\n"
            md += f"- 性別: {info.get('gender', '')}\n\n"
        
        # 職業適性
        if sections['career']:
            md += f"## 職業適性\n\n{sections['career']}\n\n"
        
        # 奉仕精神
        if sections['service_spirit']:
            md += f"## 奉仕・世話焼き精神\n\n{sections['service_spirit']}\n\n"
        
        # 自由主義
        if sections['freedom']:
            md += f"## 自由主義・楽天性\n\n{sections['freedom']}\n\n"
        
        # 性格
        if sections['personality']:
            md += f"## 性格・気質\n\n"
            for para in sections['personality']:
                md += f"{para}\n\n"
        
        # 健康
        if sections['health']:
            md += f"## 健康\n\n{sections['health']}\n\n"
        
        # 財運
        if sections['fortune']:
            md += f"## 財運\n\n{sections['fortune']}\n\n"
        
        # 吉神
        if sections['lucky_gods']:
            md += f"## 吉神の影響\n\n{sections['lucky_gods']}\n\n"
        
        # 凶神
        if sections['unlucky_gods']:
            md += f"## 凶神の影響\n\n{sections['unlucky_gods']}\n\n"
        
        # 注意事項
        if sections['warnings']:
            md += f"## 注意事項\n\n"
            for warning in sections['warnings']:
                md += f"- {warning}\n"
        
        return md


def main():
    """使用例"""
    # 提供されたデータ（ドキュメントから取得）
    sample_text = """
基本情報
生年月日	1982年（壬戌） 2月 25日 月齢 1.30　男性

判定
		
	判定は、命式表に現れる顕著な特性のうち、より確実なものを示したものです。本判定では、より確実なものとするために、さまざまな視点から判定を行なっており、そのため判定文の中に矛盾する表現が現れる場合があります。例）穏やかな性格と記されている行と、激しい性格と記されている行が存在するなど。こういう場合は、互いを打ち消しあっていますので、より強い方の特性を弱めて解釈して下さい。	
		

　職業的には、専門知識、技術、制作、職人、技芸芸術、マニアック、オタク的な職業適性を持つ。
　物事を実直正確に拘わりを持って、信用と真面目さを基調に処理する人。
　研究、分析、解析等、物事を忍耐強く行う人。
    """
    
    parser = TengelDataParser(sample_text)
    structured_md = parser.generate_structured_markdown()
    
    print(structured_md)


if __name__ == '__main__':
    main()
