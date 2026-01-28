# Go Bot (OGS AI)

An AI bot for playing on [Online-Go.com (OGS)](https://online-go.com).

## Documentation & References

- **OGS API Documentation:** [https://online-go.com/api-docs/#/](https://online-go.com/api-docs/#/)
- **KataGo Engine:** [https://github.com/lightvector/KataGo](https://github.com/lightvector/KataGo)
- **KataGo Human SL (Supervised Learning):**
    - [KataGo v1.15.0 Release Notes](https://github.com/lightvector/KataGo/releases/tag/v1.15.0) (Contains Human SL model links)
    - [Human SL Analysis Guide](https://github.com/lightvector/KataGo/blob/master/docs/Analysis_Engine.md#human-sl-analysis-guide)
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Implementation Plan:** See [PLAN.md](PLAN.md)

## Usage

### 1. Fetch Models
First, download the required KataGo models and generate the configuration:
```bash
python3 scripts/fetch_models.py
```

### 2. OGS Credentials & Configuration
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
# Edit .env with your OGS_API_KEY or OGS_USERNAME/OGS_PASSWORD
```

You can connect using either an API Key (recommended) or an Application Specific Password.

#### Option A: API Key (Recommended)
1. Create a bot account on OGS.
2. Request bot status from OGS moderators.
3. Go to the bot's profile and generate an API Key.
4. Set `OGS_API_KEY` in your `.env`.

#### Option B: Username & Application Password
1. Go to OGS Settings -> "Application Specific Passwords".
2. Generate a new password for the bot.
3. Set `OGS_USERNAME` and `OGS_PASSWORD` in your `.env`.

### 3. Run the Bot (Human SL KataGo)
Ensure you have the `katago` binary installed and accessible. Then run the bot:

```bash
# To play as a specific human rank, edit BOT_RANK in .env (e.g. 5k, 1d, 9d)
# Then run the bot using the entry point:
python3 src/go_bot/main.py
```

The bot will automatically load the models from `models/` and use the robust `models/human.cfg` configuration for high-quality human imitation play.

## Development Setup

This project uses `pre-commit` with `ruff` and `mypy` for quality control.

```bash
# Install dependencies (assuming a virtual environment is active)
pip install -e ".[dev]"
pre-commit install
```
