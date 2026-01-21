#!/usr/bin/env python3
"""Tests for kintone_search module"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from kintone_search import QueryBuilder, query, parse_natural_query, Operator


class TestQueryBuilder(unittest.TestCase):
    """Tests for QueryBuilder class"""

    def test_simple_equals(self):
        """Test simple equals condition"""
        q = query().equals("ステータス", "完了")
        self.assertEqual(q.build(), 'ステータス = "完了"')

    def test_where_with_operator(self):
        """Test where with operator"""
        q = query().where("金額", ">", 10000)
        self.assertEqual(q.build(), "金額 > 10000")

    def test_where_with_string_operator(self):
        """Test where with string operator"""
        q = query().where("ステータス", "!=", "完了")
        self.assertEqual(q.build(), 'ステータス != "完了"')

    def test_and_condition(self):
        """Test AND condition"""
        q = query().equals("ステータス", "完了").and_where("担当者", "=", "田中")
        self.assertEqual(q.build(), 'ステータス = "完了" and 担当者 = "田中"')

    def test_or_condition(self):
        """Test OR condition"""
        q = query().equals("ステータス", "完了").or_where("ステータス", "=", "進行中")
        self.assertEqual(q.build(), 'ステータス = "完了" or ステータス = "進行中"')

    def test_like_operator(self):
        """Test LIKE operator"""
        q = query().contains("タイトル", "報告")
        self.assertEqual(q.build(), 'タイトル like "報告"')

    def test_in_list(self):
        """Test IN operator"""
        q = query().in_list("部署", ["営業", "開発"])
        self.assertEqual(q.build(), '部署 in ("営業", "開発")')

    def test_order_by(self):
        """Test ORDER BY clause"""
        q = query().equals("ステータス", "完了").order_by("更新日時", "desc")
        self.assertEqual(q.build(), 'ステータス = "完了" order by 更新日時 desc')

    def test_multiple_order_by(self):
        """Test multiple ORDER BY fields"""
        q = query().order_by("更新日時", "desc").order_by("作成日時", "asc")
        self.assertEqual(q.build(), "order by 更新日時 desc, 作成日時 asc")

    def test_limit(self):
        """Test LIMIT clause"""
        q = query().equals("ステータス", "完了").limit(50)
        self.assertEqual(q.build(), 'ステータス = "完了" limit 50')

    def test_limit_max_500(self):
        """Test LIMIT max is 500"""
        q = query().limit(1000)
        self.assertEqual(q.build(), "limit 500")

    def test_offset(self):
        """Test OFFSET clause"""
        q = query().equals("ステータス", "完了").offset(100)
        self.assertEqual(q.build(), 'ステータス = "完了" offset 100')

    def test_full_query(self):
        """Test full query with all clauses"""
        q = (
            query()
            .equals("ステータス", "完了")
            .order_by("更新日時", "desc")
            .limit(10)
            .offset(20)
        )
        expected = 'ステータス = "完了" order by 更新日時 desc limit 10 offset 20'
        self.assertEqual(q.build(), expected)


class TestParseNaturalQuery(unittest.TestCase):
    """Tests for parse_natural_query function"""

    def test_simple_equals(self):
        """Test simple equals pattern"""
        result = parse_natural_query("名前が田中")
        self.assertEqual(result, '名前 = "田中"')

    def test_equals_with_ha(self):
        """Test equals with は particle"""
        result = parse_natural_query("ステータスは完了")
        self.assertEqual(result, 'ステータス = "完了"')

    def test_today(self):
        """Test TODAY() function"""
        result = parse_natural_query("作成日が今日")
        self.assertEqual(result, "作成日 = TODAY()")

    def test_this_month(self):
        """Test THIS_MONTH() function"""
        result = parse_natural_query("作成日が今月")
        self.assertEqual(result, "作成日 >= THIS_MONTH()")

    def test_loginuser(self):
        """Test LOGINUSER() function"""
        result = parse_natural_query("担当者が自分")
        self.assertEqual(result, "担当者 = LOGINUSER()")

    def test_empty(self):
        """Test empty value"""
        result = parse_natural_query("メモが空")
        self.assertEqual(result, 'メモ = ""')

    def test_not_empty(self):
        """Test not empty value"""
        result = parse_natural_query("メモが空でない")
        self.assertEqual(result, 'メモ != ""')

    def test_or_pattern(self):
        """Test OR pattern (AがBまたはC)"""
        result = parse_natural_query("ステータスが完了または進行中")
        self.assertEqual(result, 'ステータス in ("完了", "進行中")')

    def test_and_pattern(self):
        """Test AND pattern (AがBとC)"""
        result = parse_natural_query("カテゴリが営業と開発")
        self.assertEqual(result, 'カテゴリ in ("営業", "開発")')

    def test_greater_equal(self):
        """Test >= pattern"""
        result = parse_natural_query("金額が10000以上")
        self.assertEqual(result, '金額 >= "10000"')

    def test_less_equal(self):
        """Test <= pattern"""
        result = parse_natural_query("金額が5000以下")
        self.assertEqual(result, '金額 <= "5000"')

    def test_greater_than(self):
        """Test > pattern"""
        result = parse_natural_query("金額が10000より大きい")
        self.assertEqual(result, '金額 > "10000"')

    def test_less_than(self):
        """Test < pattern"""
        result = parse_natural_query("金額が5000より小さい")
        self.assertEqual(result, '金額 < "5000"')

    def test_not_equals(self):
        """Test != pattern"""
        result = parse_natural_query("ステータスが完了ではない")
        self.assertEqual(result, 'ステータス != "完了"')

    def test_passthrough_existing_query(self):
        """Test that existing query format passes through"""
        existing_query = 'ステータス = "完了"'
        result = parse_natural_query(existing_query)
        self.assertEqual(result, existing_query)


class TestOperatorEnum(unittest.TestCase):
    """Tests for Operator enum"""

    def test_operator_values(self):
        """Test operator enum values"""
        self.assertEqual(Operator.EQ.value, "=")
        self.assertEqual(Operator.NE.value, "!=")
        self.assertEqual(Operator.GT.value, ">")
        self.assertEqual(Operator.GE.value, ">=")
        self.assertEqual(Operator.LT.value, "<")
        self.assertEqual(Operator.LE.value, "<=")
        self.assertEqual(Operator.LIKE.value, "like")
        self.assertEqual(Operator.NOT_LIKE.value, "not like")
        self.assertEqual(Operator.IN.value, "in")
        self.assertEqual(Operator.NOT_IN.value, "not in")


if __name__ == "__main__":
    unittest.main()
