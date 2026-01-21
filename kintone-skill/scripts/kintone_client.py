#!/usr/bin/env python3
"""KINTONE API クライアントモジュール"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Optional
from dataclasses import dataclass

from kintone_config import KintoneConfig, get_config


@dataclass
class KintoneResponse:
    """API レスポンス"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


class KintoneClient:
    """KINTONE REST API クライアント"""

    def __init__(self, config: Optional[KintoneConfig] = None):
        self.config = config or get_config()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> KintoneResponse:
        """API リクエストを実行"""
        url = f"{self.config.base_url}/k/v1/{endpoint}"

        # GET リクエストの場合、パラメータを URL に追加
        if method == "GET" and params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        headers = {
            "X-Cybozu-API-Token": self.config.api_token,
        }

        request_data = None
        if data and method != "GET":
            request_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(
            url,
            data=request_data,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                return KintoneResponse(success=True, data=response_data)
        except urllib.error.HTTPError as e:
            error_body = json.loads(e.read().decode("utf-8"))
            return KintoneResponse(
                success=False,
                error=error_body.get("message", str(e)),
                error_code=error_body.get("code"),
            )
        except Exception as e:
            return KintoneResponse(success=False, error=str(e))

    # === レコード操作 ===

    def get_record(self, app_id: int, record_id: int) -> KintoneResponse:
        """レコードを1件取得"""
        return self._make_request(
            "GET",
            "record.json",
            params={"app": app_id, "id": record_id},
        )

    def get_records(
        self,
        app_id: int,
        query: str = "",
        fields: Optional[list[str]] = None,
        total_count: bool = False,
    ) -> KintoneResponse:
        """レコードを検索・取得"""
        params: dict[str, Any] = {"app": app_id}
        if query:
            params["query"] = query
        if fields:
            params["fields"] = fields
        if total_count:
            params["totalCount"] = "true"

        return self._make_request("GET", "records.json", params=params)

    def add_record(self, app_id: int, record: dict) -> KintoneResponse:
        """レコードを1件追加"""
        return self._make_request(
            "POST",
            "record.json",
            data={"app": app_id, "record": record},
        )

    def add_records(self, app_id: int, records: list[dict]) -> KintoneResponse:
        """レコードを複数件追加"""
        return self._make_request(
            "POST",
            "records.json",
            data={"app": app_id, "records": records},
        )

    def update_record(
        self,
        app_id: int,
        record_id: int,
        record: dict,
        revision: Optional[int] = None,
    ) -> KintoneResponse:
        """レコードを1件更新"""
        data: dict[str, Any] = {
            "app": app_id,
            "id": record_id,
            "record": record,
        }
        if revision is not None:
            data["revision"] = revision

        return self._make_request("PUT", "record.json", data=data)

    def update_records(self, app_id: int, records: list[dict]) -> KintoneResponse:
        """レコードを複数件更新"""
        return self._make_request(
            "PUT",
            "records.json",
            data={"app": app_id, "records": records},
        )

    def delete_records(self, app_id: int, record_ids: list[int]) -> KintoneResponse:
        """レコードを削除"""
        return self._make_request(
            "DELETE",
            "records.json",
            data={"app": app_id, "ids": record_ids},
        )

    # === アプリ情報 ===

    def get_app(self, app_id: int) -> KintoneResponse:
        """アプリ情報を取得"""
        return self._make_request("GET", "app.json", params={"id": app_id})

    def get_apps(
        self,
        ids: Optional[list[int]] = None,
        name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> KintoneResponse:
        """アプリ一覧を取得"""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if ids:
            params["ids"] = ids
        if name:
            params["name"] = name

        return self._make_request("GET", "apps.json", params=params)

    def get_form_fields(self, app_id: int) -> KintoneResponse:
        """フォームのフィールド定義を取得"""
        return self._make_request("GET", "app/form/fields.json", params={"app": app_id})

    # === ファイル操作 ===

    def download_file(self, file_key: str) -> bytes:
        """ファイルをダウンロード"""
        url = f"{self.config.base_url}/k/v1/file.json?fileKey={file_key}"
        headers = {"X-Cybozu-API-Token": self.config.api_token}

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.read()

    def upload_file(self, file_path: str, file_name: str) -> KintoneResponse:
        """ファイルをアップロード"""
        import mimetypes
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders

        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

        with open(file_path, "rb") as f:
            file_content = f.read()

        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8") + file_content + f"\r\n--{boundary}--\r\n".encode("utf-8")

        url = f"{self.config.base_url}/k/v1/file.json"
        headers = {
            "X-Cybozu-API-Token": self.config.api_token,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                return KintoneResponse(success=True, data=response_data)
        except urllib.error.HTTPError as e:
            error_body = json.loads(e.read().decode("utf-8"))
            return KintoneResponse(
                success=False,
                error=error_body.get("message", str(e)),
                error_code=error_body.get("code"),
            )


if __name__ == "__main__":
    # テスト用
    client = KintoneClient()
    print("KintoneClient initialized")
    print(f"Base URL: {client.config.base_url}")
