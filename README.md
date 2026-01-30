# Go Bot Project

This project contains Python-based Go bots and configuration to run them on [Online-Go.com (OGS)](https://online-go.com) using `gtp2ogs`.

## Prerequisites

1.  **Node.js & npm**: Required to run `gtp2ogs`.
    ```bash
    # Install gtp2ogs globally
    npm install -g gtp2ogs
    ```
2.  **Python 3**: For the random bot and helper scripts.
3.  **KataGo**: (Optional) Required for the `katago_human` bot.

## Setup

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt # (Ensure sgfmill is installed)
    ```

2.  **GPU Setup (WSL2/Linux)**:
    To enable the GPU bot, you need to install specific CUDA libraries locally to match the KataGo binary:
    ```bash
    mkdir -p gpu_libs
    pip install nvidia-cudnn-cu12==8.9.7.29 --target gpu_libs --no-deps
    ```
    *Note: The `scripts/run_katago_gpu.sh` script is configured to look in `gpu_libs` and your python environment for the required libraries.*

3.  **Bot Accounts**:
    - You need a separate account on OGS for your bot.
    - Ask a moderator to flag the account as a "Bot".
    - Log in to the bot account, go to **Settings** -> **Bot Settings**, and generate an **API Key**.

3.  **Configuration**:
    - Create a `.env` file from `.env.example` and add your OGS Bot API Key:
        ```bash
        cp .env.example .env
        # Edit .env and replace 'your_api_key_here'
        ```
    - The configuration files in `configs/` use `"YOUR_API_KEY_HERE"` as a placeholder. The API key should be passed via the `--apikey` flag or environment variable.

## Running the Bots

To run the bots, you need to load the environment variables from `.env` and pass the API key to `gtp2ogs`.

### Random Bot
Plays random legal moves. Extremely fast.
```bash
export $(cat .env | xargs) && gtp2ogs -c configs/gtp2ogs.random.json5 --apikey $OGS_API_KEY
```

### KataGo Human SL Bot (CPU Optimized)
Uses KataGo with a Human SL model. Optimized for your 8-core CPU.
*   **Performance:** ~11 seconds per move.
*   **Concurrency:** Limited to 5 games to ensure stability.
```bash
export $(cat .env | xargs) && gtp2ogs -c configs/gtp2ogs.katago_cpu.json5 --apikey $OGS_API_KEY
```

### KataGo Human SL Bot (GPU Optimized)
Uses KataGo with CUDA 12 backend on your GTX 1080 Ti.
*   **Performance:** ~5 seconds per move.
*   **Concurrency:** Can handle more concurrent games.
```bash
export $(cat .env | xargs) && gtp2ogs -c configs/gtp2ogs.katago_gpu.json5 --apikey $OGS_API_KEY
```

## Benchmarking Latency
Verify move generation speed:
```bash
# Benchmark Random Bot
python3 scripts/benchmark_bot.py python3 scripts/random_gtp.py

# Benchmark KataGo CPU Bot
python3 scripts/benchmark_bot.py ./scripts/run_katago_cpu.sh

# Benchmark KataGo GPU Bot
python3 scripts/benchmark_bot.py ./scripts/run_katago_gpu.sh
```

## Directory Structure
-   `src/go_bot/`: Python source code.
-   `scripts/`: Helper scripts (`benchmark_bot.py`, `run_katago_cpu.sh`, `run_katago_gpu.sh`).
-   `configs/`: `gtp2ogs` configurations.
-   `bin/`: Compiled binaries (`katago-cpu`, `katago-gpu`).
-   `models/`: KataGo models (`main_b18.bin.gz`, `human_model.bin.gz`).
-   `gpu_libs/`: Local CUDA libraries for GPU bot.
