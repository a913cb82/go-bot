#!/bin/bash
# Wrapper to run KataGo on GPU (Optimized for WSL2)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
export PATH="$PROJECT_ROOT/bin:$PATH"

# THE WSL2 GPU FIX: Use Windows host driver libs and ICD, AND local libs
# We search in gpu_libs (manual install) and .venv (pip install)
VENV_PACKAGES="$PROJECT_ROOT/.venv/lib/python3.10/site-packages"
GPU_LIBS="$PROJECT_ROOT/gpu_libs"

# Search paths for cublas and cudnn
CUBLAS_PATH=$(find "$GPU_LIBS" "$VENV_PACKAGES" -name "libcublas.so.12" -printf '%h\n' 2>/dev/null | head -n 1)
CUDNN_PATH=$(find "$GPU_LIBS" "$VENV_PACKAGES" -name "libcudnn.so.8" -printf '%h\n' 2>/dev/null | head -n 1)

export LD_LIBRARY_PATH="$CUBLAS_PATH:$CUDNN_PATH:/usr/lib/wsl/lib:$LD_LIBRARY_PATH"

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
