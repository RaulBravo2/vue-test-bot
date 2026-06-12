"""El "cerebro" de Neo: traduce comandos en acciones (disparar workflows, bajar previews)
y correla los PRs que la App abre con la sala de Matrix que originó el pedido.
"""
from __future__ import annotations

import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Awaitable, Callable

from .commands import HELP_TEXT, Command, Kind
from .config import Config
from .github_client import GitHubClient
from .railway_client import RailwayClient

log = logging.getLogger("neo.orchestrator")

# Firma del notificador que registra el bot de Matrix para poder responder a una sala.
Notifier = Callable[[str, str], Awaitable[None]]  # (room_id, markdown) -> None


@dataclass
class PendingRequest:
    room_id: str
    requester: str


class Orchestrator:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.github = GitHubClient(
            cfg.github_app_id, cfg.github_app_private_key, cfg.github_installation_id
        )
        self.railway = (
            RailwayClient(cfg.railway_api_token, cfg.railway_project_id, cfg.railway_graphql_url)
            if cfg.railway_api_token and cfg.railway_project_id
            else None
        )
        # Cola FIFO de pedidos por repo, para correlacionar el webhook de PR abierto.
        self._pending: dict[str, deque[PendingRequest]] = defaultdict(deque)
        self._notify: Notifier | None = None

    def set_notifier(self, notifier: Notifier) -> None:
        self._notify = notifier

    async def notify(self, room_id: str | None, text: str) -> None:
        room = room_id or self.cfg.matrix_default_room
        if room and self._notify:
            await self._notify(room, text)

    # ----------------------------------------------------------------- comandos

    async def handle_command(self, cmd: Command, room_id: str, sender: str) -> str:
        """Procesa un comando ya parseado y devuelve la respuesta inmediata para la sala."""
        if cmd.kind is Kind.HELP:
            return HELP_TEXT
        if cmd.kind is Kind.STATUS:
            return self._status_text()
        if cmd.kind is Kind.REPOS:
            return self._repos_text()
        if cmd.kind is Kind.IMPLEMENT:
            return await self._handle_implement(cmd, room_id, sender)
        if cmd.kind is Kind.TEARDOWN:
            return await self._handle_teardown(cmd)
        return ("No entendí el comando. Probá `!neo ayuda`.")

    async def _handle_implement(self, cmd: Command, room_id: str, sender: str) -> str:
        repo_full = self.cfg.repos.resolve(cmd.repo or "")
        if not repo_full:
            return (
                f"❌ `{cmd.repo}` no es un repo autorizado. "
                f"Autorizados: {', '.join(self.cfg.repos.aliases) or '(ninguno)'}."
            )
        inputs = {
            "request": cmd.request or "",
            "requester": sender,
            "source": "matrix",
        }
        try:
            await self.github.dispatch_workflow(
                repo_full,
                self.cfg.github_workflow_file,
                self.cfg.github_default_ref,
                inputs,
            )
        except Exception as exc:  # noqa: BLE001 - reportamos cualquier fallo a la sala
            log.exception("dispatch falló")
            return f"❌ No pude disparar el flujo en `{repo_full}`: {exc}"

        # Recordamos el pedido para avisar a esta sala cuando se abra el PR.
        self._pending[repo_full].append(PendingRequest(room_id=room_id, requester=sender))

        run_url = await self.github.latest_run_url(repo_full, self.cfg.github_workflow_file)
        extra = f"\nSeguimiento: {run_url}" if run_url else ""
        return (
            f"🚀 Disparé a Neo en `{repo_full}`. Apenas tenga el cambio listo, "
            f"abro un PR y te paso el enlace acá.{extra}"
        )

    async def _handle_teardown(self, cmd: Command) -> str:
        if not self.railway or not self.railway.configured:
            return "⚠️ Railway no está configurado en el bot; no puedo bajar previews."
        pr = cmd.pr_number
        try:
            env = await self.railway.find_pr_environment(pr)
            if not env:
                return f"No encontré ningún preview para `pr-{pr}`. ¿Ya estaba bajado?"
            ok = await self.railway.delete_environment(env["id"])
            if ok:
                return f"🧹 Bajé el preview de `pr-{pr}` (environment `{env['name']}`)."
            return f"❌ Railway no confirmó la baja de `{env['name']}`."
        except Exception as exc:  # noqa: BLE001
            log.exception("teardown falló")
            return f"❌ Error bajando `pr-{pr}`: {exc}"

    # ----------------------------------------------------------------- webhooks

    async def on_pull_request_opened(self, repo_full: str, pr: dict) -> None:
        """Llamado desde el webhook de GitHub cuando la App abre/relaciona un PR."""
        title = pr.get("title", "")
        url = pr.get("html_url", "")
        number = pr.get("number")
        pending = self._pending.get(repo_full)
        room_id = None
        if pending:
            room_id = pending.popleft().room_id
        await self.notify(
            room_id,
            f"✅ PR abierto en `{repo_full}`: **#{number} {title}**\n{url}\n"
            f"El preview se está levantando; te aviso cuando tenga URL.",
        )

    async def on_pull_request_closed(self, repo_full: str, pr: dict) -> None:
        """Al cerrar/mergear un PR, intentamos bajar su preview (defensa en profundidad:
        Railway también lo destruye solo, pero no dependemos solo de eso)."""
        number = pr.get("number")
        if not self.railway or not self.railway.configured:
            return
        try:
            env = await self.railway.find_pr_environment(number)
            if env:
                await self.railway.delete_environment(env["id"])
                await self.notify(
                    None, f"🧹 PR #{number} de `{repo_full}` cerrado → preview destruido."
                )
        except Exception:  # noqa: BLE001
            log.exception("cleanup al cerrar PR falló")

    async def on_deployment_ready(self, repo_full: str, pr_number: int, url: str) -> None:
        """Opcional: si Railway notifica que el deploy del preview quedó listo con su URL."""
        await self.notify(None, f"🌐 Preview de `{repo_full}` pr-{pr_number} listo: {url}")

    # ------------------------------------------------------------------- texto

    def _status_text(self) -> str:
        return (
            "🟢 Neo operativo.\n"
            f"• Repos autorizados: {', '.join(self.cfg.repos.authorized) or '(ninguno)'}\n"
            f"• Railway: {'configurado' if (self.railway and self.railway.configured) else 'no configurado'}\n"
            f"• Jira: {'habilitado' if self.cfg.jira_enabled else 'deshabilitado'}"
        )

    def _repos_text(self) -> str:
        if not self.cfg.repos.aliases:
            return "No hay repos autorizados configurados (NEO_REPOS vacío)."
        lines = [f"• `{alias}` → {full}" for alias, full in self.cfg.repos.aliases.items()]
        return "Repos autorizados:\n" + "\n".join(lines)
