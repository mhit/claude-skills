#!/usr/bin/env python3
"""Tests for extended kintone_crud features (search_all, chunking, status, comment)"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from kintone_crud import KintoneCRUD
from kintone_client import KintoneResponse


class TestSearchAll(unittest.TestCase):
    """Tests for search_all method using Cursor API"""

    def setUp(self):
        self.patcher = patch("kintone_crud.get_config")
        self.mock_config = self.patcher.start()
        self.mock_config.return_value = MagicMock(
            domain="test.cybozu.com",
            api_token="test-token",
        )

    def tearDown(self):
        self.patcher.stop()

    @patch("kintone_crud.KintoneClient")
    def test_search_all_single_batch(self, MockClient):
        """Test search_all with single batch (all records fit in one request)"""
        mock_client = MockClient.return_value
        mock_client.create_cursor.return_value = KintoneResponse(
            success=True,
            data={"id": "cursor-1", "totalCount": "2"},
        )
        mock_client.get_cursor_records.return_value = KintoneResponse(
            success=True,
            data={
                "records": [
                    {"$id": {"value": "1"}},
                    {"$id": {"value": "2"}},
                ],
                "next": False,
            },
        )
        mock_client.delete_cursor.return_value = KintoneResponse(success=True, data={})

        crud = KintoneCRUD()
        records = list(crud.search_all(app_id=123))

        self.assertEqual(len(records), 2)
        mock_client.create_cursor.assert_called_once()
        mock_client.delete_cursor.assert_called_once_with("cursor-1")

    @patch("kintone_crud.KintoneClient")
    def test_search_all_multiple_batches(self, MockClient):
        """Test search_all with multiple batches"""
        mock_client = MockClient.return_value
        mock_client.create_cursor.return_value = KintoneResponse(
            success=True,
            data={"id": "cursor-1", "totalCount": "3"},
        )
        # First call returns 2 records with next=True
        # Second call returns 1 record with next=False
        mock_client.get_cursor_records.side_effect = [
            KintoneResponse(
                success=True,
                data={
                    "records": [{"$id": {"value": "1"}}, {"$id": {"value": "2"}}],
                    "next": True,
                },
            ),
            KintoneResponse(
                success=True,
                data={
                    "records": [{"$id": {"value": "3"}}],
                    "next": False,
                },
            ),
        ]
        mock_client.delete_cursor.return_value = KintoneResponse(success=True, data={})

        crud = KintoneCRUD()
        records = list(crud.search_all(app_id=123))

        self.assertEqual(len(records), 3)
        self.assertEqual(mock_client.get_cursor_records.call_count, 2)

    @patch("kintone_crud.KintoneClient")
    def test_search_all_cursor_creation_fails(self, MockClient):
        """Test search_all raises error when cursor creation fails"""
        mock_client = MockClient.return_value
        mock_client.create_cursor.return_value = KintoneResponse(
            success=False,
            error="Permission denied",
        )

        crud = KintoneCRUD()

        with self.assertRaises(RuntimeError) as ctx:
            list(crud.search_all(app_id=123))

        self.assertIn("Permission denied", str(ctx.exception))

    @patch("kintone_crud.KintoneClient")
    def test_search_all_cursor_deleted_on_error(self, MockClient):
        """Test cursor is deleted even when an error occurs"""
        mock_client = MockClient.return_value
        mock_client.create_cursor.return_value = KintoneResponse(
            success=True,
            data={"id": "cursor-1", "totalCount": "100"},
        )
        mock_client.get_cursor_records.return_value = KintoneResponse(
            success=False,
            error="Cursor expired",
        )
        mock_client.delete_cursor.return_value = KintoneResponse(success=True, data={})

        crud = KintoneCRUD()

        with self.assertRaises(RuntimeError):
            list(crud.search_all(app_id=123))

        mock_client.delete_cursor.assert_called_once_with("cursor-1")


class TestAddManyChunking(unittest.TestCase):
    """Tests for add_many auto-chunking"""

    def setUp(self):
        self.patcher = patch("kintone_crud.get_config")
        self.mock_config = self.patcher.start()
        self.mock_config.return_value = MagicMock()

    def tearDown(self):
        self.patcher.stop()

    @patch("kintone_crud.KintoneClient")
    def test_add_many_single_chunk(self, MockClient):
        """Test add_many with records fitting in single chunk"""
        mock_client = MockClient.return_value
        mock_client.add_records.return_value = KintoneResponse(
            success=True,
            data={"ids": ["1", "2", "3"]},
        )

        crud = KintoneCRUD()
        records = [{"Title": f"Record {i}"} for i in range(3)]
        results = crud.add_many(app_id=123, records=records)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        mock_client.add_records.assert_called_once()

    @patch("kintone_crud.KintoneClient")
    def test_add_many_multiple_chunks(self, MockClient):
        """Test add_many splits records into chunks of 100"""
        mock_client = MockClient.return_value
        mock_client.add_records.return_value = KintoneResponse(
            success=True,
            data={"ids": []},
        )

        crud = KintoneCRUD()
        records = [{"Title": f"Record {i}"} for i in range(250)]
        results = crud.add_many(app_id=123, records=records)

        self.assertEqual(len(results), 3)  # 100 + 100 + 50
        self.assertEqual(mock_client.add_records.call_count, 3)

    @patch("kintone_crud.KintoneClient")
    def test_add_many_stops_on_error(self, MockClient):
        """Test add_many stops processing on first error"""
        mock_client = MockClient.return_value
        mock_client.add_records.side_effect = [
            KintoneResponse(success=True, data={"ids": []}),
            KintoneResponse(success=False, error="Quota exceeded"),
            KintoneResponse(success=True, data={"ids": []}),  # Should not be called
        ]

        crud = KintoneCRUD()
        records = [{"Title": f"Record {i}"} for i in range(250)]
        results = crud.add_many(app_id=123, records=records)

        self.assertEqual(len(results), 2)  # Only 2 chunks processed
        self.assertTrue(results[0].success)
        self.assertFalse(results[1].success)


class TestUpdateManyChunking(unittest.TestCase):
    """Tests for update_many auto-chunking"""

    def setUp(self):
        self.patcher = patch("kintone_crud.get_config")
        self.mock_config = self.patcher.start()
        self.mock_config.return_value = MagicMock()

    def tearDown(self):
        self.patcher.stop()

    @patch("kintone_crud.KintoneClient")
    def test_update_many_single_chunk(self, MockClient):
        """Test update_many with records fitting in single chunk"""
        mock_client = MockClient.return_value
        mock_client.update_records.return_value = KintoneResponse(
            success=True,
            data={"records": []},
        )

        crud = KintoneCRUD()
        records = [{"id": i, "Title": f"Updated {i}"} for i in range(1, 4)]
        results = crud.update_many(app_id=123, records=records)

        self.assertEqual(len(results), 1)
        mock_client.update_records.assert_called_once()

    @patch("kintone_crud.KintoneClient")
    def test_update_many_multiple_chunks(self, MockClient):
        """Test update_many splits records into chunks of 100"""
        mock_client = MockClient.return_value
        mock_client.update_records.return_value = KintoneResponse(
            success=True,
            data={"records": []},
        )

        crud = KintoneCRUD()
        records = [{"id": i, "Title": f"Updated {i}"} for i in range(1, 201)]
        results = crud.update_many(app_id=123, records=records)

        self.assertEqual(len(results), 2)  # 100 + 100
        self.assertEqual(mock_client.update_records.call_count, 2)

    def test_update_many_requires_id(self):
        """Test update_many raises error when record has no id"""
        with patch("kintone_crud.KintoneClient"):
            crud = KintoneCRUD()
            records = [{"Title": "No ID"}]

            with self.assertRaises(ValueError) as ctx:
                crud.update_many(app_id=123, records=records)

            self.assertIn("id", str(ctx.exception))

    @patch("kintone_crud.KintoneClient")
    def test_update_many_accepts_dollar_id(self, MockClient):
        """Test update_many accepts $id field"""
        mock_client = MockClient.return_value
        mock_client.update_records.return_value = KintoneResponse(
            success=True,
            data={"records": []},
        )

        crud = KintoneCRUD()
        records = [{"$id": 1, "Title": "Updated"}]
        results = crud.update_many(app_id=123, records=records)

        self.assertEqual(len(results), 1)


class TestStatusOperations(unittest.TestCase):
    """Tests for status operations"""

    def setUp(self):
        self.patcher = patch("kintone_crud.get_config")
        self.mock_config = self.patcher.start()
        self.mock_config.return_value = MagicMock()

    def tearDown(self):
        self.patcher.stop()

    @patch("kintone_crud.KintoneClient")
    def test_change_status(self, MockClient):
        """Test change_status calls client method"""
        mock_client = MockClient.return_value
        mock_client.update_status.return_value = KintoneResponse(
            success=True,
            data={"revision": "5"},
        )

        crud = KintoneCRUD()
        result = crud.change_status(
            app_id=123,
            record_id=1,
            action="Approve",
            assignee="tanaka",
        )

        self.assertTrue(result.success)
        mock_client.update_status.assert_called_once_with(123, 1, "Approve", "tanaka")


class TestCommentOperations(unittest.TestCase):
    """Tests for comment operations"""

    def setUp(self):
        self.patcher = patch("kintone_crud.get_config")
        self.mock_config = self.patcher.start()
        self.mock_config.return_value = MagicMock()

    def tearDown(self):
        self.patcher.stop()

    @patch("kintone_crud.KintoneClient")
    def test_add_comment_with_mentions(self, MockClient):
        """Test add_comment converts mention list to proper format"""
        mock_client = MockClient.return_value
        mock_client.add_comment.return_value = KintoneResponse(
            success=True,
            data={"id": "101"},
        )

        crud = KintoneCRUD()
        result = crud.add_comment(
            app_id=123,
            record_id=1,
            text="Please review",
            mentions=["tanaka", "suzuki"],
        )

        self.assertTrue(result.success)
        mock_client.add_comment.assert_called_once_with(
            123,
            1,
            "Please review",
            [
                {"code": "tanaka", "type": "USER"},
                {"code": "suzuki", "type": "USER"},
            ],
        )

    @patch("kintone_crud.KintoneClient")
    def test_add_comment_without_mentions(self, MockClient):
        """Test add_comment without mentions"""
        mock_client = MockClient.return_value
        mock_client.add_comment.return_value = KintoneResponse(
            success=True,
            data={"id": "101"},
        )

        crud = KintoneCRUD()
        crud.add_comment(app_id=123, record_id=1, text="Test comment")

        mock_client.add_comment.assert_called_once_with(123, 1, "Test comment", None)


if __name__ == "__main__":
    unittest.main()
