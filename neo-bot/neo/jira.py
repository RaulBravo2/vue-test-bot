"""Integración opcional con Jira, apagada por defecto.

CRITERIO DE ACEPTACIÓN: con NEO_JIRA_ENABLED=false, ningún disparo de Jira se procesa.
Por eso `handle_event` corta de entrada si el switch está apagado, antes de mirar el payload.

Cuando está habilitado, reacciona a:
  - comment_created cuyo cuerpo menciona "@neo"
  - issue_created cuya descripción menciona "@neo"
mapeando el KEY del proyecto Jira (p. ej. "PORTAL") a un alias de repo vía NEO_JIRA_PROJECT_REPO.
"""
from __future__ import annotations

import logging

from .config import Config
from .orchestrator import Orchestrator

log = logging.getLogger("neo.jira")

TRIGGER = "@neo"


async def handle_event(cfg: Config, orchestrator: Orchestrator, payload: dict) -> str:
    if not cfg.jira_enabled:
        log.info("Jira deshabilitado (NEO_JIRA_ENABLED=false): evento ignorado")
        return "jira-disabled"

    event = payload.get("webhookEvent", "")
    issue = payload.get("issue", {}) or {}
    fields = issue.get("fields", {}) or {}
    project_key = (fields.get("project", {}) or {}).get("key", "").upper()
    issue_key = issue.get("key", "")

    # Determinar texto del pedido según el tipo de evento.
    text = ""
    if event == "comment_created" or "comment" in payload:
        text = ((payload.get("comment", {}) or {}).get("body", "") or "").strip()
    elif event in {"jira:issue_created", "issue_created"}:
        summary = fields.get("summary", "") or ""
        description = fields.get("description", "") or ""
        text = f"{summary}\n\n{description}".strip()

    if TRIGGER not in text.lower():
        return "no-trigger"

    repo_alias = cfg.jira_project_repo.get(project_key)
    repo_full = cfg.repos.resolve(repo_alias or "") if repo_alias else None
    if not repo_full:
        log.warning("Jira: proyecto %s sin mapeo de repo autorizado", project_key)
        return "no-repo-mapping"

    # Limpiar la mención y armar el pedido.
    request = text.replace(TRIGGER, "").strip()
    request = f"[Jira {issue_key}] {request}"

    await orchestrator.github.dispatch_workflow(
        repo_full,
        cfg.github_workflow_file,
        cfg.github_default_ref,
        {"request": request, "requester": f"jira:{issue_key}", "source": "jira"},
    )
    await orchestrator.notify(None, f"🧩 Jira {issue_key} → disparé Neo en `{repo_full}`.")
    log.info("Jira %s -> dispatch en %s", issue_key, repo_full)
    return "dispatched"
