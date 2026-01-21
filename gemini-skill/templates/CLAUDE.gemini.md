# Gemini Integration for Claude Code

This file teaches Claude Code how to use Gemini CLI in your project.
Copy this to your project's `CLAUDE.md` and customize as needed.

## Environment Setup

```bash
# Required
export GEMINI_API_KEY="your-api-key"

# Optional (customize defaults)
export GEMINI_DEFAULT_MODEL="gemini-2.5-flash"  # Default model
export GEMINI_TIMEOUT="900"                      # Timeout in seconds (default: 15 min)
```

## Command Definitions

When the following phrases are used, execute the corresponding commands:

| User Says | Execute |
|-----------|---------|
| `gemini "question"` | `gemini-call.sh --task quick "question"` |
| `gemini-review <file>` | `cat <file> \| gemini-call.sh --stdin --task review "Review this code"` |
| `gemini-search "query"` | `gemini -m gemini-2.5-flash "@search query"` |
| `gemini-ocr <image>` | `gemini -m gemini-3-pro-preview "@<image> Extract text from this image"` |
| `gemini-analyze <dir>` | `gemini -m gemini-2.5-flash "@<dir> Analyze this codebase"` |

## Auto-trigger Rules

Automatically use Gemini when:

| Condition | Action | Reason |
|-----------|--------|--------|
| File size > 100KB | Use `/gemini-analyze` | Exceeds Claude's context |
| Question contains "latest" or "current" | Use `/gemini-search` | Claude's knowledge may be outdated |
| PDF or image file | Use `/gemini-ocr` | Gemini's multimodal is superior |
| UI/UX design request | Use `/gemini-design` | Gemini 3 excels at design |
| Before production deploy | Use `/gemini-review` | Second opinion for safety |

## Model Selection by Task

| Task Type | Model | Why |
|-----------|-------|-----|
| OCR (image/PDF) | `gemini-3-pro-preview` | Best multimodal |
| UI/UX Design | `gemini-3-flash-preview` | Design-focused |
| Code Review | `gemini-2.5-pro` | Deep thinking model |
| Large File Analysis | `gemini-2.5-flash` | 1M token context, cost-effective |
| Quick Questions | `gemini-2.5-flash-lite` | Fastest |

## Usage Examples

### Review Code Changes

```bash
git diff | gemini-call.sh --stdin --task review "Review these changes for bugs and security issues"
```

### Analyze Large Logs

```bash
cat production.log | gemini-call.sh --stdin --task analyze "Find error patterns and root causes"
```

### Get Latest Information

```bash
gemini -m gemini-2.5-flash "@search React 19 new features 2026"
```

### Extract Text from Screenshot

```bash
gemini -m gemini-3-pro-preview "@./screenshot.png What does this screenshot show?"
```

## Project-specific Customizations

Add your project-specific Gemini integrations below:

```markdown
# Example: Custom review command for this project
- `review-pr` → `gh pr diff | gemini-call.sh --stdin --task review "Review this PR"`
```
