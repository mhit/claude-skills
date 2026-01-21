#!/usr/bin/env python3
"""KINTONE 添付ファイル操作モジュール"""

import json
import os
from pathlib import Path
from typing import Optional

from kintone_config import get_config
from kintone_client import KintoneClient, KintoneResponse


class KintoneFileManager:
    """KINTONE 添付ファイル管理"""

    def __init__(self):
        self.config = get_config()
        self.client = KintoneClient(self.config)
        self.download_dir = self.config.cache_dir / "downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, file_path: str, file_name: Optional[str] = None) -> KintoneResponse:
        """
        ファイルをアップロード

        Returns:
            KintoneResponse with data containing {"fileKey": "..."}
        """
        path = Path(file_path)
        if not path.exists():
            return KintoneResponse(success=False, error=f"File not found: {file_path}")

        name = file_name or path.name
        return self.client.upload_file(str(path), name)

    def download(
        self,
        file_key: str,
        output_path: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        ファイルをダウンロード

        Returns:
            (success, file_path or error_message)
        """
        try:
            content = self.client.download_file(file_key)

            if output_path:
                save_path = Path(output_path)
            elif file_name:
                save_path = self.download_dir / file_name
            else:
                save_path = self.download_dir / f"file_{file_key[:8]}"

            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, "wb") as f:
                f.write(content)

            return True, str(save_path)

        except Exception as e:
            return False, str(e)

    def get_file_info_from_record(
        self,
        app_id: int,
        record_id: int,
        field_code: str,
    ) -> list[dict]:
        """
        レコードから添付ファイル情報を取得

        Returns:
            List of file info dicts with keys: fileKey, name, contentType, size
        """
        response = self.client.get_record(app_id, record_id)
        if not response.success:
            return []

        record = response.data.get("record", {})
        field = record.get(field_code, {})
        value = field.get("value", [])

        return value if isinstance(value, list) else []

    def download_from_record(
        self,
        app_id: int,
        record_id: int,
        field_code: str,
        output_dir: Optional[str] = None,
    ) -> list[tuple[str, str]]:
        """
        レコードの添付ファイルをすべてダウンロード

        Returns:
            List of (file_name, saved_path) tuples
        """
        files = self.get_file_info_from_record(app_id, record_id, field_code)
        results = []

        out_dir = Path(output_dir) if output_dir else self.download_dir

        for file_info in files:
            file_key = file_info.get("fileKey")
            file_name = file_info.get("name", f"file_{file_key[:8]}")

            success, result = self.download(file_key, str(out_dir / file_name))
            if success:
                results.append((file_name, result))
            else:
                print(f"Warning: Failed to download {file_name}: {result}")

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="KINTONE File Operations")
    parser.add_argument(
        "command",
        choices=["upload", "download", "list"],
        help="File operation command",
    )
    parser.add_argument("--file", "-f", type=str, help="File path (for upload)")
    parser.add_argument("--key", "-k", type=str, help="File key (for download)")
    parser.add_argument("--output", "-o", type=str, help="Output path")
    parser.add_argument("--app", "-a", type=int, help="App ID (for list)")
    parser.add_argument("--record", "-r", type=int, help="Record ID (for list)")
    parser.add_argument("--field", type=str, help="Field code (for list)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    manager = KintoneFileManager()

    if args.command == "upload":
        if not args.file:
            print("Error: --file is required for 'upload' command")
            return

        response = manager.upload(args.file)

        if args.json:
            if response.success:
                print(json.dumps(response.data, indent=2))
            else:
                print(json.dumps({"error": response.error}, indent=2))
        else:
            if response.success:
                print(f"✅ Upload successful")
                print(f"   File Key: {response.data['fileKey']}")
                print()
                print("📝 To attach this file to a record, use:")
                print(f'   {{"フィールドコード": [{{"fileKey": "{response.data["fileKey"]}"}}]}}')
            else:
                print(f"❌ Upload failed: {response.error}")

    elif args.command == "download":
        if not args.key:
            print("Error: --key is required for 'download' command")
            return

        success, result = manager.download(args.key, args.output)

        if args.json:
            print(json.dumps({
                "success": success,
                "path" if success else "error": result,
            }, indent=2))
        else:
            if success:
                print(f"✅ Download successful")
                print(f"   Saved to: {result}")
            else:
                print(f"❌ Download failed: {result}")

    elif args.command == "list":
        if not all([args.app, args.record, args.field]):
            print("Error: --app, --record, and --field are required for 'list' command")
            return

        files = manager.get_file_info_from_record(args.app, args.record, args.field)

        if args.json:
            print(json.dumps(files, ensure_ascii=False, indent=2))
        else:
            if files:
                print(f"📎 Attachments in App {args.app}, Record {args.record}, Field '{args.field}':")
                print("-" * 60)
                for f in files:
                    size_kb = int(f.get("size", 0)) / 1024
                    print(f"  📄 {f.get('name')}")
                    print(f"     Key: {f.get('fileKey')}")
                    print(f"     Type: {f.get('contentType')}")
                    print(f"     Size: {size_kb:.1f} KB")
                    print()
            else:
                print("No attachments found")


if __name__ == "__main__":
    main()
