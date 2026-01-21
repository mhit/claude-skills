#!/bin/bash
# gemini-call.sh - Gemini CLI wrapper for Claude Code skill
# Usage: gemini-call.sh [options] "prompt"
#
# Options:
#   -m, --model MODEL    Model to use (see below for recommendations)
#   -f, --file FILE      File to include (can be repeated)
#   -t, --timeout SECS   Timeout in seconds (default: 300)
#   -j, --json           Output as JSON
#   -y, --yolo           Auto-approve all actions
#   --task TASK          Auto-select model by task type
#   -h, --help           Show this help
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

# Defaults
MODEL=""
TASK=""
TIMEOUT=300
JSON_OUTPUT=false
YOLO_MODE=false
FILES=()
PROMPT=""

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
        -h|--help)
            head -20 "$0" | tail -19
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

CMD+=("$PROMPT")

# Show selected model
echo "Using model: $MODEL" >&2

# Execute with timeout
timeout "$TIMEOUT" "${CMD[@]}"
