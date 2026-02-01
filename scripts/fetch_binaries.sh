#!/bin/bash
# Fetch KataGo engine binaries into bin/ (binaries are NOT committed; bin/ is git-ignored).
#
# Provenance:
#   Upstream: https://github.com/lightvector/KataGo/releases/tag/v1.16.4
#   Version:  KataGo v1.16.4 (git revision 4b8de63bea2bd8790db96cd6f8daf86dc87be6f7)
#
#   CPU -> bin/katago-cpu (Eigen AVX2 build)
#     https://github.com/lightvector/KataGo/releases/download/v1.16.4/katago-v1.16.4-eigenavx2-linux-x64.zip
#   GPU -> bin/katago-gpu (CUDA 12.5 / cuDNN 8.9.7 build; needs the gpu_libs setup in the README)
#     https://github.com/lightvector/KataGo/releases/download/v1.16.4/katago-v1.16.4-cuda12.5-cudnn8.9.7-linux-x64.zip
#
#   Expected SHA256 of the installed binaries (verified 2026-09-19;
#   re-check any time with `sha256sum bin/katago-*`):
#     CPU: e24fc4b8b60af13fc9f96d2858fe6e2fcc242b225c16d12aca1310fc01ea2d79
#     GPU: e5444b1dea30e1317228cbd83a638525ac5c476f4d45444b6e60ddd1995cd263
#
# Usage: ./scripts/fetch_binaries.sh
# Do NOT commit binaries or logs (see .gitignore: bin/, gtp_logs/).

BIN_DIR="bin"
VERSION="v1.16.4"
BASE_URL="https://github.com/lightvector/KataGo/releases/download/${VERSION}"
CPU_ZIP="katago-v1.16.4-eigenavx2-linux-x64.zip"
GPU_ZIP="katago-v1.16.4-cuda12.5-cudnn8.9.7-linux-x64.zip"

CPU_SHA="e24fc4b8b60af13fc9f96d2858fe6e2fcc242b225c16d12aca1310fc01ea2d79"
GPU_SHA="e5444b1dea30e1317228cbd83a638525ac5c476f4d45444b6e60ddd1995cd263"

mkdir -p "$BIN_DIR"

download_file() {
    local url=$1
    local dest=$2

    if [ -f "$dest" ]; then
        echo "$dest already exists. Skipping."
        return
    fi

    echo "Downloading $url to $dest..."
    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$dest" "$url"
    elif command -v wget >/dev/null 2>&1; then
        wget -O "$dest" "$url"
    else
        echo "Error: Neither curl nor wget found. Please install one of them."
        exit 1
    fi
}

install_binary() {
    local zip_name=$1
    local target=$2
    local expected_sha=$3

    download_file "${BASE_URL}/${zip_name}" "${BIN_DIR}/${zip_name}"

    if [ -f "$target" ]; then
        echo "$target already exists. Skipping install."
    else
        echo "Extracting katago from ${zip_name} to ${target}..."
        unzip -o -j "${BIN_DIR}/${zip_name}" katago -d "$BIN_DIR" >/dev/null
        mv "${BIN_DIR}/katago" "$target"
        chmod +x "$target"
    fi

    if command -v sha256sum >/dev/null 2>&1; then
        local actual
        actual=$(sha256sum "$target" | cut -d' ' -f1)
        if [ "$actual" = "$expected_sha" ]; then
            echo "Checksum OK: $target"
        else
            echo "WARNING: checksum mismatch for $target"
            echo "  expected: $expected_sha"
            echo "  actual:   $actual"
        fi
    fi
    rm -f "${BIN_DIR}/${zip_name}"
}

install_binary "$CPU_ZIP" "${BIN_DIR}/katago-cpu" "$CPU_SHA"
install_binary "$GPU_ZIP" "${BIN_DIR}/katago-gpu" "$GPU_SHA"

echo "Verify with: ./bin/katago-cpu version && ./bin/katago-gpu version"
