"""Arranque de Neo: corre el bot de Matrix y el servidor de webhooks en el mismo proceso."""
from __future__ import annotations

import asyncio
import logging
import os

try:
    from dotenv import load_dotenv

    load_dotenv()  # carga .env en desarrollo local; en Railway no hace nada
except Exception:  # noqa: BLE001 - dotenv es opcional
    pass

from .config import Config
from .matrix_bot import MatrixBot
from .orchestrator import Orchestrator
from .webhooks import run_server


def _setup_logging() -> None:
    level = os.getenv("NEO_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )


async def main_async() -> None:
    _setup_logging()
    log = logging.getLogger("neo")

    cfg = Config.load()
    orchestrator = Orchestrator(cfg)
    bot = MatrixBot(cfg, orchestrator)

    # Servidor HTTP (healthcheck + webhooks) primero, para que Railway marque el deploy sano.
    runner = await run_server(cfg, orchestrator)
    log.info(
        "Neo arriba. Repos: %s | Jira: %s",
        ", ".join(cfg.repos.authorized) or "(ninguno)",
        "on" if cfg.jira_enabled else "off",
    )

    try:
        await bot.run()  # bloquea en sync_forever
    finally:
        await bot.close()
        await runner.cleanup()


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
