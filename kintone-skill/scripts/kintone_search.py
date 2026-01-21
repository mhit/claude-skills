#!/usr/bin/env python3
"""KINTONE 検索クエリビルダーモジュール"""

import json
from typing import Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class Operator(Enum):
    """比較演算子"""
    EQ = "="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    LIKE = "like"
    NOT_LIKE = "not like"
    IN = "in"
    NOT_IN = "not in"


@dataclass
class Condition:
    """検索条件"""
    field: str
    operator: Operator
    value: Any

    def to_query(self) -> str:
        """クエリ文字列に変換"""
        if self.operator == Operator.IN:
            values = ", ".join(f'"{v}"' for v in self.value)
            return f'{self.field} in ({values})'
        elif self.operator == Operator.NOT_IN:
            values = ", ".join(f'"{v}"' for v in self.value)
            return f'{self.field} not in ({values})'
        elif self.operator in (Operator.LIKE, Operator.NOT_LIKE):
            return f'{self.field} {self.operator.value} "{self.value}"'
        elif isinstance(self.value, str):
            return f'{self.field} {self.operator.value} "{self.value}"'
        else:
            return f'{self.field} {self.operator.value} {self.value}'


class QueryBuilder:
    """KINTONE 検索クエリビルダー"""

    def __init__(self):
        self.conditions: list[tuple[str, Condition]] = []  # (connector, condition)
        self._order_by: list[tuple[str, str]] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

    def where(self, field: str, operator: Union[str, Operator], value: Any) -> "QueryBuilder":
        """検索条件を追加"""
        if isinstance(operator, str):
            operator = Operator(operator)
        condition = Condition(field, operator, value)
        connector = "and" if self.conditions else ""
        self.conditions.append((connector, condition))
        return self

    def and_where(self, field: str, operator: Union[str, Operator], value: Any) -> "QueryBuilder":
        """AND 条件を追加"""
        if isinstance(operator, str):
            operator = Operator(operator)
        condition = Condition(field, operator, value)
        self.conditions.append(("and", condition))
        return self

    def or_where(self, field: str, operator: Union[str, Operator], value: Any) -> "QueryBuilder":
        """OR 条件を追加"""
        if isinstance(operator, str):
            operator = Operator(operator)
        condition = Condition(field, operator, value)
        self.conditions.append(("or", condition))
        return self

    def equals(self, field: str, value: Any) -> "QueryBuilder":
        """等価条件（ショートカット）"""
        return self.where(field, Operator.EQ, value)

    def contains(self, field: str, value: str) -> "QueryBuilder":
        """部分一致（LIKE）"""
        return self.where(field, Operator.LIKE, value)

    def in_list(self, field: str, values: list) -> "QueryBuilder":
        """リスト内に存在"""
        return self.where(field, Operator.IN, values)

    def order_by(self, field: str, direction: str = "asc") -> "QueryBuilder":
        """ソート条件を追加"""
        self._order_by.append((field, direction.lower()))
        return self

    def limit(self, count: int) -> "QueryBuilder":
        """取得件数制限"""
        self._limit = min(count, 500)  # KINTONE の最大値は 500
        return self

    def offset(self, count: int) -> "QueryBuilder":
        """オフセット"""
        self._offset = count
        return self

    def build(self) -> str:
        """クエリ文字列を生成"""
        parts = []

        # 条件部分
        for i, (connector, condition) in enumerate(self.conditions):
            if i > 0:
                parts.append(connector)
            parts.append(condition.to_query())

        query = " ".join(parts)

        # order by
        if self._order_by:
            order_parts = [f"{field} {direction}" for field, direction in self._order_by]
            query += f" order by {', '.join(order_parts)}"

        # limit
        if self._limit:
            query += f" limit {self._limit}"

        # offset
        if self._offset:
            query += f" offset {self._offset}"

        return query.strip()

    def __str__(self) -> str:
        return self.build()


# ショートカット関数
def query() -> QueryBuilder:
    """新しいクエリビルダーを作成"""
    return QueryBuilder()


