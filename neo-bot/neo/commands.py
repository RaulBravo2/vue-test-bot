"""Parseo de comandos de Matrix dirigidos a Neo.

Gramática soportada (prefijo obligatorio `!neo`):

    !neo ayuda                      -> AYUDA
    !neo status                     -> STATUS
    !neo repos                      -> REPOS
    !neo <repo>: <pedido>           -> IMPLEMENT  (repo = alias o owner/repo autorizado)
    !neo bajar pr-<N> [en <repo>]   -> TEARDOWN   (baja el preview del PR N)

Las funciones son puras (no tocan red) para poder testearlas.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto

PREFIX = "!neo"


class Kind(Enum):
    NONE = auto()        # no es un comando para Neo
    HELP = auto()
    STATUS = auto()
    REPOS = auto()
    IMPLEMENT = auto()
    TEARDOWN = auto()
    UNKNOWN = auto()      # empieza con !neo pero no matchea nada


@dataclass(frozen=True)
class Command:
    kind: Kind
    repo: str | None = None        # alias o owner/repo tal cual lo escribió el humano
    request: str | None = None     # texto del pedido (IMPLEMENT)
    pr_number: int | None = None   # número de PR (TEARDOWN)
    raw: str = ""


_BAJAR_RE = re.compile(
    r"^bajar\s+pr[-\s]?(\d+)(?:\s+en\s+(\S+))?\s*$",
    re.IGNORECASE,
)


def parse(body: str) -> Command:
    """Convierte el texto de un mensaje en un Command. Nunca lanza excepción."""
    if body is None:
        return Command(Kind.NONE, raw="")
    text = body.strip()
    lowered = text.lower()

    if not lowered.startswith(PREFIX):
        return Command(Kind.NONE, raw=text)

    # Quitar el prefijo "!neo" y espacios.
    rest = text[len(PREFIX):].strip()
    if not rest:
        return Command(Kind.HELP, raw=text)

    first = rest.split()[0].lower()

    if first in {"ayuda", "help", "?"}:
        return Command(Kind.HELP, raw=text)
    if first in {"status", "estado", "ping"}:
        return Command(Kind.STATUS, raw=text)
    if first in {"repos", "repositorios"}:
        return Command(Kind.REPOS, raw=text)

    if first == "bajar":
        m = _BAJAR_RE.match(rest)
        if not m:
            return Command(Kind.UNKNOWN, raw=text)
        pr = int(m.group(1))
        repo = m.group(2)
        return Command(Kind.TEARDOWN, repo=repo, pr_number=pr, raw=text)

    # Forma "<repo>: <pedido>". El repo es todo lo anterior al primer ':'.
    if ":" in rest:
        repo_part, request = rest.split(":", 1)
        repo = repo_part.strip()
        request = request.strip()
        if repo and request:
            return Command(Kind.IMPLEMENT, repo=repo, request=request, raw=text)

    return Command(Kind.UNKNOWN, raw=text)


HELP_TEXT = (
    "🤖 *Neo* — asistente de desarrollo. Comandos:\n"
    "• `!neo <repo>: <pedido>` — implemento el cambio y abro un PR. "
    "Ej: `!neo uko-vue: agregá un botón de exportar a CSV en la tabla de usuarios`\n"
    "• `!neo bajar pr-<N> [en <repo>]` — destruyo el preview del PR N\n"
    "• `!neo repos` — listo los repos autorizados\n"
    "• `!neo status` — estado del bot\n"
    "• `!neo ayuda` — esta ayuda"
)
