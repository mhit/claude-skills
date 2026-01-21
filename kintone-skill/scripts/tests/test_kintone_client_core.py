#!/usr/bin/env python3
"""Tests for kintone_client core methods (CRUD, app info, files)"""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from kintone_client import KintoneClient, KintoneResponse, KintoneConfig


class TestKintoneResponse(unittest.TestCase):
    """Tests for KintoneResponse dataclass"""

    def test_success_response(self):
        """Test successful response"""
        resp = KintoneResponse(success=True, data={"id": "123"})
        self.assertTrue(resp.success)
        self.assertEqual(resp.data["id"], "123")
        self.assertIsNone(resp.error)

    def test_error_response(self):
        """Test error response"""
        resp = KintoneResponse(
            success=False,
            error="Permission denied",
            error_code="CB_NO01",
        )
        self.assertFalse(resp.success)
        self.assertIsNone(resp.data)
        self.assertEqual(resp.error, "Permission denied")
        self.assertEqual(resp.error_code, "CB_NO01")


class TestKintoneClientInit(unittest.TestCase):
    """Tests for KintoneClient initialization"""

    def test_init_with_config(self):
        """Test initialization with explicit config"""
        config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        client = KintoneClient(config)
        self.assertEqual(client.config.domain, "test.cybozu.com")

    @patch("kintone_client.get_config")
    def test_init_without_config(self, mock_get_config):
        """Test initialization without config uses default"""
        mock_get_config.return_value = KintoneConfig(
            domain="default.cybozu.com",
            api_token="default-token",
        )
        client = KintoneClient()
        self.assertEqual(client.config.domain, "default.cybozu.com")


class TestMakeRequest(unittest.TestCase):
    """Tests for _make_request method"""

    def setUp(self):
        self.config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.client = KintoneClient(self.config)

    @patch("urllib.request.urlopen")
    def test_get_request(self, mock_urlopen):
        """Test GET request"""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": "ok"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = self.client._make_request("GET", "test.json", params={"app": 123})

        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], "ok")

    @patch("urllib.request.urlopen")
    def test_post_request(self, mock_urlopen):
        """Test POST request with JSON body"""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": "1"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = self.client._make_request(
            "POST",
            "record.json",
            data={"app": 123, "record": {}},
        )

        self.assertTrue(result.success)

    @patch("urllib.request.urlopen")
    def test_http_error_handling(self, mock_urlopen):
        """Test HTTP error handling"""
        error_body = b'{"message": "Invalid request", "code": "CB_IL02"}'
        mock_error = urllib.error.HTTPError(
            url="https://test.cybozu.com/k/v1/test.json",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=MagicMock(read=MagicMock(return_value=error_body)),
        )
        mock_urlopen.side_effect = mock_error

        result = self.client._make_request("GET", "test.json")

        self.assertFalse(result.success)
        self.assertEqual(result.error, "Invalid request")
        self.assertEqual(result.error_code, "CB_IL02")

    @patch("urllib.request.urlopen")
    def test_general_exception_handling(self, mock_urlopen):
        """Test general exception handling"""
        mock_urlopen.side_effect = Exception("Network timeout")

        result = self.client._make_request("GET", "test.json")

        self.assertFalse(result.success)
        self.assertIn("timeout", result.error)


