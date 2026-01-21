#!/usr/bin/env python3
"""Tests for kintone_schema module"""

import sys
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from kintone_schema import FieldInfo, AppSchema, SchemaManager
from kintone_client import KintoneResponse


class TestFieldInfo(unittest.TestCase):
    """Tests for FieldInfo dataclass"""

    def test_basic_field(self):
        """Test basic field creation"""
        field = FieldInfo(
            code="Title",
            label="タイトル",
            type="SINGLE_LINE_TEXT",
        )
        self.assertEqual(field.code, "Title")
        self.assertEqual(field.label, "タイトル")
        self.assertEqual(field.type, "SINGLE_LINE_TEXT")
        self.assertFalse(field.required)
        self.assertFalse(field.unique)
        self.assertIsNone(field.options)

    def test_field_with_options(self):
        """Test field with dropdown options"""
        field = FieldInfo(
            code="Status",
            label="ステータス",
            type="DROP_DOWN",
            required=True,
            options={"Done": {"label": "完了"}, "WIP": {"label": "作業中"}},
        )
        self.assertTrue(field.required)
        self.assertIsNotNone(field.options)
        self.assertIn("Done", field.options)


class TestAppSchema(unittest.TestCase):
    """Tests for AppSchema dataclass"""

    def test_to_dict(self):
        """Test AppSchema to_dict conversion"""
        schema = AppSchema(
            app_id=123,
            app_name="Test App",
            fields={
                "Title": FieldInfo(
                    code="Title",
                    label="タイトル",
                    type="SINGLE_LINE_TEXT",
                )
            },
            cached_at=1234567890.0,
        )

        result = schema.to_dict()

        self.assertEqual(result["app_id"], 123)
        self.assertEqual(result["app_name"], "Test App")
        self.assertIn("Title", result["fields"])
        self.assertEqual(result["fields"]["Title"]["code"], "Title")
        self.assertEqual(result["cached_at"], 1234567890.0)

    def test_from_dict(self):
        """Test AppSchema from_dict creation"""
        data = {
            "app_id": 456,
            "app_name": "Another App",
            "fields": {
                "Status": {
                    "code": "Status",
                    "label": "状態",
                    "type": "DROP_DOWN",
                    "required": True,
                    "unique": False,
                    "options": None,
                }
            },
            "cached_at": 9876543210.0,
        }

        schema = AppSchema.from_dict(data)

        self.assertEqual(schema.app_id, 456)
        self.assertEqual(schema.app_name, "Another App")
        self.assertIn("Status", schema.fields)
        self.assertEqual(schema.fields["Status"].type, "DROP_DOWN")
        self.assertTrue(schema.fields["Status"].required)

    def test_roundtrip(self):
        """Test to_dict -> from_dict roundtrip"""
        original = AppSchema(
            app_id=789,
            app_name="Roundtrip Test",
            fields={
                "Field1": FieldInfo("Field1", "フィールド1", "TEXT"),
                "Field2": FieldInfo("Field2", "フィールド2", "NUMBER", True, True),
            },
            cached_at=time.time(),
        )

        restored = AppSchema.from_dict(original.to_dict())

        self.assertEqual(restored.app_id, original.app_id)
        self.assertEqual(restored.app_name, original.app_name)
        self.assertEqual(len(restored.fields), len(original.fields))