def parse_natural_query(text: str, schema: Optional[dict] = None) -> str:
    """
    自然言語風のクエリをKINTONEクエリに変換

    例:
    - "名前が田中" → '名前 = "田中"'
    - "作成日が今日" → '作成日 = TODAY()'
    - "ステータスが完了または進行中" → 'ステータス in ("完了", "進行中")'
    """
    # 基本的なパターンマッチング
    import re

    # 「が」「は」で分割（match.groups() は 0-indexed）
    patterns = [
        (r"(.+?)が(.+?)と(.+)", lambda m: f'{m[0]} in ("{m[1]}", "{m[2]}")'),  # AがBとC
        (r"(.+?)が(.+?)または(.+)", lambda m: f'{m[0]} in ("{m[1]}", "{m[2]}")'),  # AがBまたはC
        (r"(.+?)が今日", lambda m: f'{m[0]} = TODAY()'),  # が今日
        (r"(.+?)が今月", lambda m: f'{m[0]} >= THIS_MONTH()'),  # が今月
        (r"(.+?)が自分", lambda m: f'{m[0]} = LOGINUSER()'),  # が自分
        (r"(.+?)が空でない", lambda m: f'{m[0]} != ""'),  # が空でない（空より先にマッチ）
        (r"(.+?)が空", lambda m: f'{m[0]} = ""'),  # が空
        (r"(.+?)を含む(.+)", lambda m: f'{m[1]} like "{m[0]}"'),  # を含む
        (r"(.+?)が(.+?)以上", lambda m: f'{m[0]} >= "{m[1]}"'),  # 以上
        (r"(.+?)が(.+?)以下", lambda m: f'{m[0]} <= "{m[1]}"'),  # 以下
        (r"(.+?)が(.+?)より大きい", lambda m: f'{m[0]} > "{m[1]}"'),  # より大きい
        (r"(.+?)が(.+?)より小さい", lambda m: f'{m[0]} < "{m[1]}"'),  # より小さい
        (r"(.+?)が(.+?)ではない", lambda m: f'{m[0]} != "{m[1]}"'),  # ではない
        (r"(.+?)が(.+)", lambda m: f'{m[0]} = "{m[1]}"'),  # 基本形（が）
        (r"(.+?)は(.+)", lambda m: f'{m[0]} = "{m[1]}"'),  # 基本形（は）
    ]

    for pattern, converter in patterns:
        match = re.match(pattern, text)
        if match:
            return converter(match.groups())

    # マッチしない場合はそのまま返す（既にクエリ形式の可能性）
    return text


def main():
    import argparse

    parser = argparse.ArgumentParser(description="KINTONE Query Builder")
    parser.add_argument("--natural", "-n", type=str, help="Natural language query")
    parser.add_argument("--demo", action="store_true", help="Show demo queries")

    args = parser.parse_args()

    if args.natural:
        result = parse_natural_query(args.natural)
        print(f"Input: {args.natural}")
        print(f"Query: {result}")

    elif args.demo:
        print("=== Query Builder Demo ===\n")

        # 基本的なクエリ
        q1 = query().equals("ステータス", "完了").order_by("更新日時", "desc").limit(10)
        print(f"1. 完了したレコード（最新10件）:")
        print(f"   {q1}\n")

        # 複合条件
        q2 = (
            query()
            .where("担当者", "=", "田中")
            .and_where("ステータス", "!=", "完了")
            .order_by("期限", "asc")
        )
        print(f"2. 田中さんの未完了タスク（期限順）:")
        print(f"   {q2}\n")

        # LIKE 検索
        q3 = query().contains("プロジェクト", "顧客").limit(50)
        print(f"3. 「顧客」を含むプロジェクト:")
        print(f"   {q3}\n")

        # IN 検索
        q4 = query().in_list("部署", ["営業", "マーケティング", "開発"])
        print(f"4. 特定部署のレコード:")
        print(f"   {q4}\n")

        print("=== Natural Query Demo ===\n")

        natural_queries = [
            "名前が田中",
            "ステータスが完了または進行中",
            "作成日が今日",
            "担当者が自分",
            "メモが空でない",
            "金額が10000以上",
            "タイトルを含む報告",
        ]

        for nq in natural_queries:
            result = parse_natural_query(nq)
            print(f"  \"{nq}\" → {result}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
