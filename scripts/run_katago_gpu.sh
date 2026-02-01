#!/bin/bash
# Wrapper to run KataGo on GPU (Optimized for WSL2)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
export PATH="$PROJECT_ROOT/bin:$PATH"

# THE WSL2 GPU FIX: Use Windows host driver libs and ICD, AND local libs
# We need to find where pip installed nvidia-cublas (system venv) and nvidia-cudnn (local gpu_libs)
VENV_LIB="$PROJECT_ROOT/.venv/lib/python3.10/site-packages"
CUBLAS_LIB="$VENV_LIB/nvidia/cublas/lib"
# Local install of cudnn 8.9.7
CUDNN_LIB="$PROJECT_ROOT/gpu_libs/nvidia/cudnn/lib"

export LD_LIBRARY_PATH="$CUBLAS_LIB:$CUDNN_LIB:/usr/lib/wsl/lib:$LD_LIBRARY_PATH"

MAIN_MODEL="$PROJECT_ROOT/models/main_b18.bin.gz"
HUMAN_MODEL="$PROJECT_ROOT/models/human_model.bin.gz"
CONFIG_PATH="$PROJECT_ROOT/models/human.cfg"

# Optional rank override
ARGS=()
if [ -n "$BOT_RANK" ]; then
    echo "Setting KataGo rank profile to $BOT_RANK" >&2
    ARGS+=("-override-config" "humanSLProfile=$BOT_RANK")
fi

# Use the GPU binary (CUDA version matches our local libs)
exec katago-gpu gtp -model "$MAIN_MODEL" -human-model "$HUMAN_MODEL" -config "$CONFIG_PATH" "${ARGS[@]}" "$@"
