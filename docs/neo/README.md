# Neo — Runbook de implementación (MAN-TEC-001 v1.1)

Guía operativa para poner en marcha **Neo**, el asistente de desarrollo (Claude) que recibe
pedidos por **Element/Matrix**, **GitHub** y (opcional) **Jira**, implementa el código, abre
**Pull Requests** y levanta **previews efímeros en Railway**.

Esta entrega contiene el código y la configuración; los pasos que requieren consola web
(crear la GitHub App, crear el proyecto en Railway, cargar secretos) están detallados abajo —
**no se pueden hacer desde el repo** y quedan a cargo del operador.

> Arquitectura v1.1: **Railway** para previews y hosting del bot (reemplaza AWS). **Sin Docker**
> (buildpacks Nixpacks). **Producción NO cambia**: sigue en la VPS actual, fuera del alcance de Neo.

---

## 1. Qué se entregó en este repo

| Ruta | Para qué |
|---|---|
| [CLAUDE.md](../../CLAUDE.md) | Contexto que Neo lee en cada corrida sobre este repo (comandos, convenciones, guardarraíles). |
| [.github/workflows/neo.yml](../../.github/workflows/neo.yml) | Workflow `anthropics/claude-code-action@v1`: trigger `@neo` + `workflow_dispatch`, autenticado con la GitHub App. |
| [railway.json](../../railway.json) · [nixpacks.toml](../../nixpacks.toml) | Config de preview del front-end en Railway (build Nixpacks, healthcheck, auto-sleep). |
| `package.json` → script `start` | Sirve el build en `0.0.0.0:$PORT` (requisito Railway). |
| [.env.example](../../.env.example) | Variables de build del front (Firebase, `VITE_API_BASE_URL`). |
| [neo-bot/](../../neo-bot/) | El bot (Matrix + GitHub + Railway + Jira). Servicio independiente → mover a su repo. |
| [docs/neo/seed/](seed/) | Seed de Mongo con datos sintéticos + guardarraíl anti-producción. |

Estado de los repos objetivo (Anexo 10.3): este repo (`uko-vue`, **front-end**) queda listo.
La **API** (`api_portal_cliente`) necesita el ajuste de la sección 6 antes de entrar al preview
full-stack.

---

## 2. Plan por semanas → qué cubre cada parte

- **Semana 1 — GitHub.** GitHub App `neo-bot` (Contents, Issues, PRs) + `neo.yml` (trigger
  `@neo`) en el repo piloto + `CLAUDE.md`. → §3, §4.
- **Semana 2 — Matrix.** Bot Python (matrix-nio) en Railway; `!neo <repo>: <pedido>` →
  `workflow_dispatch` → reporte del PR a la sala. → §5, [neo-bot/README.md](../../neo-bot/README.md).
- **Semana 3 — Previews.** PR environments en Railway (Mongo efímero + seed), auto-sleep,
  bajada al cerrar el PR y con `!neo bajar pr-N`. → §6.
- **Semana 4 — Jira + escala.** Switch `NEO_JIRA_ENABLED` + extensión al resto de los repos. → §7.

---

## 3. GitHub App `neo-bot` (Semana 1)

1. **GitHub → Settings → Developer settings → GitHub Apps → New GitHub App.**
   - Nombre: `neo-bot`.
   - **Permissions (Repository):** *Contents* → Read & write · *Issues* → Read & write ·
     *Pull requests* → Read & write · *Workflows* → Read & write (si Neo edita workflows) ·
     *Metadata* → Read.
   - **Subscribe to events:** *Pull request*, *Issue comment*, *Issues*.
   - **Webhook:** URL `https://<bot>.up.railway.app/webhooks/github`, *Secret* = el valor que
     pondrás en `NEO_GITHUB_WEBHOOK_SECRET`.
2. **Generá una private key** (.pem) y anotá el **App ID**.
3. **Install App** → instalala **solo en los repos autorizados** (piloto primero; el resto en
   Semana 4). Anotá el **Installation ID** (aparece en la URL de la instalación).
4. Cargá en el bot: `NEO_GITHUB_APP_ID`, `NEO_GITHUB_APP_PRIVATE_KEY`,
   `NEO_GITHUB_INSTALLATION_ID`, `NEO_GITHUB_WEBHOOK_SECRET`.

