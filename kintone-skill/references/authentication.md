# KINTONE Authentication Reference

Reference for KINTONE REST API authentication methods.

## Table of Contents

- [Authentication Methods](#authentication-methods)
- [API Token Authentication (Recommended)](#api-token-authentication-recommended)
- [Password Authentication](#password-authentication)
- [Security Best Practices](#security-best-practices)
- [Environment Variable Examples](#environment-variable-examples)
- [Troubleshooting](#troubleshooting)

## Authentication Methods

KINTONE は以下の認証方式をサポートしています：

| 方式 | ヘッダー | 推奨度 | 用途 |
|------|---------|--------|------|
| API トークン | `X-Cybozu-API-Token` | ★★★ | スクリプト・自動化 |
| パスワード認証 | `X-Cybozu-Authorization` | ★★☆ | 一時的なアクセス |
| OAuth | Bearer トークン | ★★☆ | 外部アプリ連携 |

## API Token Authentication (Recommended)

### トークン発行手順

1. KINTONE にログイン
2. 対象アプリを開く
3. 「アプリの設定」→「APIトークン」
4. 「生成する」をクリック
5. 必要な権限を選択
6. 「保存」→「アプリを更新」

### 権限設定

| 権限 | 説明 | 必要な操作 |
|------|------|-----------|
| レコード閲覧 | レコードの取得・検索 | GET |
| レコード追加 | レコードの追加 | POST |
| レコード編集 | レコードの更新 | PUT |
| レコード削除 | レコードの削除 | DELETE |
| アプリ管理 | アプリ設定の変更 | アプリ操作 |

### 使用方法

```bash
# 環境変数に設定
export KINTONE_API_TOKEN="your-api-token-here"
```

```python
# Python
headers = {
    "X-Cybozu-API-Token": api_token,
    "Content-Type": "application/json"
}
```

### 複数アプリのトークン

複数アプリにアクセスする場合、トークンをカンマ区切りで指定：

```
X-Cybozu-API-Token: token1,token2,token3
```

## Password Authentication

ユーザーのログイン名とパスワードを Base64 エンコードして使用。

```python
import base64

credentials = f"{login_name}:{password}"
encoded = base64.b64encode(credentials.encode()).decode()

headers = {
    "X-Cybozu-Authorization": encoded
}
```

**注意**: パスワード認証はセキュリティ上、本番環境では非推奨。

## Security Best Practices

### やるべきこと

- [ ] API トークンは環境変数で管理
- [ ] 必要最小限の権限のみ付与
- [ ] 本番・開発環境でトークンを分ける
- [ ] 定期的にトークンを再発行

### やってはいけないこと

- ❌ トークンをソースコードにハードコード
- ❌ トークンを Git にコミット
- ❌ 全権限を持つトークンを作成
- ❌ 複数人で同じトークンを共有

## Environment Variable Examples

### Bash/Zsh

```bash
# ~/.bashrc または ~/.zshrc
export KINTONE_DOMAIN="your-company.cybozu.com"
export KINTONE_API_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxx"
```

### direnv（プロジェクトごと）

```bash
# .envrc
export KINTONE_DOMAIN="your-company.cybozu.com"
export KINTONE_API_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxx"
```

### 設定ファイル

`~/.config/kintone-skill/config.json`:

```json
{
  "domain": "your-company.cybozu.com",
  "api_token": "xxxxxxxxxxxxxxxxxxxxxxxx",
  "default_app_id": 123,
  "cache_ttl": 3600
}
```

## Troubleshooting

### 401 Unauthorized

- トークンが正しくない
- トークンの有効期限切れ
- ヘッダー名のタイポ

### 403 Forbidden

- 指定した操作の権限がない
- アプリへのアクセス権限がない
- トークンが別のアプリ用

### CORS エラー（ブラウザ）

- KINTONE REST API はブラウザからの直接アクセスに制限あり
- サーバーサイドから呼び出すか、KINTONE プラグイン/カスタマイズで使用
