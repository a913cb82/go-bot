#!/bin/bash

MODELS_DIR="models"
HUMAN_MODEL_URL="https://github.com/lightvector/KataGo/releases/download/v1.15.0/b18c384nbt-humanv0.bin.gz"
MAIN_MODEL_URL="https://media.katagotraining.org/uploaded/networks/models/kata1/kata1-b18c384nbt-s9996604416-d4316597426.bin.gz"

mkdir -p "$MODELS_DIR"

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

# Clean up invalid small files from previous failed downloads
clean_invalid() {
    local file=$1
    if [ -f "$file" ]; then
        # Use stat -c%s for Linux, stat -f%z for macOS
        local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        if [ -n "$size" ] && [ "$size" -lt 1000000 ]; then
            echo "Removing invalid/small file: $file"
            rm "$file"
        fi
    fi
}

clean_invalid "$MODELS_DIR/main_b18.bin.gz"
clean_invalid "$MODELS_DIR/human_model.bin.gz"

download_file "$HUMAN_MODEL_URL" "$MODELS_DIR/human_model.bin.gz"
download_file "$MAIN_MODEL_URL" "$MODELS_DIR/main_b18.bin.gz"
