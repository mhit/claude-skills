#!/usr/bin/env python3
"""Tests for kintone_file module"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from kintone_file import KintoneFileManager
from kintone_client import KintoneResponse


class TestKintoneFileManager(unittest.TestCase):
    """Tests for KintoneFileManager class"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.patcher = patch("kintone_file.get_config")
        self.mock_config = self.patcher.start()
        self.mock_config.return_value = MagicMock(
            domain="test.cybozu.com",
            api_token="test-token",
            cache_dir=Path(self.temp_dir),
        )

    def tearDown(self):
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("kintone_file.KintoneClient")
    def test_upload_success(self, MockClient):
        """Test successful file upload"""
        mock_client = MockClient.return_value
        mock_client.upload_file.return_value = KintoneResponse(
            success=True,
            data={"fileKey": "abc123"},
        )

        # Create a test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")

        manager = KintoneFileManager()
        result = manager.upload(str(test_file))

        self.assertTrue(result.success)
        self.assertEqual(result.data["fileKey"], "abc123")

    @patch("kintone_file.KintoneClient")
    def test_upload_file_not_found(self, MockClient):
        """Test upload with non-existent file"""
        manager = KintoneFileManager()
        result = manager.upload("/nonexistent/file.txt")

        self.assertFalse(result.success)
        self.assertIn("not found", result.error)

    @patch("kintone_file.KintoneClient")
    def test_upload_with_custom_name(self, MockClient):
        """Test upload with custom file name"""
        mock_client = MockClient.return_value
        mock_client.upload_file.return_value = KintoneResponse(
            success=True,
            data={"fileKey": "xyz789"},
        )

        test_file = Path(self.temp_dir) / "original.txt"
        test_file.write_text("content")

        manager = KintoneFileManager()
        manager.upload(str(test_file), file_name="custom.txt")

        mock_client.upload_file.assert_called_once()
        call_args = mock_client.upload_file.call_args
        self.assertEqual(call_args[0][1], "custom.txt")

    @patch("kintone_file.KintoneClient")
    def test_download_success(self, MockClient):
        """Test successful file download"""
        mock_client = MockClient.return_value
        mock_client.download_file.return_value = b"file content here"

        manager = KintoneFileManager()
        output_path = Path(self.temp_dir) / "downloaded.txt"
        success, result = manager.download("abc123", str(output_path))

        self.assertTrue(success)
        self.assertEqual(result, str(output_path))
        self.assertEqual(output_path.read_bytes(), b"file content here")

    @patch("kintone_file.KintoneClient")
    def test_download_to_default_dir(self, MockClient):
        """Test download to default directory"""
        mock_client = MockClient.return_value
        mock_client.download_file.return_value = b"content"

        manager = KintoneFileManager()
        success, result = manager.download("abc123", file_name="myfile.txt")

        self.assertTrue(success)
        self.assertIn("myfile.txt", result)

    @patch("kintone_file.KintoneClient")
    def test_download_error(self, MockClient):
        """Test download error handling"""
        mock_client = MockClient.return_value
        mock_client.download_file.side_effect = Exception("Network error")

        manager = KintoneFileManager()
        success, result = manager.download("abc123")

        self.assertFalse(success)
        self.assertIn("Network error", result)

    @patch("kintone_file.KintoneClient")
    def test_get_file_info_from_record(self, MockClient):
        """Test getting file info from record"""
        mock_client = MockClient.return_value
        mock_client.get_record.return_value = KintoneResponse(
            success=True,
            data={
                "record": {
                    "Attachments": {
                        "value": [
                            {
                                "fileKey": "key1",
                                "name": "doc.pdf",
                                "contentType": "application/pdf",
                                "size": "1024",
                            },
                            {
                                "fileKey": "key2",
                                "name": "image.png",
                                "contentType": "image/png",
                                "size": "2048",
                            },
                        ]
                    }
                }
            },
        )

        manager = KintoneFileManager()
        files = manager.get_file_info_from_record(
            app_id=123,
            record_id=1,
            field_code="Attachments",
        )

        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "doc.pdf")
        self.assertEqual(files[1]["name"], "image.png")

    @patch("kintone_file.KintoneClient")
    def test_get_file_info_no_attachments(self, MockClient):
        """Test getting file info when field is empty"""
        mock_client = MockClient.return_value
        mock_client.get_record.return_value = KintoneResponse(
            success=True,
            data={
                "record": {
                    "Attachments": {"value": []}
                }
            },
        )

        manager = KintoneFileManager()
        files = manager.get_file_info_from_record(123, 1, "Attachments")

        self.assertEqual(len(files), 0)

    @patch("kintone_file.KintoneClient")
    def test_get_file_info_record_error(self, MockClient):
        """Test getting file info when record fetch fails"""
        mock_client = MockClient.return_value
        mock_client.get_record.return_value = KintoneResponse(
            success=False,
            error="Record not found",
        )

        manager = KintoneFileManager()
        files = manager.get_file_info_from_record(123, 1, "Attachments")

        self.assertEqual(len(files), 0)

    @patch("kintone_file.KintoneClient")
    def test_get_file_info_field_not_exists(self, MockClient):
        """Test getting file info when field doesn't exist"""
        mock_client = MockClient.return_value
        mock_client.get_record.return_value = KintoneResponse(
            success=True,
            data={"record": {}},
        )

        manager = KintoneFileManager()
        files = manager.get_file_info_from_record(123, 1, "NonExistent")

        self.assertEqual(len(files), 0)

    @patch("kintone_file.KintoneClient")
    def test_download_from_record(self, MockClient):
        """Test downloading all files from record"""
        mock_client = MockClient.return_value
        mock_client.get_record.return_value = KintoneResponse(
            success=True,
            data={
                "record": {
                    "Files": {
                        "value": [
                            {"fileKey": "key1", "name": "file1.txt"},
                            {"fileKey": "key2", "name": "file2.txt"},
                        ]
                    }
                }
            },
        )
        mock_client.download_file.return_value = b"content"

        manager = KintoneFileManager()
        results = manager.download_from_record(
            app_id=123,
            record_id=1,
            field_code="Files",
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "file1.txt")
        self.assertEqual(results[1][0], "file2.txt")


if __name__ == "__main__":
    unittest.main()
