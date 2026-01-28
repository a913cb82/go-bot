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

### 2. OGS Credentials
You can connect using either an API Key (recommended) or an Application Specific Password.

#### Option A: API Key (Recommended)
1. Create a bot account on OGS.
2. Request bot status from OGS moderators.
3. Go to the bot's profile and generate an API Key.
4. Set the environment variable: `export OGS_API_KEY="your_api_key"`

#### Option B: Username & Password
1. Go to OGS Settings -> "Application Specific Passwords".
2. Generate a new password for the bot.
3. Set environment variables:
   ```bash
   export OGS_USERNAME="your_username"
   export OGS_PASSWORD="your_application_specific_password"
   ```

### 3. Run the Bot
Run the bot using the provided entry point:

```bash
# Run with KataGo (requires katago binary in PATH)
export BOT_TYPE="katago"
export KATAGO_PATH="/path/to/katago"
export BOT_RANK="1d"
python3 src/go_bot/main.py

# Run with Random engine (for testing)
export BOT_TYPE="random"
python3 src/go_bot/main.py
```

## Development Setup

This project uses `pre-commit` with `ruff` and `mypy` for quality control.

```bash
# Install dependencies (assuming a virtual environment is active)
pip install -e ".[dev]"
pre-commit install
```
