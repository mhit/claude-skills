#!/bin/bash
# KINTONE CLI ラッパー
# Usage: kintone.sh <command> [options]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Python パスを追加
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

show_help() {
    cat << 'EOF'
KINTONE CLI - KINTONE REST API を操作するコマンドラインツール

Usage: kintone <command> [options]

Commands:
  apps [--name <name>]         アプリ一覧を取得
  schema <app_id>              スキーマ（フィールド定義）を表示
  schema list                  キャッシュ済みスキーマ一覧
  schema clear [app_id]        スキーマキャッシュをクリア
  get <app_id> <record_id>     レコードを1件取得
  search <app_id> [query]      レコードを検索（--all で全件取得）
  add <app_id> <json>          レコードを追加
  update <app_id> <id> <json>  レコードを更新
  delete <app_id> <ids>        レコードを削除（カンマ区切り）
  status <app_id> <id> <action>  ステータスを更新（ワークフロー）
  comment <app_id> <id> <subcmd> コメント操作（add/list/delete）
  file upload <path>           ファイルをアップロード
  file download <fileKey>      ファイルをダウンロード
  file list <app_id> <record_id> <field>  添付ファイル一覧
  query <text>                 自然言語クエリを変換
  help                         このヘルプを表示

Options:
  --json                       JSON形式で出力
  --refresh                    キャッシュを更新（schema）
  --limit N                    取得件数制限（search）
  --offset N                   オフセット（search）
  --all                        全件取得（search、Cursor API使用）
  --assignee USER              担当者（status）
  --output PATH                出力先パス（file download）

Environment Variables:
  KINTONE_DOMAIN              KINTONE ドメイン（必須）
  KINTONE_API_TOKEN           API トークン（必須）
  KINTONE_DEFAULT_APP         デフォルトアプリID
  KINTONE_CACHE_DIR           キャッシュディレクトリ
  KINTONE_CACHE_TTL           キャッシュ有効期限（秒）

Examples:
  # アプリ一覧
  kintone apps
  kintone apps --name "顧客"

  # スキーマ確認
  kintone schema 123
  kintone schema list           # キャッシュ一覧
  kintone schema clear          # 全キャッシュクリア
  kintone schema clear 123      # 特定アプリのキャッシュクリア

  # レコード取得
  kintone get 123 1

  # 検索
  kintone search 123 'ステータス = "完了"'
  kintone search 123 --query 'ステータスが完了'  # 自然言語

  # レコード追加
  kintone add 123 '{"タイトル": "新規タスク", "担当者": "田中"}'

  # レコード更新
  kintone update 123 1 '{"ステータス": "完了"}'

  # レコード削除
  kintone delete 123 1,2,3

  # 全件取得（500件超）
  kintone search 123 --all
  kintone search 123 'ステータス = "完了"' --all

  # ステータス更新（ワークフロー）
  kintone status 123 1 "承認"
  kintone status 123 1 "承認" --assignee tanaka

  # コメント操作
  kintone comment 123 1 add "確認しました"
  kintone comment 123 1 list
  kintone comment 123 1 delete 456

  # ファイル操作
  kintone file upload ./document.pdf
  kintone file download abc123def456
  kintone file list 123 1 添付ファイル  # 添付ファイル一覧

EOF
}