> **Branch protection (criterio de aceptación).** En cada repo objetivo: *Settings → Branches →
> Add rule* sobre `main` → **Require a pull request before merging** + **Require approvals (≥1)**
> + **Require review from someone other than the last pusher** (o **Dismiss stale approvals**).
> Como los PRs son autoría de la App `neo-bot`, **Neo no puede aprobar ni mergear sus propios PRs**:
> siempre revisa y mergea un humano.

### Secretos del repo (Actions)
En **cada repo objetivo → Settings → Secrets and variables → Actions**:

| Secret | Valor |
|---|---|
| `ANTHROPIC_API_KEY` | API key de Anthropic (la usa `claude-code-action`). |
| `NEO_APP_ID` | App ID de `neo-bot`. |
| `NEO_APP_PRIVATE_KEY` | Contenido del `.pem` de la App. |

El workflow usa estos secretos para generar un token de instalación con
`actions/create-github-app-token` y correr Claude Code como la App.

---

## 4. Probar el trigger `@neo` (Semana 1)

1. Subí `.github/workflows/neo.yml` y `CLAUDE.md` al repo piloto.
2. Abrí un **issue** y escribí, por ejemplo:
   `@neo agregá un botón "Exportar a CSV" en la tabla de usuarios`.
3. El workflow corre, Neo implementa en una rama nueva, deja `yarn build` en verde y **abre un PR**.
   → ✅ *Criterio: "Mención @neo en un issue genera un PR funcional".*

---

## 5. Bot de Matrix en Railway (Semana 2)

Detalle completo en [neo-bot/README.md](../../neo-bot/README.md). Resumen:

1. Creá el usuario `@neo` en tu homeserver y obtené un **access token** (o usá password).
2. Subí `neo-bot/` a su propio repo y deployalo en Railway (Nixpacks, Python; arranque
   `python -m neo`). **Auto-sleep apagado** en el bot (mantiene `sync_forever`).
3. Variables del servicio: ver [neo-bot/.env.example](../../neo-bot/.env.example). Clave:
   `NEO_REPOS="uko-vue=mi-org/uko-vue,api=mi-org/api_portal_cliente"`.
4. Invitá a `@neo` a la sala de Element y probá:
   `!neo uko-vue: agregá un botón de exportar a CSV en la tabla de usuarios`.
   El bot dispara el workflow y, cuando la App abre el PR (webhook), **reporta el enlace** a la sala.
   → ✅ *Criterio: "Comando !neo dispara el flujo y reporta el enlace del PR".*

---

## 6. Previews por PR en Railway (Semana 3)

### 6.1 Prerrequisito de la API (`api_portal_cliente`) — Anexo 10.3
La API debe escuchar en `0.0.0.0` y en el puerto que inyecta Railway:

```js
const port = process.env.PORT || 3000;
app.listen(port, "0.0.0.0", () => console.log(`API en :${port}`));
```

(El front-end de este repo ya cumple el equivalente con el script `start` →
`vite preview --host 0.0.0.0 --port $PORT`.)

### 6.2 Habilitar PR environments
1. En el proyecto de Railway, environment base, agregá los servicios:
   **front** (este repo) + **api** (`api_portal_cliente`) + **MongoDB** (plugin/Database de Railway).
2. **Project → Settings → Environments → Enable PR environments** (Railway crea un environment
   por cada PR, con **URL pública dinámica** `RAILWAY_PUBLIC_DOMAIN` por servicio).
3. **Auto-sleep:** en los servicios del preview, *Settings → Serverless / App Sleeping* (en el
   front ya viene `sleepApplication: true`). El preview **se duerme por inactividad**.
4. **Mongo efímero:** al clonarse el environment del PR, la base arranca vacía. Seteá en el
   environment de preview:
   - `NEO_PREVIEW=true`
   - `NEO_PROD_DB_DENYLIST="<host/cluster productivo>"` (defensa anti-producción)
   - El **front** apunta a la API del PR: `VITE_API_BASE_URL="https://${{ api.RAILWAY_PUBLIC_DOMAIN }}"`.
5. **Seed sintético:** copiá [docs/neo/seed/](seed/) al repo de la API y corré `node seed-mongo.js`
   al levantar el preview (deploy command de la API, o un servicio "seed" one-off). El seed
   **aborta** si no es un preview o si la URL parece productiva (verificado en esta entrega).
   → ✅ *Criterios: "preview con URL dinámica", "se duerme por inactividad", "previews nunca
   conectados a bases productivas".*

### 6.3 Bajar el preview
- **Automático al cerrar/mergear el PR:** Railway destruye el PR environment; además el bot lo
  baja por las dudas vía webhook (`on_pull_request_closed`).
