#!/bin/bash
# gemini-call.sh - Gemini CLI wrapper for Claude Code skill
# Usage: gemini-call.sh [options] "prompt"
#
# Options:
#   -m, --model MODEL    Model to use (see below for recommendations)
#   -f, --file FILE      File to include (can be repeated)
#   -t, --timeout SECS   Timeout in seconds (default: 900 = 15 min)
#   -j, --json           Output as JSON
#   -y, --yolo           Auto-approve all actions
#   --stdin              Read content from stdin (pipe support)
#   --task TASK          Auto-select model by task type
#   -h, --help           Show this help
#
# Environment variables:
#   GEMINI_API_KEY       API key (required by gemini CLI)
#   GEMINI_DEFAULT_MODEL Default model (optional)
#   GEMINI_TIMEOUT       Timeout in seconds (default: 900 = 15 min)
#
# Model recommendations by task:
#   ocr      → gemini-3-pro-preview (multimodal best)
#   design   → gemini-3-flash-preview (balanced)
#   review   → gemini-2.5-pro (thinking model)
#   analyze  → gemini-2.5-flash (cost-effective, 1M tokens)
#   quick    → gemini-2.5-flash-lite (fastest)

set -euo pipefail

# Model mapping by task
declare -A TASK_MODELS=(
    ["ocr"]="gemini-3-pro-preview"
    ["design"]="gemini-3-flash-preview"
    ["review"]="gemini-2.5-pro"
    ["analyze"]="gemini-2.5-flash"
    ["quick"]="gemini-2.5-flash-lite"
    ["default"]="gemini-2.5-flash"
)

# Defaults (can be overridden by environment variables)
MODEL="${GEMINI_DEFAULT_MODEL:-}"
TASK=""
TIMEOUT="${GEMINI_TIMEOUT:-900}"
JSON_OUTPUT=false
YOLO_MODE=false
READ_STDIN=false
FILES=()
PROMPT=""
STDIN_CONTENT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        --task)
            TASK="$2"
            shift 2
            ;;
        -f|--file)
            FILES+=("$2")
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -j|--json)
            JSON_OUTPUT=true
            shift
            ;;
        -y|--yolo)
            YOLO_MODE=true
            shift
            ;;
        --stdin)
            READ_STDIN=true
            shift
            ;;
        -h|--help)
            head -25 "$0" | tail -24
            exit 0
            ;;
        --)
            shift
            PROMPT="$*"
            break
            ;;
        *)
            if [[ -z "$PROMPT" ]]; then
                PROMPT="$1"
            else
                PROMPT="$PROMPT $1"
            fi
            shift
            ;;
    esac
done

# Select model based on task if not explicitly specified
if [[ -z "$MODEL" ]]; then
    if [[ -n "$TASK" && -n "${TASK_MODELS[$TASK]:-}" ]]; then
        MODEL="${TASK_MODELS[$TASK]}"
    else
        MODEL="${TASK_MODELS[default]}"
    fi
fi

# Validate
if [[ -z "$PROMPT" ]]; then
    echo "Error: No prompt provided" >&2
    exit 1
fi

# Build command
CMD=(gemini)
CMD+=(-m "$MODEL")

if $JSON_OUTPUT; then
    CMD+=(-o json)
fi

if $YOLO_MODE; then
    CMD+=(--yolo)
fi

# Read from stdin if --stdin flag is set
if $READ_STDIN; then
    if [[ ! -t 0 ]]; then
        STDIN_CONTENT="$(cat)"
        echo "Read $(echo "$STDIN_CONTENT" | wc -c) bytes from stdin" >&2
    else
        echo "Warning: --stdin specified but no input piped" >&2
    fi
fi

# Add files to prompt if specified
if [[ ${#FILES[@]} -gt 0 ]]; then
    FILE_CONTENT=""
    for file in "${FILES[@]}"; do
        if [[ -f "$file" ]]; then
            FILE_CONTENT+="--- File: $file ---"$'\n'
            FILE_CONTENT+="$(cat "$file")"$'\n\n'
        else
            echo "Warning: File not found: $file" >&2
        fi
    done
    PROMPT="$FILE_CONTENT$PROMPT"
fi

# Add stdin content to prompt
if [[ -n "$STDIN_CONTENT" ]]; then
    PROMPT="--- Input ---"$'\n'"$STDIN_CONTENT"$'\n\n'"$PROMPT"
fi

CMD+=("$PROMPT")

# Show selected model
echo "Using model: $MODEL" >&2

# Execute with timeout
timeout "$TIMEOUT" "${CMD[@]}"