# コマンド判定
case "$1" in
    apps)
        shift
        python3 "${SCRIPT_DIR}/kintone_crud.py" apps "$@"
        ;;

    schema)
        shift
        SUBCMD="$1"

        # サブコマンド判定
        if [[ "$SUBCMD" == "list" ]]; then
            shift
            python3 "${SCRIPT_DIR}/kintone_schema.py" list "$@"
        elif [[ "$SUBCMD" == "clear" ]]; then
            shift
            APP_ID="$1"
            if [[ -n "$APP_ID" && ! "$APP_ID" =~ ^-- ]]; then
                shift
                python3 "${SCRIPT_DIR}/kintone_schema.py" clear --app "$APP_ID" "$@"
            else
                python3 "${SCRIPT_DIR}/kintone_schema.py" clear "$@"
            fi
        else
            # app_id として扱う
            APP_ID="$SUBCMD"
            shift
            if [[ -z "$APP_ID" ]]; then
                echo "Error: App ID is required"
                echo "Usage: kintone schema <app_id> [--refresh] [--json]"
                echo "       kintone schema list"
                echo "       kintone schema clear [app_id]"
                exit 1
            fi

            EXTRA_ARGS=""
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --refresh) EXTRA_ARGS="$EXTRA_ARGS refresh"; shift ;;
                    --json) EXTRA_ARGS="$EXTRA_ARGS --json"; shift ;;
                    *) shift ;;
                esac
            done

            if [[ "$EXTRA_ARGS" == *"refresh"* ]]; then
                python3 "${SCRIPT_DIR}/kintone_schema.py" refresh --app "$APP_ID" $EXTRA_ARGS
            else
                python3 "${SCRIPT_DIR}/kintone_schema.py" get --app "$APP_ID" $EXTRA_ARGS
            fi
        fi
        ;;

    get)
        shift
        APP_ID="$1"
        RECORD_ID="$2"
        shift 2

        if [[ -z "$APP_ID" || -z "$RECORD_ID" ]]; then
            echo "Error: App ID and Record ID are required"
            echo "Usage: kintone get <app_id> <record_id>"
            exit 1
        fi

        python3 "${SCRIPT_DIR}/kintone_crud.py" get --app "$APP_ID" --id "$RECORD_ID" "$@"
        ;;

    search)
        shift
        APP_ID="$1"
        shift

        if [[ -z "$APP_ID" ]]; then
            echo "Error: App ID is required"
            echo "Usage: kintone search <app_id> [query] [--limit N] [--offset N]"
            exit 1
        fi

        # 次の引数がオプションでなければクエリとして扱う
        QUERY=""
        if [[ -n "$1" && ! "$1" =~ ^-- ]]; then
            QUERY="$1"
            shift
        fi

        python3 "${SCRIPT_DIR}/kintone_crud.py" search --app "$APP_ID" --query "$QUERY" "$@"
        ;;

    add)
        shift
        APP_ID="$1"
        DATA="$2"
        shift 2

        if [[ -z "$APP_ID" || -z "$DATA" ]]; then
            echo "Error: App ID and JSON data are required"
            echo "Usage: kintone add <app_id> '<json_data>'"
            exit 1
        fi

        python3 "${SCRIPT_DIR}/kintone_crud.py" add --app "$APP_ID" --data "$DATA" "$@"
        ;;

    update)
        shift
        APP_ID="$1"
        RECORD_ID="$2"
        DATA="$3"
        shift 3

        if [[ -z "$APP_ID" || -z "$RECORD_ID" || -z "$DATA" ]]; then
            echo "Error: App ID, Record ID, and JSON data are required"
            echo "Usage: kintone update <app_id> <record_id> '<json_data>'"
            exit 1
        fi

        python3 "${SCRIPT_DIR}/kintone_crud.py" update --app "$APP_ID" --id "$RECORD_ID" --data "$DATA" "$@"
        ;;

    delete)
        shift
        APP_ID="$1"
        IDS="$2"
        shift 2

        if [[ -z "$APP_ID" || -z "$IDS" ]]; then
            echo "Error: App ID and Record IDs are required"
            echo "Usage: kintone delete <app_id> <id1,id2,...>"
            exit 1
        fi

        python3 "${SCRIPT_DIR}/kintone_crud.py" delete --app "$APP_ID" --ids "$IDS" "$@"
        ;;

    status)
        shift
        APP_ID="$1"
        RECORD_ID="$2"
        ACTION="$3"
        shift 3

        if [[ -z "$APP_ID" || -z "$RECORD_ID" || -z "$ACTION" ]]; then
            echo "Error: App ID, Record ID, and Action are required"
            echo "Usage: kintone status <app_id> <record_id> <action> [--assignee <user>]"
            exit 1
        fi

        python3 "${SCRIPT_DIR}/kintone_crud.py" status --app "$APP_ID" --id "$RECORD_ID" --action "$ACTION" "$@"
        ;;

    comment)
        shift
        APP_ID="$1"
        RECORD_ID="$2"
        SUBCMD="$3"
        shift 3

        if [[ -z "$APP_ID" || -z "$RECORD_ID" || -z "$SUBCMD" ]]; then
            echo "Error: App ID, Record ID, and subcommand are required"
            echo "Usage: kintone comment <app_id> <record_id> <add|list|delete> [options]"
            exit 1
        fi

        case "$SUBCMD" in
            add)
                TEXT="$1"
                shift
                if [[ -z "$TEXT" ]]; then
                    echo "Error: Comment text is required"
                    echo "Usage: kintone comment <app_id> <record_id> add <text>"
                    exit 1
                fi
                python3 "${SCRIPT_DIR}/kintone_crud.py" comment --app "$APP_ID" --id "$RECORD_ID" --comment-action add --text "$TEXT" "$@"
                ;;
            list)
                python3 "${SCRIPT_DIR}/kintone_crud.py" comment --app "$APP_ID" --id "$RECORD_ID" --comment-action list "$@"
                ;;
            delete)
                COMMENT_ID="$1"
                shift
                if [[ -z "$COMMENT_ID" ]]; then
                    echo "Error: Comment ID is required"
                    echo "Usage: kintone comment <app_id> <record_id> delete <comment_id>"
                    exit 1
                fi
                python3 "${SCRIPT_DIR}/kintone_crud.py" comment --app "$APP_ID" --id "$RECORD_ID" --comment-action delete --comment-id "$COMMENT_ID" "$@"
                ;;
            *)
                echo "Unknown comment subcommand: $SUBCMD"
                echo "Available: add, list, delete"
                exit 1
                ;;
        esac
        ;;

    file)
        shift
        SUBCMD="$1"
        shift

        case "$SUBCMD" in
            upload)
                FILE_PATH="$1"
                shift
                if [[ -z "$FILE_PATH" ]]; then
                    echo "Error: File path is required"
                    echo "Usage: kintone file upload <path>"
                    exit 1
                fi
                python3 "${SCRIPT_DIR}/kintone_file.py" upload --file "$FILE_PATH" "$@"
                ;;
            download)
                FILE_KEY="$1"
                shift
                if [[ -z "$FILE_KEY" ]]; then
                    echo "Error: File key is required"
                    echo "Usage: kintone file download <fileKey> [--output <path>]"
                    exit 1
                fi
                python3 "${SCRIPT_DIR}/kintone_file.py" download --key "$FILE_KEY" "$@"
                ;;
            list)
                APP_ID="$1"
                RECORD_ID="$2"
                FIELD_CODE="$3"
                shift 3 2>/dev/null || true
                if [[ -z "$APP_ID" || -z "$RECORD_ID" || -z "$FIELD_CODE" ]]; then
                    echo "Error: App ID, Record ID, and Field code are required"
                    echo "Usage: kintone file list <app_id> <record_id> <field_code>"
                    exit 1
                fi
                python3 "${SCRIPT_DIR}/kintone_file.py" list --app "$APP_ID" --record "$RECORD_ID" --field "$FIELD_CODE" "$@"
                ;;
            *)
                echo "Unknown file command: $SUBCMD"
                echo "Available: upload, download, list"
                exit 1
                ;;
        esac
        ;;

    query)
        shift
        TEXT="$1"
        if [[ -z "$TEXT" ]]; then
            echo "Error: Query text is required"
            echo "Usage: kintone query '<natural language query>'"
            exit 1
        fi
        python3 "${SCRIPT_DIR}/kintone_search.py" --natural "$TEXT"
        ;;

    help|--help|-h)
        show_help
        ;;

    *)
        if [[ -z "$1" ]]; then
            show_help
        else
            echo "Unknown command: $1"
            echo "Run 'kintone help' for usage information"
            exit 1
        fi
        ;;
esac