class TestRecordOperations(unittest.TestCase):
    """Tests for record CRUD operations"""

    def setUp(self):
        self.config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.client = KintoneClient(self.config)

    @patch.object(KintoneClient, "_make_request")
    def test_get_record(self, mock_request):
        """Test get single record"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"record": {"$id": {"value": "1"}}},
        )

        result = self.client.get_record(app_id=123, record_id=1)

        self.assertTrue(result.success)
        mock_request.assert_called_once_with(
            "GET",
            "record.json",
            params={"app": 123, "id": 1},
        )

    @patch.object(KintoneClient, "_make_request")
    def test_get_records(self, mock_request):
        """Test get multiple records"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"records": [], "totalCount": "0"},
        )

        result = self.client.get_records(
            app_id=123,
            query='Status = "Done"',
            fields=["Title", "Status"],
            total_count=True,
        )

        self.assertTrue(result.success)
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]["params"]["app"], 123)
        self.assertEqual(call_args[1]["params"]["query"], 'Status = "Done"')
        self.assertEqual(call_args[1]["params"]["totalCount"], "true")

    @patch.object(KintoneClient, "_make_request")
    def test_add_record(self, mock_request):
        """Test add single record"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"id": "10", "revision": "1"},
        )

        result = self.client.add_record(
            app_id=123,
            record={"Title": {"value": "Test"}},
        )

        self.assertTrue(result.success)
        mock_request.assert_called_once_with(
            "POST",
            "record.json",
            data={"app": 123, "record": {"Title": {"value": "Test"}}},
        )

    @patch.object(KintoneClient, "_make_request")
    def test_add_records(self, mock_request):
        """Test add multiple records"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"ids": ["10", "11"], "revisions": ["1", "1"]},
        )

        records = [
            {"Title": {"value": "Test 1"}},
            {"Title": {"value": "Test 2"}},
        ]
        result = self.client.add_records(app_id=123, records=records)

        self.assertTrue(result.success)
        self.assertEqual(len(result.data["ids"]), 2)

    @patch.object(KintoneClient, "_make_request")
    def test_update_record(self, mock_request):
        """Test update single record"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"revision": "2"},
        )

        result = self.client.update_record(
            app_id=123,
            record_id=1,
            record={"Status": {"value": "Done"}},
            revision=1,
        )

        self.assertTrue(result.success)
        call_data = mock_request.call_args[1]["data"]
        self.assertEqual(call_data["revision"], 1)

    @patch.object(KintoneClient, "_make_request")
    def test_update_records(self, mock_request):
        """Test update multiple records"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"records": [{"id": "1", "revision": "2"}]},
        )

        records = [{"id": 1, "record": {"Status": {"value": "Done"}}}]
        result = self.client.update_records(app_id=123, records=records)

        self.assertTrue(result.success)

    @patch.object(KintoneClient, "_make_request")
    def test_delete_records(self, mock_request):
        """Test delete records"""
        mock_request.return_value = KintoneResponse(success=True, data={})

        result = self.client.delete_records(app_id=123, record_ids=[1, 2, 3])

        self.assertTrue(result.success)
        call_data = mock_request.call_args[1]["data"]
        self.assertEqual(call_data["ids"], [1, 2, 3])


class TestAppOperations(unittest.TestCase):
    """Tests for app operations"""

    def setUp(self):
        self.config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.client = KintoneClient(self.config)

    @patch.object(KintoneClient, "_make_request")
    def test_get_app(self, mock_request):
        """Test get app info"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"appId": "123", "name": "Test App"},
        )

        result = self.client.get_app(app_id=123)

        self.assertTrue(result.success)
        mock_request.assert_called_once_with(
            "GET",
            "app.json",
            params={"id": 123},
        )

    @patch.object(KintoneClient, "_make_request")
    def test_get_apps(self, mock_request):
        """Test get apps list"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"apps": []},
        )

        result = self.client.get_apps(
            ids=[123, 456],
            name="Test",
            limit=50,
            offset=10,
        )

        self.assertTrue(result.success)
        call_params = mock_request.call_args[1]["params"]
        self.assertEqual(call_params["ids"], [123, 456])
        self.assertEqual(call_params["name"], "Test")
        self.assertEqual(call_params["limit"], 50)
        self.assertEqual(call_params["offset"], 10)

    @patch.object(KintoneClient, "_make_request")
    def test_get_form_fields(self, mock_request):
        """Test get form fields"""
        mock_request.return_value = KintoneResponse(
            success=True,
            data={"properties": {}},
        )

        result = self.client.get_form_fields(app_id=123)

        self.assertTrue(result.success)
        mock_request.assert_called_once_with(
            "GET",
            "app/form/fields.json",
            params={"app": 123},
        )


class TestFileOperations(unittest.TestCase):
    """Tests for file operations"""

    def setUp(self):
        self.config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.client = KintoneClient(self.config)

    @patch("urllib.request.urlopen")
    def test_download_file(self, mock_urlopen):
        """Test file download"""
        mock_response = MagicMock()
        mock_response.read.return_value = b"file content"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = self.client.download_file("abc123")

        self.assertEqual(result, b"file content")


if __name__ == "__main__":
    unittest.main()
