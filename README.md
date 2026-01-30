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

### 2. OGS API Key
1. Create a bot account on OGS.
2. Ask a moderator to flag the account as a "Bot".
3. Log in to the bot account, go to **Settings** -> **Bot Settings**, and generate an **API Key**.
4. Create your local `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and replace 'your_api_key_here' with your actual key
   ```

### 3. GPU Setup (WSL2 / Linux)
To enable sub-second moves using your GPU without installing the full CUDA toolkit system-wide, install the required libraries into a local directory:
```bash
mkdir -p gpu_libs
pip install nvidia-cudnn-cu12==8.9.7.29 --target gpu_libs --no-deps
```
*The `scripts/run_katago_gpu.sh` script is pre-configured to find these libraries.*

## Running the Bot

Always load your API key from the `.env` file when starting the bot.

### KataGo Human SL (GPU Optimized)
**Recommended.** Uses your GTX 1080 Ti for ~5s latency per move.
```bash
export $(cat .env | xargs) && gtp2ogs -c configs/gtp2ogs.katago_gpu.json5 --apikey $OGS_API_KEY
```

### KataGo Human SL (CPU Optimized)
Fallback for systems without a compatible GPU. ~11s latency per move on an 8-core CPU.
```bash
export $(cat .env | xargs) && gtp2ogs -c configs/gtp2ogs.katago_cpu.json5 --apikey $OGS_API_KEY
```

### Random Bot
A lightweight Python bot that plays random legal moves. Useful for testing OGS connectivity.
```bash
export $(cat .env | xargs) && gtp2ogs -c configs/gtp2ogs.random.json5 --apikey $OGS_API_KEY
```

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
- `scripts/`: Wrapper scripts and benchmarking utilities.
- `gpu_libs/`: (Local) CUDA libraries for the GPU backend.
