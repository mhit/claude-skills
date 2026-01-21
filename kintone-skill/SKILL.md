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

### /kintone apps

Lists all accessible apps.

```bash
scripts/kintone.sh apps
scripts/kintone.sh apps --name "顧客"           # Filter by name
scripts/kintone.sh apps --app-ids 123,456       # Filter by IDs
scripts/kintone.sh apps --limit 50 --offset 10  # Pagination
scripts/kintone.sh apps --json
```

### /kintone search --all

Retrieves all records using Cursor API (no 500-record limit).

```bash
scripts/kintone.sh search 123 --all
scripts/kintone.sh search 123 'Status = "Done"' --all
scripts/kintone.sh search 123 --all --json
```

### /kintone status

Updates record status (workflow).

```bash
scripts/kintone.sh status 123 1 "Approve"
scripts/kintone.sh status 123 1 "Approve" --assignee tanaka
```

### /kintone comment

Manages record comments.

```bash
# Add comment
scripts/kintone.sh comment 123 1 add "確認しました"

# List comments
scripts/kintone.sh comment 123 1 list

# Delete comment
scripts/kintone.sh comment 123 1 delete 456
```

### /kintone schema

Displays app field definitions. Results are cached.

```bash
scripts/kintone.sh schema 123
scripts/kintone.sh schema 123 --refresh  # Force refresh
scripts/kintone.sh schema 123 --json     # JSON output

# Cache management
scripts/kintone.sh schema list           # List cached schemas
scripts/kintone.sh schema clear          # Clear all cache
scripts/kintone.sh schema clear 123      # Clear specific app cache
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
# Single record
scripts/kintone.sh add 123 '{"タイトル": "新規タスク", "担当者": "田中"}'
scripts/kintone.sh add 123 --file record.json

# Multiple records (auto-chunking: splits into 100-record batches)
scripts/kintone.sh add 123 --file records.json  # JSON array of records
```

**Auto Chunking**: When adding 100+ records, automatically splits into multiple API calls (100 records per batch).

### /kintone update

```bash
# Single record
scripts/kintone.sh update 123 1 '{"ステータス": "完了"}'
```

**Bulk update** (Python API only):

```python
# Multiple records with auto-chunking (100 records per batch)
records = [{"id": i, "record": {"Status": {"value": "Done"}}} for i in range(1, 251)]
results = crud.update_many(app_id=123, records=records)
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

# List attachments in a record field
scripts/kintone.sh file list 123 1 添付ファイル
```

**Download all files from record** (Python API):

```python
from kintone_file import KintoneFileManager

manager = KintoneFileManager()

# Get file info from record
files = manager.get_file_info_from_record(app_id=123, record_id=1, field_code="添付ファイル")
# Returns: [{"fileKey": "...", "name": "doc.pdf", "contentType": "...", "size": "1024"}, ...]

# Download all files from record
results = manager.download_from_record(app_id=123, record_id=1, field_code="添付ファイル")
# Returns: [("file1.txt", True, "/path/to/file1.txt"), ("file2.pdf", True, "/path/to/file2.pdf")]
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
from kintone_crud import KintoneCRUD
from kintone_schema import SchemaManager
from kintone_search import query, parse_natural_query

# Client
client = KintoneClient()
response = client.get_record(app_id=123, record_id=1)

# CRUD operations
crud = KintoneCRUD()

# Search all records (no 500-record limit)
for record in crud.search_all(app_id=123, query='Status = "Done"'):
    print(record)

# Bulk add with auto-chunking (handles 100+ records)
records = [{"Title": f"Item {i}"} for i in range(250)]
results = crud.add_many(app_id=123, records=records)  # Auto-splits into 3 chunks

# Status update (workflow)
crud.change_status(app_id=123, record_id=1, action="Approve", assignee="tanaka")

# Comment operations
crud.add_comment(app_id=123, record_id=1, text="確認しました", mentions=["tanaka"])
crud.get_comments(app_id=123, record_id=1)
crud.delete_comment(app_id=123, record_id=1, comment_id=456)

# Bulk Request (atomic multi-app operations, max 20 requests)
client = KintoneClient()
requests = [
    {"method": "POST", "api": "/k/v1/record.json", "payload": {"app": 123, "record": {"Title": {"value": "A"}}}},
    {"method": "POST", "api": "/k/v1/record.json", "payload": {"app": 456, "record": {"Name": {"value": "B"}}}},
]
result = client.bulk_request(requests)  # All succeed or all rollback

# Apps list
response = client.get_apps(ids=[123, 456], name="顧客", limit=50, offset=0)

# Schema
schema_mgr = SchemaManager()
schema = schema_mgr.get_schema(app_id=123)
cached = schema_mgr.list_cached_schemas()  # [(app_id, app_name, cached_at), ...]
schema_mgr.clear_cache()                   # Clear all
schema_mgr.clear_cache(app_id=123)         # Clear specific app

# Query builder
q = query().equals("ステータス", "完了").order_by("更新日時", "desc").limit(10)
print(q.build())
```

## API Limits

| API | Limit | Handling |
|-----|-------|----------|
| Get records | 500 records/request | Use `--all` (Cursor API) |
| Add records | 100 records/request | Auto-chunking |
| Update records | 100 records/request | Auto-chunking |
| Delete records | 100 records/request | Manual chunking |
| Bulk request | 20 requests | Atomic rollback |
| Cursor | 10 cursors/domain, 10min TTL | Auto-cleanup |
| Comments | 10 comments/request | Pagination |

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