- **Manual:** `!neo bajar pr-N` en Matrix → el bot llama a la API de Railway y destruye el
  environment `pr-N`.
  → ✅ *Criterio: "se destruye al cerrar el PR o con !neo bajar pr-N".*

Variables del bot para esto: `NEO_RAILWAY_API_TOKEN`, `NEO_RAILWAY_PROJECT_ID`.

---

## 7. Jira opcional + escala (Semana 4)

- **Switch:** `NEO_JIRA_ENABLED=false` por defecto. Con `true`, el bot procesa el webhook de
  Jira (`/webhooks/jira`) cuando un comentario/issue menciona `@neo`, mapeando el proyecto a un
  repo con `NEO_JIRA_PROJECT_REPO="PORTAL=uko-vue,API=api"`.
  → ✅ *Criterio: "Con NEO_JIRA_ENABLED=false, ningún disparo de Jira es procesado"* — el handler
  corta de entrada antes de mirar el payload ([neo-bot/neo/jira.py](../../neo-bot/neo/jira.py)).
- **Escala a más repos:** agregá cada repo a `NEO_REPOS`, instalá la GitHub App ahí, copiá
  `neo.yml` + `CLAUDE.md`, y configurá su preview en Railway.

---

## 8. Seguridad (resumen)

- Credenciales **solo** en GitHub Secrets / variables de Railway. Nada en el código.
- GitHub App acotada a permisos mínimos (Contents/Issues/PRs) y **solo a los repos autorizados**.
- Neo opera solo sobre repos de `NEO_REPOS`; salas/usuarios restringibles con
  `NEO_MATRIX_ROOMS` / `NEO_MATRIX_ALLOWED_SENDERS`.
- Verificación de firma en el webhook de GitHub.
- Previews aislados con Mongo efímero + seed sintético; guardarraíl que rechaza bases productivas.
- Branch protection: Neo no mergea sus propios PRs.

---

## 9. Checklist de criterios de aceptación

| Criterio | Cómo se cumple | Dónde |
|---|---|---|
| `@neo` en un issue genera un PR funcional | Workflow `neo.yml` (tag mode) + `CLAUDE.md` | §4 |
| `!neo` dispara el flujo y reporta el PR | Bot Matrix → `workflow_dispatch` → webhook de PR | §5 |
| Cada PR levanta un preview con URL dinámica | PR environments de Railway (`RAILWAY_PUBLIC_DOMAIN`) | §6.2 |
| Se duerme por inactividad | `sleepApplication: true` | §6.2 |
| Se destruye al cerrar el PR o con `!neo bajar pr-N` | Railway nativo + bot (`on_pull_request_closed`, teardown) | §6.3 |
| `NEO_JIRA_ENABLED=false` ⇒ ningún disparo de Jira | `jira.handle_event` corta si el switch está off | §7 |
| Branch protection: Neo no mergea sus PRs | Reglas de rama + PRs autoría de la App | §3 |
| Previews nunca conectados a bases productivas | Mongo efímero + guardarraíl del seed (probado) | §6.2 |

---

## 10. Estado del pilot (`uko-vue`) — validado localmente

Este repo se eligió como **pilot de prueba** (bajo riesgo). Validado en local antes de provisionar nada externo:

- ✅ `yarn build` en verde. **Fix aplicado:** el theme no compilaba de fábrica — error de tipos
  en [src/main.ts](../../src/main.ts) (`app.use(VueApexCharts)`); se resolvió con un cast a `Plugin`.
  Era necesario: el preview de Railway y la verificación de Neo corren `yarn build`.
- ✅ `yarn start` sirve en `0.0.0.0:$PORT` con **SPA fallback** (rutas profundas → 200).
  **Fix aplicado:** `$PORT` ahora se lee en [vite.config.ts](../../vite.config.ts) (`preview.port`),
  no por expansión de shell (que en Windows con yarn no funciona). Portable Windows/Linux.

**Simplificación del pilot:** como la app usa **mock API** (`src/__mock__`, sin backend real),
el preview puede validarse **front-only**. Para este pilot, los pasos de **API + Mongo + seed**
(§6.1, §6.2 punto 4-5) son **opcionales**: alcanza con el servicio del front para validar los
criterios de preview (URL dinámica, auto-sleep, bajada). El stack completo se valida después en un
repo con backend (`api_portal_cliente`).

Pendiente (requiere consola web, ver §3–§6): GitHub App, secretos, Railway, Matrix, branch protection.
