"""Bot de Matrix (matrix-nio). Escucha mensajes `!neo ...`, los parsea y delega en el
Orchestrator. Responde en la misma sala.

Nota sobre E2EE: este bot usa salas sin cifrado de extremo a extremo. Para soportar E2EE
hay que instalar `matrix-nio[e2e]` (requiere libolm) y manejar verificación de dispositivos.
"""
from __future__ import annotations

import logging
import time

import markdown as md
from nio import AsyncClient, MatrixRoom, RoomMessageText

from . import commands
from .config import Config
from .orchestrator import Orchestrator

log = logging.getLogger("neo.matrix")


class MatrixBot:
    def __init__(self, cfg: Config, orchestrator: Orchestrator) -> None:
        self.cfg = cfg
        self.orchestrator = orchestrator
        self.client = AsyncClient(cfg.matrix_homeserver, cfg.matrix_user_id)
        self._started_ms = int(time.time() * 1000)
        orchestrator.set_notifier(self.send_markdown)

    async def login(self) -> None:
        if self.cfg.matrix_access_token:
            self.client.access_token = self.cfg.matrix_access_token
            self.client.user_id = self.cfg.matrix_user_id
            self.client.device_id = self.cfg.matrix_device_id
            log.info("Matrix: sesión restaurada por access token")
        elif self.cfg.matrix_password:
            resp = await self.client.login(
                self.cfg.matrix_password, device_name=self.cfg.matrix_device_id
            )
            log.info("Matrix: login por password -> %s", type(resp).__name__)
        else:
            raise RuntimeError(
                "Configurá NEO_MATRIX_ACCESS_TOKEN o NEO_MATRIX_PASSWORD para autenticar el bot."
            )

    async def send_markdown(self, room_id: str, text: str) -> None:
        """Envía un mensaje con cuerpo plano + HTML (renderizado desde Markdown)."""
        html = md.markdown(text, extensions=["fenced_code", "nl2br"])
        await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": text,
                "format": "org.matrix.custom.html",
                "formatted_body": html,
            },
        )

    def _allowed(self, room: MatrixRoom, sender: str) -> bool:
        if self.cfg.matrix_rooms and room.room_id not in self.cfg.matrix_rooms:
            return False
        if self.cfg.matrix_allowed_senders and sender not in self.cfg.matrix_allowed_senders:
            return False
        return True

    async def _on_message(self, room: MatrixRoom, event: RoomMessageText) -> None:
        # Ignorar mensajes propios y los previos al arranque (historial del primer sync).
        if event.sender == self.client.user_id:
            return
        if event.server_timestamp < self._started_ms:
            return

        cmd = commands.parse(event.body)
        if cmd.kind is commands.Kind.NONE:
            return  # no es para Neo

        if not self._allowed(room, event.sender):
            log.warning("Comando ignorado de %s en %s (no autorizado)", event.sender, room.room_id)
            await self.send_markdown(
                room.room_id, "🚫 No estás autorizado a usar Neo en esta sala."
            )
            return

        log.info("Comando %s de %s en %s", cmd.kind.name, event.sender, room.room_id)
        try:
            reply = await self.orchestrator.handle_command(cmd, room.room_id, event.sender)
        except Exception as exc:  # noqa: BLE001
            log.exception("handle_command falló")
            reply = f"❌ Error procesando el comando: {exc}"
        await self.send_markdown(room.room_id, reply)

    async def run(self) -> None:
        await self.login()
        self.client.add_event_callback(self._on_message, RoomMessageText)
        log.info("Matrix: escuchando (sync_forever)…")
        await self.client.sync_forever(timeout=30000, full_state=False)

    async def close(self) -> None:
        await self.client.close()
