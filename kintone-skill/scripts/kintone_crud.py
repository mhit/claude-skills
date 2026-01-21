#!/usr/bin/env python3
"""KINTONE CRUD 操作モジュール"""

import json
import sys
from typing import Optional, Any, Iterator

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

    def search_all(
        self,
        app_id: int,
        query: str = "",
        fields: Optional[list[str]] = None,
        batch_size: int = 500,
    ) -> Iterator[dict]:
        """全レコードをイテレーターで取得（500件超対応）

        カーソル API を使用して、制限なくレコードを取得します。

        Args:
            app_id: アプリ ID
            query: 検索条件（limit/offset は使用不可）
            fields: 取得フィールド
            batch_size: 1回の取得件数（1-500）

        Yields:
            dict: レコード
        """
        cursor = self.client.create_cursor(app_id, query, fields, batch_size)
        if not cursor.success:
            raise RuntimeError(f"Failed to create cursor: {cursor.error}")

        cursor_id = cursor.data["id"]
        try:
            while True:
                result = self.client.get_cursor_records(cursor_id)
                if not result.success:
                    raise RuntimeError(f"Failed to get cursor records: {result.error}")

                for record in result.data.get("records", []):
                    yield record

                if not result.data.get("next", False):
                    break
        finally:
            self.client.delete_cursor(cursor_id)

    def add(self, app_id: int, record: dict) -> KintoneResponse:
        """レコードを1件追加"""
        # フィールド値を KINTONE 形式に変換
        formatted_record = self._format_record(record)
        return self.client.add_record(app_id, formatted_record)

    def add_many(
        self,
        app_id: int,
        records: list[dict],
        chunk_size: int = 100,
    ) -> list[KintoneResponse]:
        """レコードを複数件追加（自動チャンク分割）

        100件を超える場合、自動的に分割して実行します。

        Args:
            app_id: アプリ ID
            records: レコードリスト
            chunk_size: 1回の追加件数（最大100）

        Returns:
            list[KintoneResponse]: 各チャンクのレスポンス
        """
        formatted_records = [self._format_record(r) for r in records]
        chunk_size = min(chunk_size, 100)

        if len(formatted_records) <= chunk_size:
            return [self.client.add_records(app_id, formatted_records)]

        results = []
        for i in range(0, len(formatted_records), chunk_size):
            chunk = formatted_records[i : i + chunk_size]
            result = self.client.add_records(app_id, chunk)
            results.append(result)
            if not result.success:
                break
        return results

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

    def update_many(
        self,
        app_id: int,
        records: list[dict],
        chunk_size: int = 100,
    ) -> list[KintoneResponse]:
        """レコードを複数件更新（自動チャンク分割）

        100件を超える場合、自動的に分割して実行します。
        各レコードに id または $id フィールドが必要です。

        Args:
            app_id: アプリ ID
            records: レコードリスト（各レコードに id が必要）
            chunk_size: 1回の更新件数（最大100）

        Returns:
            list[KintoneResponse]: 各チャンクのレスポンス
        """
        formatted_records = []
        for r in records:
            r_copy = dict(r)
            record_id = r_copy.pop("id", None) or r_copy.pop("$id", None)
            if not record_id:
                raise ValueError("Each record must have 'id' field")
            formatted_records.append({
                "id": record_id,
                "record": self._format_record(r_copy),
            })

        chunk_size = min(chunk_size, 100)

        if len(formatted_records) <= chunk_size:
            return [self.client.update_records(app_id, formatted_records)]

        results = []
        for i in range(0, len(formatted_records), chunk_size):
            chunk = formatted_records[i : i + chunk_size]
            result = self.client.update_records(app_id, chunk)
            results.append(result)
            if not result.success:
                break
        return results

    def delete(self, app_id: int, record_ids: list[int]) -> KintoneResponse:
        """レコードを削除"""
        return self.client.delete_records(app_id, record_ids)

    # === ステータス操作 ===

    def change_status(
        self,
        app_id: int,
        record_id: int,
        action: str,
        assignee: Optional[str] = None,
    ) -> KintoneResponse:
        """レコードのステータスを更新（ワークフロー）

        Args:
            app_id: アプリ ID
            record_id: レコード ID
            action: アクション名
            assignee: 次の作業者（ログイン名）
        """
        return self.client.update_status(app_id, record_id, action, assignee)

    # === コメント操作 ===

    def add_comment(
        self,
        app_id: int,
        record_id: int,
        text: str,
        mentions: Optional[list[str]] = None,
    ) -> KintoneResponse:
        """レコードにコメントを追加

        Args:
            app_id: アプリ ID
            record_id: レコード ID
            text: コメント本文
            mentions: メンション対象のユーザー名リスト（@なし）
        """
        mention_list = None
        if mentions:
            mention_list = [{"code": m, "type": "USER"} for m in mentions]
        return self.client.add_comment(app_id, record_id, text, mention_list)

    def get_comments(
        self,
        app_id: int,
        record_id: int,
        order: str = "desc",
        limit: int = 10,
    ) -> KintoneResponse:
        """レコードのコメントを取得"""
        return self.client.get_comments(app_id, record_id, order, 0, limit)

    def delete_comment(
        self,
        app_id: int,
        record_id: int,
        comment_id: int,
    ) -> KintoneResponse:
        """コメントを削除"""
        return self.client.delete_comment(app_id, record_id, comment_id)

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


