#!/usr/bin/env python3
"""
天使ネット連携スクリプト

不明な解釈がある場合、天使ネット(tengel)に問い合わせて
プロフェッショナルな解釈を取得し、データベースに反映します。

サイト運営者の許可を得て使用しています。
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import time
import re


class TengelConnector:
    """天使ネット連携クラス"""
    
    def __init__(self):
        self.url = "https://www.dumbonet.com/tengel/"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Fortune-Telling Master Skill)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def fetch_interpretation(self, year: int, month: int, day: int,
                           hour: int = 12, minute: int = 0,
                           gender: str = 'male') -> Optional[Dict]:
        """
        天使ネットから解釈を取得
        
        Args:
            year: 生年（例: 1982）
            month: 生月（1-12）
            day: 生日（1-31）
            hour: 時（0-23、デフォルト12）
            minute: 分（0-59、デフォルト0）
            gender: 性別（'male' or 'female'）
        
        Returns:
            Dict: {
                'meishiki': 命式情報,
                'interpretation': 判定文,
                'raw_html': 生のHTML（デバッグ用）
            }
        """
        # フォームデータを準備
        form_data = {
            'year': str(year),
            'month': str(month),
            'day': str(day),
            'hour': str(hour),
            'minute': str(minute),
            'gender': '1' if gender.lower() == 'male' else '2',
            'submit': '判定'
        }
        
        try:
            print(f"🔍 天使ネットに問い合わせ中: {year}年{month}月{day}日 {hour}:{minute:02d} ({gender})...")
            
            # POSTリクエスト送信
            response = self.session.post(
                self.url,
                data=form_data,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # レスポンスをパース
            result = self._parse_response(response.text)
            
            if result:
                print("✅ 解釈を取得しました！")
                return result
            else:
                print("⚠️ 解釈の抽出に失敗しました")
                return None
                
        except requests.RequestException as e:
            print(f"❌ エラー: {e}")
            return None
    
    def _parse_response(self, html: str) -> Optional[Dict]:
        """HTMLレスポンスをパースして解釈を抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'meishiki': {},
            'interpretation': '',
            'raw_html': html
        }
        
        # 命式表の抽出（テーブルから）
        tables = soup.find_all('table')
        if tables:
            result['meishiki'] = self._extract_meishiki(tables[0])
        
        # 判定文の抽出
        # 通常、判定文は特定のdivやtableの中にある
        # HTMLの構造に応じて調整が必要
        
        # 全テキストを取得して判定セクションを探す
        all_text = soup.get_text()
        
        # 「判定」セクションを探す
        if '判定' in all_text:
            # 判定セクション以降のテキストを抽出
            interpretation_start = all_text.find('判定')
            if interpretation_start != -1:
                interpretation_text = all_text[interpretation_start:]
                
                # 不要な部分を除去（フッターなど）
                interpretation_text = self._clean_text(interpretation_text)
                result['interpretation'] = interpretation_text
        
        return result if result['interpretation'] else None
    
    def _extract_meishiki(self, table) -> Dict:
        """命式表からデータを抽出"""
        meishiki = {
            'year_pillar': None,
            'month_pillar': None,
            'day_pillar': None,
            'hour_pillar': None
        }
        
        # テーブル構造をパース
        rows = table.find_all('tr')
        
        # 実際のHTML構造に応じて調整が必要
        # ここでは基本的な構造を想定
        
        return meishiki
    
    def _clean_text(self, text: str) -> str:
        """テキストをクリーニング"""
        # 余分な空白を除去
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 不要なセクションを除去
        # 例: コピーライト表示など
        if '© 2003-' in text:
            text = text[:text.find('© 2003-')]
        
        return text.strip()
    
    def save_to_database(self, interpretation: str, 
                        star_name: str,
                        db_path: str = 'references/detailed_interpretations.md'):
        """解釈をデータベースに保存"""
        # 既存のデータベースを読み込み
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                existing_db = f.read()
        except FileNotFoundError:
            existing_db = "# 四柱推命 詳細解釈データベース\n\n"
        
        # 新しいエントリを追加
        new_entry = f"\n\n### {star_name} (天使ネットより)\n\n{interpretation}\n"
        
        # 重複チェック
        if star_name not in existing_db:
            with open(db_path, 'a', encoding='utf-8') as f:
                f.write(new_entry)
            print(f"✅ データベースに追加: {star_name}")
        else:
            print(f"ℹ️ 既に存在: {star_name}")


def main():
    """使用例"""
    connector = TengelConnector()
    
    # テストケース: 1982年2月25日 男性
    result = connector.fetch_interpretation(
        year=1982,
        month=2,
        day=25,
        hour=10,
        minute=0,
        gender='male'
    )
    
    if result:
        print("\n=== 取得した解釈 ===")
        print(result['interpretation'][:500])  # 最初の500文字を表示
        print("\n...")
        
        # データベースに保存（例）
        # connector.save_to_database(
        #     result['interpretation'],
        #     '1982年2月25日 男性のケース'
        # )
    else:
        print("解釈の取得に失敗しました")


if __name__ == '__main__':
    main()
