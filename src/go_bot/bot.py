import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from go_bot.session import GameSession

logger = logging.getLogger(__name__)


class Bot(ABC):
    @abstractmethod
    async def get_move(self, session: GameSession) -> str:
        """
        Generate a move for the given game session.
        Returns a GTP coordinate string (e.g., "Q16" or "pass").
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """Initialize the bot/engine."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Clean up resources."""
        pass


class GTPBot(Bot):
    def __init__(self, engine_path: str, engine_args: Optional[List[str]] = None):
        self.engine_path = engine_path
        self.engine_args = engine_args or []
        self.process: Optional[asyncio.subprocess.Process] = None
        self._lock = asyncio.Lock()  # Ensure only one command at a time

    async def start(self) -> None:
        logger.info(f"Starting engine: {self.engine_path} {' '.join(self.engine_args)}")
        self.process = await asyncio.create_subprocess_exec(
            self.engine_path,
            *self.engine_args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Start a task to log stderr
        asyncio.create_task(self._log_stderr())

    async def _log_stderr(self) -> None:
        if not self.process or not self.process.stderr:
            return
        while True:
            line = await self.process.stderr.readline()
            if not line:
                break
            logger.error(f"Engine Stderr: {line.decode().strip()}")

    async def stop(self) -> None:
        if self.process:
            try:
                # Try to send quit, but don't wait forever if engine is dead
                try:
                    await asyncio.wait_for(self._send_command("quit"), timeout=1.0)
                except (
                    asyncio.TimeoutError,
                    RuntimeError,
                    ConnectionResetError,
                    ProcessLookupError,
                ):
                    pass
            finally:
                if self.process.returncode is None:
                    try:
                        self.process.terminate()
                        await self.process.wait()
                    except ProcessLookupError:
                        pass
                self.process = None

    async def _send_command(self, command: str) -> str:
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise RuntimeError("Engine not started")

        logger.debug(f"GTP Command: {command}")
        self.process.stdin.write(f"{command}\n".encode())
        await self.process.stdin.drain()

        response_lines: List[str] = []
        while True:
            line_bytes = await self.process.stdout.readline()
            if not line_bytes:
                break

            line = line_bytes.decode().strip()
            if not line:
                if response_lines:
                    break
                continue

            response_lines.append(line)
            if line.startswith("=") or line.startswith("?"):
                # Standard GTP response: one line starting with = or ?,
                # followed by optional lines, ending with a double newline.
                pass

        full_response = "\n".join(response_lines)
        logger.debug(f"GTP Response: {full_response}")

        if not full_response:
            raise RuntimeError("Engine closed connection")

        if full_response.startswith("?"):
            raise ValueError(f"GTP Error: {full_response}")

        if full_response.startswith("="):
            return full_response[1:].strip()
        return full_response.strip()

    async def get_move(self, session: GameSession) -> str:
        async with self._lock:
            await self._send_command(f"boardsize {session.board_size}")
            await self._send_command("clear_board")

            for play_cmd in session.get_gtp_history():
                await self._send_command(play_cmd)

            color = "black" if session.turn == "black" else "white"
            move = await self._send_command(f"genmove {color}")
            return move


class KataGoBot(GTPBot):
    def __init__(
        self,
        katago_path: str,
        config_path: str,
        model_path: str,
        human_model_path: Optional[str] = None,
        rank: str = "5k",
    ):
        args = ["gtp", "-config", config_path, "-model", model_path]
        if human_model_path:
            args.extend(["-human-model", human_model_path])

        # Override the rank in the config
        # Format: rank_5k, rank_1d, etc.
        # We assume the user passes "5k", "1d", etc.
        profile = f"rank_{rank}"
        args.extend(["-override-config", f"humanSLProfile={profile}"])

        super().__init__(katago_path, args)
