---
name: managing-kintone
description: "Performs CRUD operations on KINTONE REST API. Retrieves, adds, updates, and deletes records. Supports natural language query conversion, schema caching, and file attachments. Use when users mention KINTONE, kintone, or want to: (1) Get/add/update/delete KINTONE records, (2) Search KINTONE data, (3) Check app schema/field definitions, (4) Upload/download attachments."
---

# Managing KINTONE

Operates KINTONE REST API directly from Claude Code.

## When to Use

| User Request | Command |
|-------------|---------|
| "Get KINTONE data" | `/kintone get` `/kintone search` |
| "Add to KINTONE" | `/kintone add` |
| "Update KINTONE record" | `/kintone update` |
| "Attach file to KINTONE" | `/kintone file` |
| "Show field definitions" | `/kintone schema` |

## Prerequisites

Required environment variables:

```bash
# Required
export KINTONE_DOMAIN="xxx.cybozu.com"
export KINTONE_API_TOKEN="your-api-token"

# Optional
export KINTONE_DEFAULT_APP="123"
export KINTONE_CACHE_DIR="~/.cache/kintone-skill"
export KINTONE_CACHE_TTL="3600"
```

## Commands

### /kintone schema

Displays app field definitions. Results are cached.

```bash
scripts/kintone.sh schema 123
scripts/kintone.sh schema 123 --refresh  # Force refresh
scripts/kintone.sh schema 123 --json     # JSON output
```

### /kintone get

```bash
scripts/kintone.sh get 123 1        # Get record ID 1 from app 123
scripts/kintone.sh get 123 1 --json
```

### /kintone search

```bash
scripts/kintone.sh search 123
scripts/kintone.sh search 123 'ステータス = "完了"'
scripts/kintone.sh search 123 --limit 50 --offset 100
```

**Natural language query conversion**:

| Input | Converted Query |
|-------|----------------|
| `名前が田中` | `名前 = "田中"` |
| `ステータスが完了または進行中` | `ステータス in ("完了", "進行中")` |
| `作成日が今日` | `作成日 = TODAY()` |
| `担当者が自分` | `担当者 = LOGINUSER()` |
| `メモが空でない` | `メモ != ""` |
| `金額が10000以上` | `金額 >= "10000"` |

Convert with: `scripts/kintone.sh query "名前が田中"`

### /kintone add

```bash
scripts/kintone.sh add 123 '{"タイトル": "新規タスク", "担当者": "田中"}'
scripts/kintone.sh add 123 --file record.json
```

### /kintone update

```bash
scripts/kintone.sh update 123 1 '{"ステータス": "完了"}'
```

### /kintone delete

```bash
scripts/kintone.sh delete 123 1,2,3  # Comma-separated IDs
```

### /kintone file

```bash
# Upload
scripts/kintone.sh file upload ./document.pdf
# Returns fileKey

# Download
scripts/kintone.sh file download abc123def456 --output ./downloaded.pdf

# List attachments
scripts/kintone.sh file list --app 123 --record 1 --field 添付ファイル
```

## Schema Caching

1. Fetches schema from API on first access
2. Saves to `~/.cache/kintone-skill/schemas/app_XXX.json`
3. Subsequent accesses use cache (fast)
4. Use `--refresh` to update cache
5. Default TTL: 1 hour

**Benefit**: Enables immediate field name/type lookup for accurate query generation.

## Python API

```python
from kintone_client import KintoneClient
from kintone_schema import SchemaManager
from kintone_search import query, parse_natural_query

# Client
client = KintoneClient()
response = client.get_record(app_id=123, record_id=1)

# Schema
schema_mgr = SchemaManager()
schema = schema_mgr.get_schema(app_id=123)

# Query builder
q = query().equals("ステータス", "完了").order_by("更新日時", "desc").limit(10)
print(q.build())
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `KINTONE_DOMAIN not found` | Env var not set | `export KINTONE_DOMAIN=...` |
| `401 Unauthorized` | Invalid API token | Regenerate token |
| `403 Forbidden` | Insufficient permissions | Check app token permissions |
| `404 Not Found` | App/record doesn't exist | Verify ID |
| `400 Bad Request` | Invalid request format | Check field names/types |

## References

- [references/query-syntax.md](references/query-syntax.md) - Query syntax details
- [references/authentication.md](references/authentication.md) - Authentication methods
