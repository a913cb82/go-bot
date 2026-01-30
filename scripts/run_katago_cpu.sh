#!/bin/bash
# Wrapper to run KataGo on CPU (Eigen AVX2)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
export PATH="$PROJECT_ROOT/bin:$PATH"

MAIN_MODEL="$PROJECT_ROOT/models/main_b18.bin.gz"
HUMAN_MODEL="$PROJECT_ROOT/models/human_model.bin.gz"
CONFIG_PATH="$PROJECT_ROOT/models/human.cfg"

# Optional rank override
ARGS=()
if [ -n "$BOT_RANK" ]; then
    ARGS+=("-override-config" "humanSLProfile=$BOT_RANK")
fi

# Use the CPU binary
exec katago-cpu gtp -model "$MAIN_MODEL" -human-model "$HUMAN_MODEL" -config "$CONFIG_PATH" "${ARGS[@]}" "$@"
