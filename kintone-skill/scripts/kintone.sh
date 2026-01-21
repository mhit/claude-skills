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
  schema <app_id>              スキーマ（フィールド定義）を表示
  get <app_id> <record_id>     レコードを1件取得
  search <app_id> [query]      レコードを検索
  add <app_id> <json>          レコードを追加
  update <app_id> <id> <json>  レコードを更新
  delete <app_id> <ids>        レコードを削除（カンマ区切り）
  file upload <path>           ファイルをアップロード
  file download <fileKey>      ファイルをダウンロード
  query <text>                 自然言語クエリを変換
  help                         このヘルプを表示

Options:
  --json                       JSON形式で出力
  --refresh                    キャッシュを更新（schema）
  --limit N                    取得件数制限（search）
  --offset N                   オフセット（search）
  --output PATH                出力先パス（file download）

Environment Variables:
  KINTONE_DOMAIN              KINTONE ドメイン（必須）
  KINTONE_API_TOKEN           API トークン（必須）
  KINTONE_DEFAULT_APP         デフォルトアプリID
  KINTONE_CACHE_DIR           キャッシュディレクトリ
  KINTONE_CACHE_TTL           キャッシュ有効期限（秒）

Examples:
  # スキーマ確認
  kintone schema 123

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

  # ファイル操作
  kintone file upload ./document.pdf
  kintone file download abc123def456

EOF
}

# コマンド判定
case "$1" in
    schema)
        shift
        APP_ID="$1"
        shift
        if [[ -z "$APP_ID" ]]; then
            echo "Error: App ID is required"
            echo "Usage: kintone schema <app_id> [--refresh] [--json]"
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
                python3 "${SCRIPT_DIR}/kintone_file.py" list "$@"
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
