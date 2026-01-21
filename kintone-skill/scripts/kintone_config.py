#!/usr/bin/env python3
"""KINTONE API 設定管理モジュール"""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class KintoneConfig:
    """KINTONE 接続設定"""
    domain: str
    api_token: str
    default_app_id: Optional[int] = None
    cache_dir: Path = Path.home() / ".cache" / "kintone-skill"
    cache_ttl: int = 3600  # 秒

    @classmethod
    def from_env(cls) -> "KintoneConfig":
        """環境変数から設定を読み込む"""
        domain = os.environ.get("KINTONE_DOMAIN")
        api_token = os.environ.get("KINTONE_API_TOKEN")

        if not domain:
            raise ValueError("KINTONE_DOMAIN environment variable is required")
        if not api_token:
            raise ValueError("KINTONE_API_TOKEN environment variable is required")

        default_app = os.environ.get("KINTONE_DEFAULT_APP")
        cache_dir = os.environ.get("KINTONE_CACHE_DIR")
        cache_ttl = os.environ.get("KINTONE_CACHE_TTL")

        return cls(
            domain=domain,
            api_token=api_token,
            default_app_id=int(default_app) if default_app else None,
            cache_dir=Path(cache_dir) if cache_dir else cls.cache_dir,
            cache_ttl=int(cache_ttl) if cache_ttl else cls.cache_ttl,
        )

    @classmethod
    def from_file(cls, config_path: Path) -> "KintoneConfig":
        """設定ファイルから読み込む"""
        with open(config_path) as f:
            data = json.load(f)

        return cls(
            domain=data["domain"],
            api_token=data["api_token"],
            default_app_id=data.get("default_app_id"),
            cache_dir=Path(data.get("cache_dir", cls.cache_dir)),
            cache_ttl=data.get("cache_ttl", cls.cache_ttl),
        )

    @property
    def base_url(self) -> str:
        """API ベース URL"""
        return f"https://{self.domain}"

    def ensure_cache_dir(self) -> Path:
        """キャッシュディレクトリを作成して返す"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir


def get_config() -> KintoneConfig:
    """設定を取得する（環境変数優先）"""
    config_file = Path.home() / ".config" / "kintone-skill" / "config.json"

    if os.environ.get("KINTONE_DOMAIN") and os.environ.get("KINTONE_API_TOKEN"):
        return KintoneConfig.from_env()
    elif config_file.exists():
        return KintoneConfig.from_file(config_file)
    else:
        raise ValueError(
            "KINTONE configuration not found. "
            "Set KINTONE_DOMAIN and KINTONE_API_TOKEN environment variables, "
            f"or create {config_file}"
        )


if __name__ == "__main__":
    # テスト用
    try:
        config = get_config()
        print(f"Domain: {config.domain}")
        print(f"Base URL: {config.base_url}")
        print(f"Default App: {config.default_app_id}")
        print(f"Cache Dir: {config.cache_dir}")
    except ValueError as e:
        print(f"Error: {e}")
