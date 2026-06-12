"""Servidor HTTP (aiohttp) para webhooks entrantes y healthcheck.

Escucha en 0.0.0.0:$PORT (requisito de Railway).
Rutas:
  GET  /healthz            -> 200 ok (healthcheck de Railway)
  POST /webhooks/github    -> eventos pull_request (abrir/cerrar) de la App neo-bot
  POST /webhooks/jira      -> eventos de Jira (procesados solo si NEO_JIRA_ENABLED=true)
"""
from __future__ import annotations

import hashlib
import hmac
import logging

from aiohttp import web

from . import jira
from .config import Config
from .orchestrator import Orchestrator

log = logging.getLogger("neo.webhooks")


def _verify_github_signature(secret: str | None, body: bytes, header: str | None) -> bool:
    if not secret:
        return True  # sin secreto configurado, no verificamos (no recomendado en prod)
    if not header or not header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header)


def build_app(cfg: Config, orchestrator: Orchestrator) -> web.Application:
    app = web.Application()

    async def healthz(_req: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "service": "neo-bot"})

    async def github_webhook(req: web.Request) -> web.Response:
        body = await req.read()
        sig = req.headers.get("X-Hub-Signature-256")
        if not _verify_github_signature(cfg.github_webhook_secret, body, sig):
            log.warning("Firma de webhook de GitHub inválida")
            return web.json_response({"error": "bad signature"}, status=401)

        event = req.headers.get("X-GitHub-Event", "")
        payload = await req.json()

        if event == "pull_request":
            action = payload.get("action")
            pr = payload.get("pull_request", {}) or {}
            repo_full = (payload.get("repository", {}) or {}).get("full_name", "")
            if action in {"opened", "ready_for_review"}:
                await orchestrator.on_pull_request_opened(repo_full, pr)
            elif action == "closed":
                await orchestrator.on_pull_request_closed(repo_full, pr)
        elif event == "ping":
            log.info("GitHub webhook ping OK")

        return web.json_response({"ok": True})

    async def jira_webhook(req: web.Request) -> web.Response:
        # Verificación opcional por secreto en query (?secret=...) o header propio.
        if cfg.jira_webhook_secret:
            provided = req.query.get("secret") or req.headers.get("X-Neo-Jira-Secret")
            if provided != cfg.jira_webhook_secret:
                return web.json_response({"error": "bad secret"}, status=401)
        payload = await req.json()
        result = await jira.handle_event(cfg, orchestrator, payload)
        return web.json_response({"result": result})

    app.router.add_get("/healthz", healthz)
    app.router.add_post("/webhooks/github", github_webhook)
    app.router.add_post("/webhooks/jira", jira_webhook)
    return app


async def run_server(cfg: Config, orchestrator: Orchestrator) -> web.AppRunner:
    app = build_app(cfg, orchestrator)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=cfg.port)
    await site.start()
    log.info("HTTP escuchando en 0.0.0.0:%s", cfg.port)
    return runner
