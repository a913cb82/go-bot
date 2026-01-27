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

## Development Setup

This project uses `pre-commit` with `ruff` and `mypy` for quality control.

```bash
# Install dependencies (assuming a virtual environment is active)
pip install -e .
pre-commit install
```
