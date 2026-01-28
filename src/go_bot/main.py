import asyncio
import logging
import os
import sys
from go_bot.client import OGSClient
from go_bot.manager import GameManager
from go_bot.bot import Bot, KataGoBot, GTPBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    username = os.environ.get("OGS_USERNAME")
    password = os.environ.get("OGS_PASSWORD")
    api_key = os.environ.get("OGS_API_KEY")

    if api_key:
        client = OGSClient(api_key=api_key)
    elif username and password:
        logger.info(f"Logging in as {username}...")
        client = await OGSClient.login(username, password)
    else:
        print(
            "Error: Set OGS_API_KEY or (OGS_USERNAME and OGS_PASSWORD) environment variables."
        )
        sys.exit(1)

    # Bot configuration
    bot_type = os.environ.get("BOT_TYPE", "random")
    bot: Bot
    if bot_type == "katago":
        katago_path = os.environ.get("KATAGO_PATH", "katago")
        bot = KataGoBot(
            katago_path=katago_path,
            config_path="models/human.cfg",
            model_path="models/main_model.bin.gz",
            human_model_path="models/human_model.bin.gz",
            rank=os.environ.get("BOT_RANK", "5k"),
        )
    else:
        # Fallback to random GTP engine for testing
        engine_path = os.path.abspath("src/go_bot/random_gtp.py")
        bot = GTPBot(engine_path)

    manager = GameManager(client, bot)

    logger.info("Starting bot...")
    try:
        await manager.run_forever()
    except KeyboardInterrupt:
        manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
