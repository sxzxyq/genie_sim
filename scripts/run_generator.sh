#!/usr/bin/env bash

set -euo pipefail

PY_PATH="/geniesim/main/source/geniesim/generator/app.py"
PYTHON="/geniesim/generator_env/bin/python"
TARGET_PATH="/geniesim/main/source/geniesim/benchmark/config/llm_task"

# Fail early if the script is missing
[[ -f "$PY_PATH" ]] || { echo "ERROR: $PY_PATH not found" >&2; exit 1; }
[[ -d "$TARGET_PATH" ]] || { echo "ERROR: $TARGET_PATH not found" >&2; exit 1; }

TARGET_UID=$(stat -c '%u' "$TARGET_PATH")
TARGET_GID=$(stat -c '%g' "$TARGET_PATH")
RUNTIME_HOME="/tmp/geniesim_generator_${TARGET_UID}"

mkdir -p "$RUNTIME_HOME"
chmod 777 "$RUNTIME_HOME"

sudo setpriv \
    --reuid="${TARGET_UID}" \
    --regid="${TARGET_GID}" \
    --clear-groups \
    env \
    HOME="$RUNTIME_HOME" \
    XDG_CACHE_HOME="$RUNTIME_HOME/.cache" \
    PYTHONPATH="${PYTHONPATH:-}${PYTHONPATH:+:}/geniesim/main/source" \
    "$PYTHON" "$PY_PATH" "$@"
