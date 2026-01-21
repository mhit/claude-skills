#!/usr/bin/env python3
"""Tests for extended kintone_client features (Cursor, Status, Comment, Bulk)"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from kintone_client import KintoneClient, KintoneResponse, KintoneConfig


class TestCursorAPI(unittest.TestCase):
    """Tests for Cursor API methods"""

    def setUp(self):
        self.config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.client = KintoneClient(self.config)

    @patch.object(KintoneClient, "_make_request")
    def test_create_cursor(self, mock_request):
        """Test cursor creation"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"id": "cursor-123", "totalCount": "1000"},
        )

        result = self.client.create_cursor(app_id=123, query="", size=500)

        self.assertTrue(result.success)
        self.assertEqual(result.data["id"], "cursor-123")
        mock_request.assert_called_once_with(
            "POST",
            "records/cursor.json",
            data={"app": 123, "size": 500},
        )

    @patch.object(KintoneClient, "_make_request")
    def test_create_cursor_with_query_and_fields(self, mock_request):
        """Test cursor creation with query and fields"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"id": "cursor-456", "totalCount": "500"},
        )

        result = self.client.create_cursor(
            app_id=123,
            query='Status = "Done"',
            fields=["Title", "Status"],
            size=100,
        )

        self.assertTrue(result.success)
        mock_request.assert_called_once_with(
            "POST",
            "records/cursor.json",
            data={
                "app": 123,
                "size": 100,
                "query": 'Status = "Done"',
                "fields": ["Title", "Status"],
            },
        )

    @patch.object(KintoneClient, "_make_request")
    def test_create_cursor_size_limits(self, mock_request):
        """Test cursor size is clamped to 1-500"""
        mock_request.return_value = KintoneResponse(success=True, data={})

        # Size > 500 should be clamped to 500
        self.client.create_cursor(app_id=123, size=1000)
        call_args = mock_request.call_args[1]["data"]
        self.assertEqual(call_args["size"], 500)

        # Size < 1 should be clamped to 1
        self.client.create_cursor(app_id=123, size=0)
        call_args = mock_request.call_args[1]["data"]
        self.assertEqual(call_args["size"], 1)

    @patch.object(KintoneClient, "_make_request")
    def test_get_cursor_records(self, mock_request):
        """Test getting records from cursor"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"records": [{"$id": {"value": "1"}}], "next": True},
        )

        result = self.client.get_cursor_records("cursor-123")

        self.assertTrue(result.success)
        self.assertEqual(len(result.data["records"]), 1)
        self.assertTrue(result.data["next"])
        mock_request.assert_called_once_with(
            "GET",
            "records/cursor.json",
            params={"id": "cursor-123"},
        )

    @patch.object(KintoneClient, "_make_request")
    def test_delete_cursor(self, mock_request):
        """Test cursor deletion"""
        mock_request.return_value = KintoneResponse(success=True, data={})

        result = self.client.delete_cursor("cursor-123")

        self.assertTrue(result.success)
        mock_request.assert_called_once_with(
            "DELETE",
            "records/cursor.json",
            data={"id": "cursor-123"},
        )


