# neo-bot — asistente de desarrollo (Matrix · GitHub · Railway · Jira)

> ⚠️ **Este directorio es un servicio independiente.** Está dentro del repo `uko-vue` solo
> para revisarlo junto al resto de la entrega. **Antes de deployar, movelo a su propio repo
> `neo-bot`** y conectalo como un servicio aparte en Railway. No forma parte del build del
> front-end.

Neo recibe pedidos por **Element/Matrix** (`!neo ...`), dispara el workflow de GitHub Actions
que ejecuta **Claude Code** (`anthropics/claude-code-action@v1`) en el repo objetivo, y reporta
el **Pull Request** resultante a la sala. También baja los **previews de Railway** de cada PR.

```
Element/Matrix ──!neo──▶  neo-bot  ──workflow_dispatch──▶  GitHub Actions (@neo)
                            ▲  │                                   │
            webhook PR ─────┘  └── Railway GraphQL (bajar preview) │
                                                                   ▼
                                                      Claude Code abre el PR
                                                      Railway levanta el preview del PR
```

## Componentes

| Archivo | Rol |
|---|---|
| `neo/config.py` | Carga toda la config del entorno. Switch `NEO_JIRA_ENABLED`. |
| `neo/commands.py` | Parser puro de `!neo ...` (con tests). |
| `neo/matrix_bot.py` | Cliente matrix-nio: escucha `!neo`, responde en la sala. |
| `neo/github_client.py` | GitHub App: JWT → installation token → `workflow_dispatch`. |
| `neo/railway_client.py` | API GraphQL de Railway: listar/destruir environments de preview. |
| `neo/orchestrator.py` | Cerebro: comandos → acciones; correla PR↔sala. |
| `neo/webhooks.py` | Servidor aiohttp (`/healthz`, `/webhooks/github`, `/webhooks/jira`). |
| `neo/jira.py` | Integración Jira **gated** por `NEO_JIRA_ENABLED`. |
| `neo/app.py` | Arranca Matrix + servidor HTTP en un proceso. |

## Comandos de Matrix

```
!neo <repo>: <pedido>          implemento el cambio y abro un PR
!neo bajar pr-<N> [en <repo>]  destruyo el preview del PR N
!neo repos                     listo los repos autorizados
!neo status                    estado del bot
!neo ayuda                     ayuda
```

`<repo>` es un **alias** declarado en `NEO_REPOS` (p. ej. `uko-vue`) o un `owner/repo`
autorizado. Repos fuera de esa lista se rechazan.

## Correr en local

```bash
cd neo-bot
python -m venv .venv && . .venv/bin/activate    # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                            # completá los valores
python -m neo
```

Tests del parser (sin red ni credenciales):

```bash
python tests/test_commands.py      # o:  pytest
```

## Deploy en Railway (sin Docker)

1. Subí este directorio a su propio repo de GitHub (`neo-bot`).
2. En Railway: **New Project → Deploy from GitHub repo → neo-bot**. Nixpacks detecta Python
   por `requirements.txt`. El arranque es `python -m neo` (ver `Procfile` / `railway.json`).
3. Cargá las **variables** del servicio (ver `.env.example`). `PORT` lo inyecta Railway.
4. **No** habilites auto-sleep en este servicio: el bot mantiene la conexión `sync_forever`
   con Matrix (`sleepApplication: false` en `railway.json`). El auto-sleep es solo para los
   **previews de los PRs**, no para el bot.
5. Healthcheck: `GET /healthz`.

### Webhooks que apuntan al bot

- **GitHub App neo-bot** → Webhook URL: `https://<bot>.up.railway.app/webhooks/github`,
  secret = `NEO_GITHUB_WEBHOOK_SECRET`. Eventos: *Pull requests*. Con esto el bot reporta a la
  sala cuando se abre el PR y limpia el preview al cerrarse.
- **Jira** (opcional) → `https://<bot>.up.railway.app/webhooks/jira?secret=<NEO_JIRA_WEBHOOK_SECRET>`.

## Seguridad

- Todas las credenciales se leen del entorno. Nada de secretos en el código.
- El bot solo opera sobre los repos de `NEO_REPOS`.
- Opcional: limitá salas con `NEO_MATRIX_ROOMS` y usuarios con `NEO_MATRIX_ALLOWED_SENDERS`.
- Verificación de firma en el webhook de GitHub (`X-Hub-Signature-256`).

## Limitaciones conocidas (MVP)

- **Correlación PR↔sala** es FIFO en memoria por repo: si se disparan dos pedidos al mismo
  repo casi simultáneos, el reporte podría ir a la sala equivocada. Si se reinicia el bot, los
  pendientes se pierden y el PR se reporta a `NEO_MATRIX_DEFAULT_ROOM`. Suficiente para el
  piloto; para robustez, persistir la correlación (p. ej. con un id en el nombre de rama).
- Salas **sin E2EE**. Para cifrado de extremo a extremo: `matrix-nio[e2e]` + libolm.
