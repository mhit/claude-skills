#!/usr/bin/env python3
"""
トランスクリプト解析スクリプト
音声トランスクリプトを解析し、構造化されたデータを抽出する
"""

import re
import json
import sys
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict


class TranscriptAnalyzer:
    """トランスクリプトを解析し、構造化データを生成するクラス"""
    
    def __init__(self, transcript_text: str):
        self.text = transcript_text
        self.lines = transcript_text.strip().split('\n')
        self.format_type = self._detect_format()
        self.parsed_data = self._parse_transcript()
        
    def _detect_format(self) -> str:
        """トランスクリプトの形式を検出"""
        # パターン1: [00:00 - 00:06] 形式
        pattern1 = r'\[\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}\]'
        # パターン2: 0:03 | Me 形式
        pattern2 = r'^\d{1,2}:\d{2}\s*\|\s*\w+'
        # パターン3: タイムスタンプなし
        
        has_pattern1 = bool(re.search(pattern1, self.text[:500]))
        has_pattern2 = bool(re.search(pattern2, self.text[:500], re.MULTILINE))
        
        if has_pattern1:
            return "timestamp_range"
        elif has_pattern2:
            return "timestamp_speaker"
        else:
            return "plain_text"
    
    def _parse_transcript(self) -> List[Dict]:
        """トランスクリプトを解析して構造化"""
        if self.format_type == "timestamp_range":
            return self._parse_timestamp_range()
        elif self.format_type == "timestamp_speaker":
            return self._parse_timestamp_speaker()
        else:
            return self._parse_plain_text()
    
    def _parse_timestamp_range(self) -> List[Dict]:
        """[00:00 - 00:06]形式のパース"""
        pattern = r'\[(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\]\s*(.+)'
        entries = []
        
        for line in self.lines:
            match = re.match(pattern, line.strip())
            if match:
                start_time, end_time, text = match.groups()
                entries.append({
                    'start': start_time,
                    'end': end_time,
                    'speaker': 'Unknown',
                    'text': text.strip()
                })
        
        return entries
    
    def _parse_timestamp_speaker(self) -> List[Dict]:
        """0:03 | Me 形式のパース"""
        entries = []
        current_entry = None
        
        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            # タイムスタンプと話者のパターン
            match = re.match(r'^(\d{1,2}:\d{2})\s*\|\s*(.+)', line)
            
            if match:
                # 前のエントリがあれば保存
                if current_entry:
                    entries.append(current_entry)
                
                timestamp, speaker = match.groups()
                current_entry = {
                    'start': timestamp,
                    'speaker': speaker.strip(),
                    'text': ''
                }
            elif current_entry and line:
                # 現在のエントリにテキストを追加
                if current_entry['text']:
                    current_entry['text'] += ' ' + line
                else:
                    current_entry['text'] = line
            
            i += 1
        
        # 最後のエントリを保存
        if current_entry:
            entries.append(current_entry)
        
        return entries
    
    def _parse_plain_text(self) -> List[Dict]:
        """プレーンテキストのパース(段落ベース)"""
        paragraphs = self.text.split('\n\n')
        entries = []
        
        for i, para in enumerate(paragraphs):
            if para.strip():
                entries.append({
                    'segment': i + 1,
                    'speaker': 'Unknown',
                    'text': para.strip()
                })
        
        return entries
    
    def extract_entities(self) -> Dict[str, List[str]]:
        """固有名詞・重要語句を抽出"""
        full_text = ' '.join([entry.get('text', '') for entry in self.parsed_data])
        
        # 人名パターン(日本語)
        person_pattern = r'([ぁ-ん]{2,4}(?:さん|様|先生|社長|部長|課長|氏|君|殿))'
        persons = re.findall(person_pattern, full_text)
        
        # 会社名・組織名パターン
        company_pattern = r'([ァ-ヴー]{2,}(?:株式会社|会社|コーポレーション|グループ|Japan|Inc\.|Co\.))'
        companies = re.findall(company_pattern, full_text)
        
        # 製品・ブランド名(カタカナ3文字以上)
        product_pattern = r'([ァ-ヴー]{3,})'
        products_raw = re.findall(product_pattern, full_text)
        products = [p for p in products_raw if len(p) >= 3 and p not in companies]
        
        # 英数字混在の固有名詞
        alpha_pattern = r'\b([A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*)\b'
        alpha_names = re.findall(alpha_pattern, full_text)
        
        # 頻度でフィルタリング
        person_counter = Counter(persons)
        company_counter = Counter(companies)
        product_counter = Counter(products)
        alpha_counter = Counter(alpha_names)
        
        return {
            'persons': [name for name, count in person_counter.most_common(20) if count >= 2],
            'companies': [name for name, count in company_counter.most_common(10)],
            'products': [name for name, count in product_counter.most_common(15) if count >= 2],
            'other_names': [name for name, count in alpha_counter.most_common(15) if count >= 2 and len(name) > 2]
        }
    
    def classify_meeting_type(self) -> Dict[str, any]:
        """会議の種類を分類"""
        full_text = ' '.join([entry.get('text', '') for entry in self.parsed_data])
        
        keywords = {
            'strategic': ['戦略', 'ビジョン', 'ミッション', '方針', '目標', '計画', 'KPI', 'OKR'],
            'brainstorming': ['アイデア', 'ブレスト', '意見', '提案', '考えてみたい', '可能性'],
            'status_update': ['進捗', '状況', 'ステータス', '報告', '共有', '更新'],
            'problem_solving': ['課題', '問題', '解決', '対策', '改善', 'トラブル', 'リスク'],
            'client_meeting': ['お客様', 'クライアント', '顧客', '提案', '契約', '商談'],
            'interview': ['採用', '面接', '求職', '応募', '志望', '経験'],
            'review': ['レビュー', '振り返り', '評価', 'フィードバック', '反省'],
            'product_discussion': ['製品', 'プロダクト', '機能', '仕様', '開発', 'リリース']
        }
        
        scores = {}
        for category, words in keywords.items():
            score = sum(full_text.count(word) for word in words)
            scores[category] = score
        
        # 上位3つの分類を特定
        top_categories = sorted(scores.items(), key=lambda x: x[-1], reverse=True)[:3]
        primary_type = top_categories[0][0] if top_categories[0][1] > 0 else 'general'
        
        return {
            'primary_type': primary_type,
            'scores': dict(top_categories),
            'is_formal': '御社' in full_text or '貴社' in full_text or '弊社' in full_text
        }
    
    def extract_action_items(self) -> List[Dict]:
        """TODO・アクションアイテムを抽出"""
        action_patterns = [
            r'([^。]+(?:します|やります|お願いします|確認します|検討します|対応します))',
            r'([^。]+(?:してください|お願い|確認|検討|対応)(?:してください|ください|願います))',
            r'TODO[：:]\s*([^。\n]+)',
            r'・([^。\n]+(?:する|やる|行う))'
        ]
        
        action_items = []
        full_text = ' '.join([entry.get('text', '') for entry in self.parsed_data])
        
        for pattern in action_patterns:
            matches = re.findall(pattern, full_text)
            for match in matches:
                if len(match) > 10 and len(match) < 200:
                    action_items.append({
                        'text': match.strip(),
                        'priority': 'normal'
                    })
        
        # 重複を除去
        seen = set()
        unique_items = []
        for item in action_items:
            if item['text'] not in seen:
                seen.add(item['text'])
                unique_items.append(item)
        
        return unique_items[:20]  # 上位20件
    
    def extract_key_topics(self) -> List[Dict]:
        """主要トピックを抽出"""
        full_text = ' '.join([entry.get('text', '') for entry in self.parsed_data])
        
        # 文を分割
        sentences = re.split(r'[。\n]', full_text)
        
        # 重要と思われる文を抽出(質問、決定事項など)
        important_patterns = [
            r'([^。]{10,}(?:\?|ですか|でしょうか))',  # 質問
            r'([^。]{10,}(?:決定|決まり|方針|することになり))',  # 決定事項
            r'([^。]{10,}(?:重要|大切|必要|ポイント))',  # 重要事項
        ]
        
        key_topics = []
        for pattern in important_patterns:
            matches = re.findall(pattern, full_text)
            key_topics.extend(matches)
        
        return [{'topic': topic.strip()} for topic in key_topics[:15]]
    
    def get_summary_statistics(self) -> Dict:
        """統計情報を取得"""
        total_chars = sum(len(entry.get('text', '')) for entry in self.parsed_data)
        speakers = set(entry.get('speaker', 'Unknown') for entry in self.parsed_data)
        
        # 話者別の発言量
        speaker_stats = defaultdict(int)
        for entry in self.parsed_data:
            speaker = entry.get('speaker', 'Unknown')
            text = entry.get('text', '')
            speaker_stats[speaker] += len(text)
        
        return {
            'total_entries': len(self.parsed_data),
            'total_characters': total_chars,
            'unique_speakers': len(speakers),
            'speaker_list': list(speakers),
            'speaker_contribution': dict(speaker_stats),
            'format_type': self.format_type
        }
    
    def to_json(self) -> str:
        """すべての分析結果をJSON形式で出力"""
        result = {
            'statistics': self.get_summary_statistics(),
            'meeting_classification': self.classify_meeting_type(),
            'entities': self.extract_entities(),
            'action_items': self.extract_action_items(),
            'key_topics': self.extract_key_topics(),
            'parsed_entries': self.parsed_data
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_transcript.py <transcript_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        analyzer = TranscriptAnalyzer(transcript)
        print(analyzer.to_json())
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