def print_records_iterator(records: Iterator[dict], as_json: bool = False, limit: int = 0):
    """イテレーターからレコードを表示"""
    count = 0
    all_records = []
    for record in records:
        count += 1
        if as_json:
            all_records.append(record)
        else:
            if count <= 5:
                print(f"\n--- Record {count} ---")
                print(json.dumps(record, ensure_ascii=False, indent=2))
        if limit and count >= limit:
            break

    if as_json:
        print(json.dumps(all_records, ensure_ascii=False, indent=2))
    else:
        print(f"\n✅ Total: {count} 件")
        if count > 5:
            print(f"(showing first 5 records)")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="KINTONE CRUD Operations")
    parser.add_argument(
        "command",
        choices=["get", "search", "add", "update", "delete", "status", "comment", "apps"],
        help="CRUD command",
    )
    parser.add_argument("--app", "-a", type=int, help="App ID")
    parser.add_argument("--id", "-i", type=int, help="Record ID (for get/update/status/comment)")
    parser.add_argument("--ids", type=str, help="Record IDs comma-separated (for delete)")
    parser.add_argument("--query", "-q", type=str, default="", help="Search query")
    parser.add_argument("--data", "-d", type=str, help="Record data as JSON")
    parser.add_argument("--file", "-f", type=str, help="Record data from JSON file")
    parser.add_argument("--limit", type=int, default=100, help="Search limit")
    parser.add_argument("--offset", type=int, default=0, help="Search offset")
    parser.add_argument("--all", action="store_true", help="Search all records using cursor API")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    # Status options
    parser.add_argument("--action", type=str, help="Status action name")
    parser.add_argument("--assignee", type=str, help="Next assignee (login name)")
    # Comment options
    parser.add_argument("--comment-action", type=str, choices=["add", "list", "delete"], help="Comment action")
    parser.add_argument("--text", "-t", type=str, help="Comment text")
    parser.add_argument("--comment-id", type=int, help="Comment ID (for delete)")
    # Apps options
    parser.add_argument("--name", type=str, help="App name filter (for apps)")
    parser.add_argument("--app-ids", type=str, help="App IDs comma-separated (for apps)")

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

    # Validate app_id for commands that require it
    if args.command != "apps" and not args.app:
        print(f"Error: --app is required for '{args.command}' command")
        sys.exit(1)

    if args.command == "apps":
        app_ids = None
        if args.app_ids:
            app_ids = [int(x.strip()) for x in args.app_ids.split(",")]
        response = crud.client.get_apps(ids=app_ids, name=args.name, limit=args.limit, offset=args.offset)
        print_response(response, args.json)

    elif args.command == "get":
        if not args.id:
            print("Error: --id is required for 'get' command")
            sys.exit(1)
        response = crud.get(args.app, args.id)
        print_response(response, args.json)

    elif args.command == "search":
        if args.all:
            # カーソル API を使用した全件取得
            try:
                records = crud.search_all(args.app, args.query)
                print_records_iterator(records, args.json, args.limit if args.limit != 100 else 0)
            except RuntimeError as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
        else:
            response = crud.search(
                args.app,
                args.query,
                limit=args.limit,
                offset=args.offset,
            )
            print_response(response, args.json)

    elif args.command == "add":
        if not record_data:
            print("Error: --data or --file is required for 'add' command")
            sys.exit(1)
        if isinstance(record_data, list):
            responses = crud.add_many(args.app, record_data)
            for i, resp in enumerate(responses, 1):
                print(f"Chunk {i}: ", end="")
                print_response(resp, args.json)
        else:
            response = crud.add(args.app, record_data)
            print_response(response, args.json)

    elif args.command == "update":
        if not args.id:
            print("Error: --id is required for 'update' command")
            sys.exit(1)
        if not record_data:
            print("Error: --data or --file is required for 'update' command")
            sys.exit(1)
        response = crud.update(args.app, args.id, record_data)
        print_response(response, args.json)

    elif args.command == "delete":
        if not args.ids:
            print("Error: --ids is required for 'delete' command")
            sys.exit(1)
        record_ids = [int(x.strip()) for x in args.ids.split(",")]
        response = crud.delete(args.app, record_ids)
        print_response(response, args.json)

    elif args.command == "status":
        if not args.id:
            print("Error: --id is required for 'status' command")
            sys.exit(1)
        if not args.action:
            print("Error: --action is required for 'status' command")
            sys.exit(1)
        response = crud.change_status(args.app, args.id, args.action, args.assignee)
        print_response(response, args.json)

    elif args.command == "comment":
        if not args.id:
            print("Error: --id is required for 'comment' command")
            sys.exit(1)
        if not args.comment_action:
            print("Error: --comment-action is required for 'comment' command")
            sys.exit(1)

        if args.comment_action == "add":
            if not args.text:
                print("Error: --text is required for 'comment add'")
                sys.exit(1)
            response = crud.add_comment(args.app, args.id, args.text)
            print_response(response, args.json)
        elif args.comment_action == "list":
            response = crud.get_comments(args.app, args.id)
            print_response(response, args.json)
        elif args.comment_action == "delete":
            if not args.comment_id:
                print("Error: --comment-id is required for 'comment delete'")
                sys.exit(1)
            response = crud.delete_comment(args.app, args.id, args.comment_id)
            print_response(response, args.json)


if __name__ == "__main__":
    main()
