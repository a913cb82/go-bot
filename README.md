# OGS KataGo Human SL Bot

This project connects [KataGo](https://github.com/lightvector/KataGo) (using the Human Supervised Learning model) to [Online-Go.com (OGS)](https://online-go.com) using the [gtp2ogs](https://github.com/pro-forma/gtp2ogs) bridge.

The "Human SL" model is specifically trained to mimic human play styles rather than playing optimally, making it a more natural opponent for human players on OGS.

## Prerequisites

- **Node.js & npm**: To run the `gtp2ogs` bridge.
  ```bash
  npm install -g gtp2ogs
  ```
- **Python 3**: For helper scripts and the random testing bot.
- **KataGo Binaries**: Pre-compiled CPU and GPU binaries are included in `bin/`.

## Setup

### 1. Install Dependencies
```bash
pip install sgfmill
```

### 2. Fetch Models
Download the required neural network models:
```bash
./scripts/fetch_models.sh
```
This script will create the `models/` directory and download the main network and the human SL weights. The engine configuration (`models/human.cfg`) is already included in the repository.

### 3. OGS API Key & Configuration
1. Create a bot account on OGS.
2. Ask a moderator to flag the account as a "Bot".
3. Log in to the bot account, go to **Settings** -> **Bot Settings**, and generate an **API Key**.
4. Create your local `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and replace placeholders with your actual key and desired rank
   ```
   *Available ranks include: `rank_30k`, `rank_20k`, `rank_10k`, `rank_5k`, `rank_1k`, `rank_1d`, `rank_9d`, etc.*

### 4. GPU Setup (WSL2 / Linux) - Optional
To enable sub-second moves using your GPU without installing the full CUDA toolkit system-wide, install the required libraries into a local directory:
```bash
mkdir -p gpu_libs
pip install nvidia-cudnn-cu12==8.9.7.29 --target gpu_libs --no-deps
```
*The `scripts/run_katago_gpu.sh` script is pre-configured to find these libraries.*

## Running the Bot

Always load your API key from the `.env` file when starting the bot.

### KataGo Human SL (GPU Optimized)
**Recommended.** High performance inference. Expected sub-second move time on modern GPUs (~1.5GB VRAM per instance).
```bash
export $(grep -v '^#' .env | xargs) && gtp2ogs -c configs/gtp2ogs.katago_gpu.json5 --apikey $OGS_API_KEY
```

### KataGo Human SL (CPU Optimized)
Fallback for systems without a compatible GPU. Move time depends on CPU performance; expected ~10-20s per move on modern multi-core CPUs.
```bash
export $(grep -v '^#' .env | xargs) && gtp2ogs -c configs/gtp2ogs.katago_cpu.json5 --apikey $OGS_API_KEY
```

### Random Bot
A lightweight Python bot that plays random legal moves. Useful for testing OGS connectivity.
```bash
export $(grep -v '^#' .env | xargs) && gtp2ogs -c configs/gtp2ogs.random.json5 --apikey $OGS_API_KEY
```

## Running Multiple Bots

To run multiple bots concurrently, redirect their output to separate log files in the `gtp_logs/` directory and run them in the background using `&`:

```bash
# Bot 1: 20k account
BOT_RANK=rank_20k gtp2ogs -c configs/gtp2ogs.katago_gpu.json5 --apikey KEY1 > gtp_logs/bot20k.log 2>&1 &

# Bot 2: 5k account
BOT_RANK=rank_5k gtp2ogs -c configs/gtp2ogs.katago_gpu.json5 --apikey KEY2 > gtp_logs/bot5k.log 2>&1 &
```

### Managing Bots
- **Monitor activity:** Use `tail -f gtp_logs/bot20k.log` to watch a bot's real-time logs.
- **Verify Rank:** Look for `DEBUG: Setting KataGo rank profile to...` in the log file to confirm the rank was passed correctly.
- **List running instances:** Use `pgrep -af gtp2ogs` to see all active bots and their ranks.
- **Stop all bots:** Use `pkill -f gtp2ogs` to kill all running instances.

*Note: Each KataGo instance uses ~1.5GB of VRAM. Ensure your GPU has enough memory to support the desired number of concurrent bots.*

## Benchmarking
You can verify the move generation speed locally without connecting to OGS:
```bash
# Benchmark GPU Bot
python3 scripts/benchmark_bot.py ./scripts/run_katago_gpu.sh

# Benchmark CPU Bot
python3 scripts/benchmark_bot.py ./scripts/run_katago_cpu.sh
```

## Project Structure
- `bin/`: KataGo engine binaries (`katago-cpu`, `katago-gpu`).
- `configs/`: `gtp2ogs` JSON5 configuration files.
- `models/`: KataGo neural network models and configuration.
- `scripts/`: Wrapper scripts, model fetch script (`fetch_models.sh`), and benchmarking utilities.
- `gpu_libs/`: (Local) CUDA libraries for the GPU backend.
