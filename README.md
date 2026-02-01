# OGS KataGo Human SL Bot

This project connects [KataGo](https://github.com/lightvector/KataGo) (using the Human Supervised Learning model) to [Online-Go.com (OGS)](https://online-go.com) using the [gtp2ogs](https://github.com/online-go/gtp2ogs) bridge.

The "Human SL" model is specifically trained to mimic human play styles rather than playing optimally, making it a more natural opponent for human players on OGS.

## Prerequisites

- **Node.js & npm**: To run the `gtp2ogs` bridge.
  ```bash
  npm install -g gtp2ogs
  ```
- **KataGo Binaries**: Pre-compiled CPU and GPU binaries are included in `bin/`.
- **Python 3.10**: Required for GPU library compatibility and helper scripts.

## Setup

### 1. Fetch Models
Download the required neural network models:
```bash
./scripts/fetch_models.sh
```
This script will create the `models/` directory and download the main network and the human SL weights. The engine configuration (`models/human.cfg`) is already included in the repository.

### 2. OGS API Key
1. Create a bot account on [OGS](https://online-go.com).
2. Ask a moderator (e.g., in the "Support" channel) to flag the account as a "Bot".
3. Log in to the bot account, go to **Settings** -> **Bot Settings**, and generate an **API Key**.

### 3. GPU Setup (Optional)
To enable sub-second moves using your GPU without installing the full CUDA toolkit system-wide, install the required libraries into a local directory using **Python 3.10**:
```bash
mkdir -p gpu_libs
pip install nvidia-cudnn-cu12==8.9.7.29 nvidia-cublas-cu12 --target gpu_libs --no-deps
```
*The `scripts/run_katago_gpu.sh` script is pre-configured to find these libraries in `gpu_libs/` or a `.venv/`.*

## Running the Bot

Start the bot by providing your API key and (optionally) the desired rank profile inline.

### Available Rank Profiles
The Human SL model supports a wide range of imitation styles:
- **Modern Human:** `rank_20k` through `rank_9d` (e.g., `rank_5k`).
- **Pre-AlphaZero:** `preaz_20k` through `preaz_9d` (Traditional opening styles).
- **Historical Pro:** `proyear_1800` through `proyear_2023` (Imitates styles from specific eras).

*Note: For high-dan/pro ranks, the model's actual strength may not reach the target without increasing search visits (config settings), as it primarily mimics style.*

### KataGo Human SL (GPU Optimized)
**Recommended.** High performance inference. Expected sub-second move time on modern GPUs (~1.5GB VRAM per instance).
```bash
BOT_RANK=rank_20k gtp2ogs -c configs/gtp2ogs.katago_gpu.json5 --apikey YOUR_API_KEY
```

### KataGo Human SL (CPU Optimized)
Fallback for systems without a compatible GPU. Move time depends on CPU performance; expected ~10-20s per move on modern multi-core CPUs.
```bash
BOT_RANK=rank_20k gtp2ogs -c configs/gtp2ogs.katago_cpu.json5 --apikey YOUR_API_KEY
```

### Random Bot
A lightweight Python bot that plays random legal moves. Useful for testing OGS connectivity. (Requires `python3` and `pip install sgfmill`).
```bash
gtp2ogs -c configs/gtp2ogs.random.json5 --apikey YOUR_API_KEY
```

## Running Multiple Bots (Background)

To run multiple bots concurrently, or to run a bot in the background, redirect output to a log file in the `gtp_logs/` directory and use `&`:

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
