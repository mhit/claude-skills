#!/usr/bin/env python3
"""KINTONE スキーマ管理・キャッシュモジュール"""

import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

from kintone_config import get_config, KintoneConfig
from kintone_client import KintoneClient


@dataclass
class FieldInfo:
    """フィールド情報"""
    code: str
    label: str
    type: str
    required: bool = False
    unique: bool = False
    options: Optional[dict] = None  # ドロップダウンなどの選択肢


@dataclass
class AppSchema:
    """アプリスキーマ"""
    app_id: int
    app_name: str
    fields: dict[str, FieldInfo]
    cached_at: float  # Unix timestamp

    def to_dict(self) -> dict:
        """辞書に変換"""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "fields": {
                code: asdict(field) for code, field in self.fields.items()
            },
            "cached_at": self.cached_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppSchema":
        """辞書から生成"""
        fields = {
            code: FieldInfo(**field_data)
            for code, field_data in data["fields"].items()
        }
        return cls(
            app_id=data["app_id"],
            app_name=data["app_name"],
            fields=fields,
            cached_at=data["cached_at"],
        )


class SchemaManager:
    """スキーマキャッシュ管理"""

    def __init__(self, config: Optional[KintoneConfig] = None):
        self.config = config or get_config()
        self.client = KintoneClient(self.config)
        self.schema_dir = self.config.ensure_cache_dir() / "schemas"
        self.schema_dir.mkdir(exist_ok=True)

    def _cache_path(self, app_id: int) -> Path:
        """キャッシュファイルパス"""
        return self.schema_dir / f"app_{app_id}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """キャッシュが有効か判定"""
        if not cache_path.exists():
            return False

        with open(cache_path) as f:
            data = json.load(f)

        cached_at = data.get("cached_at", 0)
        return (time.time() - cached_at) < self.config.cache_ttl

    def get_schema(self, app_id: int, refresh: bool = False) -> Optional[AppSchema]:
        """スキーマを取得（キャッシュ優先）"""
        cache_path = self._cache_path(app_id)

        # キャッシュが有効で refresh でなければキャッシュを返す
        if not refresh and self._is_cache_valid(cache_path):
            with open(cache_path) as f:
                return AppSchema.from_dict(json.load(f))

        # API からスキーマを取得
        schema = self._fetch_schema(app_id)
        if schema:
            # キャッシュに保存
            with open(cache_path, "w") as f:
                json.dump(schema.to_dict(), f, ensure_ascii=False, indent=2)

        return schema

    def _fetch_schema(self, app_id: int) -> Optional[AppSchema]:
        """API からスキーマを取得"""
        # アプリ情報取得
        app_response = self.client.get_app(app_id)
        if not app_response.success:
            print(f"Error getting app info: {app_response.error}")
            return None

        app_name = app_response.data.get("name", f"App {app_id}")

        # フィールド定義取得
        fields_response = self.client.get_form_fields(app_id)
        if not fields_response.success:
            print(f"Error getting fields: {fields_response.error}")
            return None

        fields = {}
        for code, field_data in fields_response.data.get("properties", {}).items():
            fields[code] = FieldInfo(
                code=code,
                label=field_data.get("label", code),
                type=field_data.get("type", "UNKNOWN"),
                required=field_data.get("required", False),
                unique=field_data.get("unique", False),
                options=field_data.get("options"),
            )

        return AppSchema(
            app_id=app_id,
            app_name=app_name,
            fields=fields,
            cached_at=time.time(),
        )

    def list_cached_schemas(self) -> list[tuple[int, str, float]]:
        """キャッシュされているスキーマ一覧"""
        result = []
        for cache_file in self.schema_dir.glob("app_*.json"):
            with open(cache_file) as f:
                data = json.load(f)
                result.append((
                    data["app_id"],
                    data["app_name"],
                    data["cached_at"],
                ))
        return result

    def clear_cache(self, app_id: Optional[int] = None):
        """キャッシュをクリア"""
        if app_id:
            cache_path = self._cache_path(app_id)
            if cache_path.exists():
                cache_path.unlink()
        else:
            for cache_file in self.schema_dir.glob("app_*.json"):
                cache_file.unlink()

    def print_schema(self, app_id: int, refresh: bool = False):
        """スキーマを整形して表示"""
        schema = self.get_schema(app_id, refresh)
        if not schema:
            print(f"Failed to get schema for app {app_id}")
            return

        print(f"\n📋 App: {schema.app_name} (ID: {schema.app_id})")
        print("=" * 60)
        print(f"{'フィールドコード':<20} {'ラベル':<20} {'型':<15} {'必須'}")
        print("-" * 60)

        for code, field in sorted(schema.fields.items()):
            required = "✓" if field.required else ""
            print(f"{code:<20} {field.label:<20} {field.type:<15} {required}")

        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="KINTONE Schema Manager")
    parser.add_argument("command", choices=["get", "list", "clear", "refresh"])
    parser.add_argument("--app", "-a", type=int, help="App ID")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    manager = SchemaManager()

    if args.command == "get":
        if not args.app:
            print("Error: --app is required for 'get' command")
            return
        if args.json:
            schema = manager.get_schema(args.app)
            if schema:
                print(json.dumps(schema.to_dict(), ensure_ascii=False, indent=2))
        else:
            manager.print_schema(args.app)

    elif args.command == "list":
        schemas = manager.list_cached_schemas()
        if args.json:
            print(json.dumps([
                {"app_id": s[0], "app_name": s[1], "cached_at": s[2]}
                for s in schemas
            ], ensure_ascii=False, indent=2))
        else:
            print("\n📚 Cached Schemas:")
            print("-" * 50)
            for app_id, app_name, cached_at in schemas:
                import datetime
                cached_time = datetime.datetime.fromtimestamp(cached_at)
                print(f"  App {app_id}: {app_name} (cached: {cached_time})")

    elif args.command == "clear":
        manager.clear_cache(args.app)
        print("Cache cleared")

    elif args.command == "refresh":
        if not args.app:
            print("Error: --app is required for 'refresh' command")
            return
        manager.print_schema(args.app, refresh=True)
        print("Schema refreshed")


if __name__ == "__main__":
    main()
