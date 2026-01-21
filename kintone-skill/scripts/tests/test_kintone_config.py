#!/usr/bin/env python3
"""Tests for kintone_config module"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import patch
from kintone_config import KintoneConfig, get_config


class TestKintoneConfig(unittest.TestCase):
    """Tests for KintoneConfig class"""

    def test_dataclass_fields(self):
        """Test dataclass has expected fields"""
        config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.assertEqual(config.domain, "test.cybozu.com")
        self.assertEqual(config.api_token, "test-token")
        self.assertIsNone(config.default_app_id)
        self.assertEqual(config.cache_ttl, 3600)

    def test_base_url(self):
        """Test base_url property"""
        config = KintoneConfig(
            domain="test.cybozu.com",
            api_token="test-token",
        )
        self.assertEqual(config.base_url, "https://test.cybozu.com")

    def test_ensure_cache_dir(self):
        """Test ensure_cache_dir creates directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = KintoneConfig(
                domain="test.cybozu.com",
                api_token="test-token",
                cache_dir=Path(tmpdir) / "test-cache",
            )
            cache_dir = config.ensure_cache_dir()
            self.assertTrue(cache_dir.exists())
            self.assertTrue(cache_dir.is_dir())

    def test_from_env(self):
        """Test loading config from environment variables"""
        with patch.dict(os.environ, {
            "KINTONE_DOMAIN": "env.cybozu.com",
            "KINTONE_API_TOKEN": "env-token",
            "KINTONE_DEFAULT_APP": "123",
            "KINTONE_CACHE_TTL": "7200",
        }):
            config = KintoneConfig.from_env()
            self.assertEqual(config.domain, "env.cybozu.com")
            self.assertEqual(config.api_token, "env-token")
            self.assertEqual(config.default_app_id, 123)
            self.assertEqual(config.cache_ttl, 7200)

    def test_from_env_missing_domain(self):
        """Test from_env raises error when KINTONE_DOMAIN is missing"""
        with patch.dict(os.environ, {
            "KINTONE_API_TOKEN": "test-token",
        }, clear=True):
            # Clear KINTONE_DOMAIN if it exists
            os.environ.pop("KINTONE_DOMAIN", None)
            with self.assertRaises(ValueError) as ctx:
                KintoneConfig.from_env()
            self.assertIn("KINTONE_DOMAIN", str(ctx.exception))

    def test_from_env_missing_token(self):
        """Test from_env raises error when KINTONE_API_TOKEN is missing"""
        with patch.dict(os.environ, {
            "KINTONE_DOMAIN": "test.cybozu.com",
        }, clear=True):
            # Clear KINTONE_API_TOKEN if it exists
            os.environ.pop("KINTONE_API_TOKEN", None)
            with self.assertRaises(ValueError) as ctx:
                KintoneConfig.from_env()
            self.assertIn("KINTONE_API_TOKEN", str(ctx.exception))

    def test_from_file(self):
        """Test loading config from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "domain": "file.cybozu.com",
                "api_token": "file-token",
                "default_app_id": 456,
                "cache_ttl": 1800,
            }, f)
            f.flush()

            try:
                config = KintoneConfig.from_file(Path(f.name))
                self.assertEqual(config.domain, "file.cybozu.com")
                self.assertEqual(config.api_token, "file-token")
                self.assertEqual(config.default_app_id, 456)
                self.assertEqual(config.cache_ttl, 1800)
            finally:
                os.unlink(f.name)


class TestGetConfig(unittest.TestCase):
    """Tests for get_config function"""

    def test_get_config_from_env(self):
        """Test get_config prefers environment variables"""
        with patch.dict(os.environ, {
            "KINTONE_DOMAIN": "env.cybozu.com",
            "KINTONE_API_TOKEN": "env-token",
        }):
            config = get_config()
            self.assertEqual(config.domain, "env.cybozu.com")

    def test_get_config_no_config(self):
        """Test get_config raises error when no config available"""
        with patch.dict(os.environ, {}, clear=True):
            # Clear relevant env vars
            os.environ.pop("KINTONE_DOMAIN", None)
            os.environ.pop("KINTONE_API_TOKEN", None)
            with self.assertRaises(ValueError):
                get_config()


if __name__ == "__main__":
    unittest.main()
