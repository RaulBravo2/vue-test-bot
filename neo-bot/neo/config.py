"""Configuración de Neo, leída íntegramente del entorno.

Regla de seguridad: NINGÚN secreto vive en el código. En Railway se setean como variables
del servicio; en local podés usar un archivo .env (ver .env.example) cargado por python-dotenv.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on", "si", "sí"}


def _list(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Falta la variable de entorno obligatoria: {name}")
    return value


@dataclass(frozen=True)
class RepoMap:
    """Mapea un alias corto (lo que el humano escribe en Matrix) al owner/repo real.

    Se configura con NEO_REPOS, formato:  alias=owner/repo,alias2=owner/repo2
    Ej:  uko-vue=miorg/uko-vue,api=miorg/api_portal_cliente
    """

    aliases: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "RepoMap":
        mapping: dict[str, str] = {}
        for pair in _list("NEO_REPOS"):
            if "=" not in pair:
                continue
            alias, full = pair.split("=", 1)
            mapping[alias.strip()] = full.strip()
        return cls(aliases=mapping)

    def resolve(self, alias: str) -> str | None:
        """Devuelve 'owner/repo' a partir de un alias o de un 'owner/repo' ya completo.

        Solo resuelve repos autorizados (los declarados en NEO_REPOS). Cualquier otra cosa
        devuelve None, así Neo nunca opera sobre un repo fuera del alcance permitido.
        """
        alias = alias.strip()
        if alias in self.aliases:
            return self.aliases[alias]
        if "/" in alias and alias in set(self.aliases.values()):
            return alias  # owner/repo explícito, pero solo si está autorizado
        return None

    @property
    def authorized(self) -> list[str]:
        return sorted(set(self.aliases.values()))

    def alias_for(self, full: str) -> str:
        for alias, value in self.aliases.items():
            if value == full:
                return alias
        return full


@dataclass(frozen=True)
class Config:
    # --- Matrix ---
    matrix_homeserver: str
    matrix_user_id: str
    matrix_access_token: str | None
    matrix_password: str | None
    matrix_device_id: str
    matrix_rooms: list[str]          # rooms permitidos (vacío = todos)
    matrix_default_room: str | None  # room donde reportar PRs si no hay correlación
    matrix_allowed_senders: list[str]

    # --- GitHub App neo-bot ---
    github_app_id: str
    github_app_private_key: str
    github_installation_id: str
    github_workflow_file: str        # ej: neo.yml
    github_default_ref: str          # ej: main
    github_webhook_secret: str | None

    # --- Railway ---
    railway_api_token: str | None
    railway_project_id: str | None
    railway_graphql_url: str

    # --- Jira (opcional, apagado por defecto) ---
    jira_enabled: bool
    jira_webhook_secret: str | None
    jira_project_repo: dict[str, str]  # KEY de proyecto Jira -> alias de repo

    # --- Server ---
    port: int
    repos: RepoMap

    @classmethod
    def load(cls) -> "Config":
        repos = RepoMap.from_env()

        jira_map: dict[str, str] = {}
        for pair in _list("NEO_JIRA_PROJECT_REPO"):
            if "=" in pair:
                key, alias = pair.split("=", 1)
                jira_map[key.strip().upper()] = alias.strip()

        return cls(
            matrix_homeserver=_required("NEO_MATRIX_HOMESERVER"),
            matrix_user_id=_required("NEO_MATRIX_USER_ID"),
            matrix_access_token=os.getenv("NEO_MATRIX_ACCESS_TOKEN"),
            matrix_password=os.getenv("NEO_MATRIX_PASSWORD"),
            matrix_device_id=os.getenv("NEO_MATRIX_DEVICE_ID", "NEO_BOT"),
            matrix_rooms=_list("NEO_MATRIX_ROOMS"),
            matrix_default_room=os.getenv("NEO_MATRIX_DEFAULT_ROOM"),
            matrix_allowed_senders=_list("NEO_MATRIX_ALLOWED_SENDERS"),
            github_app_id=_required("NEO_GITHUB_APP_ID"),
            github_app_private_key=_required("NEO_GITHUB_APP_PRIVATE_KEY"),
            github_installation_id=_required("NEO_GITHUB_INSTALLATION_ID"),
            github_workflow_file=os.getenv("NEO_GITHUB_WORKFLOW_FILE", "neo.yml"),
            github_default_ref=os.getenv("NEO_GITHUB_DEFAULT_REF", "main"),
            github_webhook_secret=os.getenv("NEO_GITHUB_WEBHOOK_SECRET"),
            railway_api_token=os.getenv("NEO_RAILWAY_API_TOKEN"),
            railway_project_id=os.getenv("NEO_RAILWAY_PROJECT_ID"),
            railway_graphql_url=os.getenv(
                "NEO_RAILWAY_GRAPHQL_URL", "https://backboard.railway.com/graphql/v2"
            ),
            jira_enabled=_bool("NEO_JIRA_ENABLED", False),
            jira_webhook_secret=os.getenv("NEO_JIRA_WEBHOOK_SECRET"),
            jira_project_repo=jira_map,
            port=int(os.getenv("PORT", "8080")),
            repos=repos,
        )
