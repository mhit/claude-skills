#!/usr/bin/env python3
"""KINTONE CRUD 操作モジュール"""

import json
import sys
from typing import Optional, Any

from kintone_config import get_config
from kintone_client import KintoneClient, KintoneResponse


class KintoneCRUD:
    """KINTONE CRUD 操作クラス"""

    def __init__(self):
        self.config = get_config()
        self.client = KintoneClient(self.config)

    def get(self, app_id: int, record_id: int) -> KintoneResponse:
        """レコードを1件取得"""
        return self.client.get_record(app_id, record_id)

    def search(
        self,
        app_id: int,
        query: str = "",
        fields: Optional[list[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> KintoneResponse:
        """レコードを検索"""
        # query に limit/offset を追加
        full_query = query
        if limit:
            full_query = f"{full_query} limit {limit}" if full_query else f"limit {limit}"
        if offset:
            full_query = f"{full_query} offset {offset}"

        return self.client.get_records(app_id, full_query.strip(), fields, total_count=True)

    def add(self, app_id: int, record: dict) -> KintoneResponse:
        """レコードを1件追加"""
        # フィールド値を KINTONE 形式に変換
        formatted_record = self._format_record(record)
        return self.client.add_record(app_id, formatted_record)

    def add_many(self, app_id: int, records: list[dict]) -> KintoneResponse:
        """レコードを複数件追加"""
        formatted_records = [self._format_record(r) for r in records]
        return self.client.add_records(app_id, formatted_records)

    def update(
        self,
        app_id: int,
        record_id: int,
        record: dict,
        revision: Optional[int] = None,
    ) -> KintoneResponse:
        """レコードを1件更新"""
        formatted_record = self._format_record(record)
        return self.client.update_record(app_id, record_id, formatted_record, revision)

    def update_many(self, app_id: int, records: list[dict]) -> KintoneResponse:
        """レコードを複数件更新（各レコードに id が必要）"""
        formatted_records = []
        for r in records:
            record_id = r.pop("id", None) or r.pop("$id", None)
            if not record_id:
                raise ValueError("Each record must have 'id' field")
            formatted_records.append({
                "id": record_id,
                "record": self._format_record(r),
            })
        return self.client.update_records(app_id, formatted_records)

    def delete(self, app_id: int, record_ids: list[int]) -> KintoneResponse:
        """レコードを削除"""
        return self.client.delete_records(app_id, record_ids)

    def _format_record(self, record: dict) -> dict:
        """レコードを KINTONE API 形式に変換"""
        formatted = {}
        for key, value in record.items():
            # 既に KINTONE 形式の場合はそのまま
            if isinstance(value, dict) and "value" in value:
                formatted[key] = value
            else:
                formatted[key] = {"value": value}
        return formatted

    def _unformat_record(self, record: dict) -> dict:
        """KINTONE API 形式から通常の dict に変換"""
        unformatted = {}
        for key, value in record.items():
            if isinstance(value, dict) and "value" in value:
                unformatted[key] = value["value"]
            else:
                unformatted[key] = value
        return unformatted


def print_response(response: KintoneResponse, as_json: bool = False):
    """レスポンスを表示"""
    if as_json:
        if response.success:
            print(json.dumps(response.data, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({
                "error": response.error,
                "error_code": response.error_code,
            }, ensure_ascii=False, indent=2))
    else:
        if response.success:
            print("✅ Success")
            if response.data:
                if "record" in response.data:
                    print("\n📄 Record:")
                    print(json.dumps(response.data["record"], ensure_ascii=False, indent=2))
                elif "records" in response.data:
                    records = response.data["records"]
                    print(f"\n📄 Records: {len(records)} 件")
                    if "totalCount" in response.data:
                        print(f"   Total: {response.data['totalCount']} 件")
                    for i, record in enumerate(records[:5], 1):
                        print(f"\n--- Record {i} ---")
                        print(json.dumps(record, ensure_ascii=False, indent=2))
                    if len(records) > 5:
                        print(f"\n... and {len(records) - 5} more records")
                elif "id" in response.data:
                    print(f"Created record ID: {response.data['id']}")
                elif "ids" in response.data:
                    print(f"Created record IDs: {response.data['ids']}")
                elif "revision" in response.data:
                    print(f"Updated revision: {response.data['revision']}")
                else:
                    print(json.dumps(response.data, ensure_ascii=False, indent=2))
        else:
            print(f"❌ Error: {response.error}")
            if response.error_code:
                print(f"   Code: {response.error_code}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="KINTONE CRUD Operations")
    parser.add_argument(
        "command",
        choices=["get", "search", "add", "update", "delete"],
        help="CRUD command",
    )
    parser.add_argument("--app", "-a", type=int, required=True, help="App ID")
    parser.add_argument("--id", "-i", type=int, help="Record ID (for get/update)")
    parser.add_argument("--ids", type=str, help="Record IDs comma-separated (for delete)")
    parser.add_argument("--query", "-q", type=str, default="", help="Search query")
    parser.add_argument("--data", "-d", type=str, help="Record data as JSON")
    parser.add_argument("--file", "-f", type=str, help="Record data from JSON file")
    parser.add_argument("--limit", type=int, default=100, help="Search limit")
    parser.add_argument("--offset", type=int, default=0, help="Search offset")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    crud = KintoneCRUD()

    # データの読み込み
    record_data = None
    if args.data:
        record_data = json.loads(args.data)
    elif args.file:
        with open(args.file) as f:
            record_data = json.load(f)

    response: KintoneResponse

    if args.command == "get":
        if not args.id:
            print("Error: --id is required for 'get' command")
            sys.exit(1)
        response = crud.get(args.app, args.id)

    elif args.command == "search":
        response = crud.search(
            args.app,
            args.query,
            limit=args.limit,
            offset=args.offset,
        )

    elif args.command == "add":
        if not record_data:
            print("Error: --data or --file is required for 'add' command")
            sys.exit(1)
        if isinstance(record_data, list):
            response = crud.add_many(args.app, record_data)
        else:
            response = crud.add(args.app, record_data)

    elif args.command == "update":
        if not args.id:
            print("Error: --id is required for 'update' command")
            sys.exit(1)
        if not record_data:
            print("Error: --data or --file is required for 'update' command")
            sys.exit(1)
        response = crud.update(args.app, args.id, record_data)

    elif args.command == "delete":
        if not args.ids:
            print("Error: --ids is required for 'delete' command")
            sys.exit(1)
        record_ids = [int(x.strip()) for x in args.ids.split(",")]
        response = crud.delete(args.app, record_ids)

    print_response(response, args.json)


if __name__ == "__main__":
    main()
