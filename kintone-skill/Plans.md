# KINTONE Skill 拡張計画

## 現状

実装済み: レコード CRUD、アプリ情報、ファイル操作、クエリビルダー、スキーマキャッシュ

## 未実装機能（優先度順）

| 優先度 | 機能 | エンドポイント | ユースケース |
|--------|------|---------------|-------------|
| P0 | Cursor API | `/records/cursor.json` | 500件超の取得 |
| P1 | Status API | `/record/status.json` | ワークフロー |
| P1 | Comment API | `/record/comment.json` | コメント操作 |
| P2 | Bulk Request | `/bulkRequest.json` | 複数アプリ一括 |
| P2 | Auto Chunking | - | 100件超の追加/更新 |

---

## Phase 1: Cursor API

**目的**: 500件制限を超えるレコード取得

**API**:
- `POST /records/cursor.json` - 作成（size: 1-500）
- `GET /records/cursor.json?id=xxx` - 取得（next: true/false）
- `DELETE /records/cursor.json` - 削除

**制限**: ドメイン最大10カーソル、10分で失効

**タスク**:
- [x] `create_cursor()`, `get_cursor_records()`, `delete_cursor()` 追加
- [x] `search_all()` メソッド追加（自動イテレーション）
- [x] CLI `search --all` オプション
- [x] テスト作成

---

## Phase 2: Status API

**目的**: ワークフローのステータス更新

**API**: `PUT /record/status.json`
- app, id, action（必須）、assignee, revision（任意）

**タスク**:
- [x] `update_status()` メソッド追加
- [x] CLI `status` コマンド追加
- [x] テスト作成

---

## Phase 3: Comment API

**目的**: レコードへのコメント操作

**API**:
- `POST /record/comment.json` - 追加（最大65,535文字、10メンション）
- `GET /record/comments.json` - 取得（最大10件/リクエスト）
- `DELETE /record/comment.json` - 削除

**タスク**:
- [x] `add_comment()`, `get_comments()`, `delete_comment()` 追加
- [x] CLI `comment add/list/delete` サブコマンド
- [x] メンション対応（ユーザー名リスト形式）
- [x] テスト作成

---

## Phase 4: Bulk Request API

**目的**: 複数アプリへのアトミック操作

**API**: `POST /bulkRequest.json`
- 最大20リクエスト、失敗時全ロールバック

**タスク**:
- [x] `bulk_request()` メソッド追加
- [ ] `BulkBuilder` クラス追加（将来対応）
- [x] テスト作成

---

## Phase 5: Auto Chunking

**目的**: 100件超の追加/更新を自動分割

**タスク**:
- [x] `add_many()` に自動チャンク分割実装
- [x] `update_many()` に自動チャンク分割実装
- [x] テスト作成

---

## 更新履歴

- 2026-01-21: Phase 1-5 実装完了（67テスト全パス）
- 2026-01-21: 初版作成