class TestSchemaManager(unittest.TestCase):
    """Tests for SchemaManager class"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.patcher = patch("kintone_schema.get_config")
        self.mock_config = self.patcher.start()
        self.mock_config.return_value = MagicMock(
            domain="test.cybozu.com",
            api_token="test-token",
            cache_ttl=3600,
            ensure_cache_dir=MagicMock(return_value=Path(self.temp_dir)),
        )

    def tearDown(self):
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("kintone_schema.KintoneClient")
    def test_get_schema_from_api(self, MockClient):
        """Test fetching schema from API"""
        mock_client = MockClient.return_value
        mock_client.get_app.return_value = KintoneResponse(
            success=True,
            data={"name": "Test App"},
        )
        mock_client.get_form_fields.return_value = KintoneResponse(
            success=True,
            data={
                "properties": {
                    "Title": {
                        "label": "タイトル",
                        "type": "SINGLE_LINE_TEXT",
                        "required": True,
                    }
                }
            },
        )

        manager = SchemaManager()
        schema = manager.get_schema(app_id=123, refresh=True)

        self.assertIsNotNone(schema)
        self.assertEqual(schema.app_id, 123)
        self.assertEqual(schema.app_name, "Test App")
        self.assertIn("Title", schema.fields)

    @patch("kintone_schema.KintoneClient")
    def test_get_schema_from_cache(self, MockClient):
        """Test getting schema from cache"""
        mock_client = MockClient.return_value
        mock_client.get_app.return_value = KintoneResponse(
            success=True,
            data={"name": "Cached App"},
        )
        mock_client.get_form_fields.return_value = KintoneResponse(
            success=True,
            data={"properties": {}},
        )

        manager = SchemaManager()

        # First call - fetches from API
        manager.get_schema(app_id=123)
        call_count_1 = mock_client.get_app.call_count

        # Second call - should use cache
        manager.get_schema(app_id=123)
        call_count_2 = mock_client.get_app.call_count

        self.assertEqual(call_count_1, call_count_2)  # No new API call

    @patch("kintone_schema.KintoneClient")
    def test_get_schema_refresh_ignores_cache(self, MockClient):
        """Test refresh=True ignores cache"""
        mock_client = MockClient.return_value
        mock_client.get_app.return_value = KintoneResponse(
            success=True,
            data={"name": "Test App"},
        )
        mock_client.get_form_fields.return_value = KintoneResponse(
            success=True,
            data={"properties": {}},
        )

        manager = SchemaManager()

        # First call
        manager.get_schema(app_id=123)

        # Second call with refresh
        manager.get_schema(app_id=123, refresh=True)

        self.assertEqual(mock_client.get_app.call_count, 2)

    @patch("kintone_schema.KintoneClient")
    def test_get_schema_api_error(self, MockClient):
        """Test handling API error"""
        mock_client = MockClient.return_value
        mock_client.get_app.return_value = KintoneResponse(
            success=False,
            error="Permission denied",
        )

        manager = SchemaManager()
        schema = manager.get_schema(app_id=123)

        self.assertIsNone(schema)

    @patch("kintone_schema.KintoneClient")
    def test_clear_cache_specific_app(self, MockClient):
        """Test clearing cache for specific app"""
        mock_client = MockClient.return_value
        mock_client.get_app.return_value = KintoneResponse(
            success=True,
            data={"name": "Test"},
        )
        mock_client.get_form_fields.return_value = KintoneResponse(
            success=True,
            data={"properties": {}},
        )

        manager = SchemaManager()

        # Create cache
        manager.get_schema(app_id=123)
        cache_path = manager._cache_path(123)
        self.assertTrue(cache_path.exists())

        # Clear cache
        manager.clear_cache(app_id=123)
        self.assertFalse(cache_path.exists())

    @patch("kintone_schema.KintoneClient")
    def test_clear_cache_all(self, MockClient):
        """Test clearing all cache"""
        mock_client = MockClient.return_value
        mock_client.get_app.return_value = KintoneResponse(
            success=True,
            data={"name": "Test"},
        )
        mock_client.get_form_fields.return_value = KintoneResponse(
            success=True,
            data={"properties": {}},
        )

        manager = SchemaManager()

        # Create cache for multiple apps
        manager.get_schema(app_id=123)
        manager.get_schema(app_id=456)

        # Clear all
        manager.clear_cache()

        self.assertEqual(len(list(manager.schema_dir.glob("app_*.json"))), 0)

    @patch("kintone_schema.KintoneClient")
    def test_list_cached_schemas(self, MockClient):
        """Test listing cached schemas"""
        mock_client = MockClient.return_value
        mock_client.get_app.return_value = KintoneResponse(
            success=True,
            data={"name": "Test App"},
        )
        mock_client.get_form_fields.return_value = KintoneResponse(
            success=True,
            data={"properties": {}},
        )

        manager = SchemaManager()
        manager.get_schema(app_id=123)
        manager.get_schema(app_id=456)

        cached = manager.list_cached_schemas()

        self.assertEqual(len(cached), 2)
        app_ids = [c[0] for c in cached]
        self.assertIn(123, app_ids)
        self.assertIn(456, app_ids)


if __name__ == "__main__":
    unittest.main()