class TestStatusAPI(unittest.TestCase):
    """Tests for Status Update API"""

    def setUp(self):
        self.config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.client = KintoneClient(self.config)

    @patch.object(KintoneClient, "_make_request")
    def test_update_status_basic(self, mock_request):
        """Test basic status update"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"revision": "5"},
        )

        result = self.client.update_status(
            app_id=123,
            record_id=1,
            action="Approve",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data["revision"], "5")
        mock_request.assert_called_once_with(
            "PUT",
            "record/status.json",
            data={"app": 123, "id": 1, "action": "Approve"},
        )

    @patch.object(KintoneClient, "_make_request")
    def test_update_status_with_assignee(self, mock_request):
        """Test status update with assignee"""
        mock_request.return_value = KintoneResponse(success=True, data={})

        self.client.update_status(
            app_id=123,
            record_id=1,
            action="Approve",
            assignee="tanaka",
        )

        call_args = mock_request.call_args[1]["data"]
        self.assertEqual(call_args["assignee"], "tanaka")

    @patch.object(KintoneClient, "_make_request")
    def test_update_status_with_revision(self, mock_request):
        """Test status update with revision"""
        mock_request.return_value = KintoneResponse(success=True, data={})

        self.client.update_status(
            app_id=123,
            record_id=1,
            action="Approve",
            revision=4,
        )

        call_args = mock_request.call_args[1]["data"]
        self.assertEqual(call_args["revision"], 4)


class TestCommentAPI(unittest.TestCase):
    """Tests for Comment API"""

    def setUp(self):
        self.config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.client = KintoneClient(self.config)

    @patch.object(KintoneClient, "_make_request")
    def test_add_comment_basic(self, mock_request):
        """Test basic comment addition"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"id": "101"},
        )

        result = self.client.add_comment(
            app_id=123,
            record_id=1,
            text="This is a test comment",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data["id"], "101")
        mock_request.assert_called_once_with(
            "POST",
            "record/comment.json",
            data={
                "app": 123,
                "record": 1,
                "comment": {"text": "This is a test comment"},
            },
        )

    @patch.object(KintoneClient, "_make_request")
    def test_add_comment_with_mentions(self, mock_request):
        """Test comment with mentions"""
        mock_request.return_value = KintoneResponse(success=True, data={})

        self.client.add_comment(
            app_id=123,
            record_id=1,
            text="Please review @tanaka",
            mentions=[{"code": "tanaka", "type": "USER"}],
        )

        call_args = mock_request.call_args[1]["data"]
        self.assertEqual(
            call_args["comment"]["mentions"],
            [{"code": "tanaka", "type": "USER"}],
        )

    @patch.object(KintoneClient, "_make_request")
    def test_get_comments(self, mock_request):
        """Test getting comments"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={
                "comments": [{"id": "101", "text": "Test"}],
                "older": False,
                "newer": False,
            },
        )

        result = self.client.get_comments(
            app_id=123,
            record_id=1,
            order="desc",
            limit=10,
        )

        self.assertTrue(result.success)
        self.assertEqual(len(result.data["comments"]), 1)
        mock_request.assert_called_once_with(
            "GET",
            "record/comments.json",
            params={
                "app": 123,
                "record": 1,
                "order": "desc",
                "offset": 0,
                "limit": 10,
            },
        )

    @patch.object(KintoneClient, "_make_request")
    def test_get_comments_limit_capped(self, mock_request):
        """Test comment limit is capped at 10"""
        mock_request.return_value = KintoneResponse(success=True, data={})

        self.client.get_comments(app_id=123, record_id=1, limit=100)

        call_args = mock_request.call_args[1]["params"]
        self.assertEqual(call_args["limit"], 10)

    @patch.object(KintoneClient, "_make_request")
    def test_delete_comment(self, mock_request):
        """Test comment deletion"""
        mock_request.return_value = KintoneResponse(success=True, data={})

        result = self.client.delete_comment(
            app_id=123,
            record_id=1,
            comment_id=101,
        )

        self.assertTrue(result.success)
        mock_request.assert_called_once_with(
            "DELETE",
            "record/comment.json",
            data={"app": 123, "record": 1, "comment": 101},
        )


class TestBulkRequestAPI(unittest.TestCase):
    """Tests for Bulk Request API"""

    def setUp(self):
        self.config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.client = KintoneClient(self.config)

    @patch.object(KintoneClient, "_make_request")
    def test_bulk_request_basic(self, mock_request):
        """Test basic bulk request"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"results": [{"id": "1"}, {"id": "2"}]},
        )

        requests = [
            {
                "method": "POST",
                "api": "/k/v1/record.json",
                "payload": {"app": 123, "record": {}},
            },
            {
                "method": "POST",
                "api": "/k/v1/record.json",
                "payload": {"app": 456, "record": {}},
            },
        ]

        result = self.client.bulk_request(requests)

        self.assertTrue(result.success)
        self.assertEqual(len(result.data["results"]), 2)
        mock_request.assert_called_once_with(
            "POST",
            "bulkRequest.json",
            data={"requests": requests},
        )

    def test_bulk_request_limit_exceeded(self):
        """Test bulk request fails when exceeding 20 requests"""
        requests = [{"method": "POST", "api": "/k/v1/record.json", "payload": {}}] * 21

        result = self.client.bulk_request(requests)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "LIMIT_EXCEEDED")
        self.assertIn("20", result.error)


if __name__ == "__main__":
    unittest.main()
