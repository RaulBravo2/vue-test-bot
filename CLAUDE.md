# CLAUDE.md — uko-vue (portal cliente · front-end)

Guía para **Neo**, el asistente de desarrollo (Claude) que trabaja sobre este repo vía
GitHub (`@neo`), Matrix (`!neo`) y, opcionalmente, Jira. Leé este archivo antes de tocar
código y respetá las restricciones de la sección **Guardarraíles**.

## Qué es este repo

SPA de administración construida con **Vue 3 + TypeScript + Vite**. Es el **front-end** del
portal del cliente. La API real vive en un repo aparte (`api_portal_cliente`); acá la capa de
datos está **mockeada** con `axios-mock-adapter` (ver `src/__mock__/`). La autenticación usa
**Firebase** (config por variables `VITE_FIREBASE_*`).

## Stack

- **Vue 3.5** (Composition API, `<script setup>`) + **TypeScript 5.8**
- **Vite 6** (bundler / dev server / preview)
- **Pinia** (estado) · **vue-router 4** (ruteo, modo history → requiere SPA fallback)
- **Tailwind CSS v4** + **shadcn-vue** (componentes sobre `radix-vue`) — ver `components.json`
- **VeeValidate + Yup** (formularios) · **ApexCharts** (gráficos) · **notivue** (toasts)
- **Firebase** (auth) · **axios** + **axios-mock-adapter** (API simulada)

## Comandos

El lockfile commiteado es **`yarn.lock`** → el gestor canónico es **yarn** (es el que usa
Railway). `package-lock.json` está en `.gitignore`. Localmente cualquiera de los dos sirve.

```bash
yarn install           # instalar dependencias
yarn dev               # dev server en http://localhost:5050
yarn build             # type-check (vue-tsc) + build de producción a dist/
yarn preview           # previsualizar el build (local, puerto 5050)
yarn start             # servir dist/ en 0.0.0.0:$PORT (usado por Railway en previews)
```

> No hay suite de tests ni linter configurados. **El build (`yarn build`) es la verificación
> mínima obligatoria**: `vue-tsc` falla ante errores de tipos. Antes de abrir un PR, Neo debe
> dejar `yarn build` en verde.

## Estructura

```
src/
  main.ts            # bootstrap: Pinia, router, notivue, ApexCharts, mock API
  App.vue            # raíz
  router/            # definición de rutas (history mode)
  pages/             # vistas por ruta
  sections/          # bloques compositivos de páginas
  layout/            # shells (sidebar, topbar, etc.)
  components/        # componentes reutilizables (incluye shadcn-vue en components/ui)
  stores/            # stores de Pinia
  hooks/             # composables
  auth/              # integración Firebase / guards
  __mock__/          # handlers de axios-mock-adapter (NO es una API real)
  data/              # datos estáticos / seeds de UI
  lib/               # utilidades (lib/utils.ts = helper cn() de shadcn)
  types/             # tipos compartidos
  assets/            # CSS (index.css) e imágenes
```

Alias de import: **`@` → `src/`** (configurado en `vite.config.ts` y `tsconfig.json`).

## Convenciones

- Componentes en **`<script setup lang="ts">`**. Nombres de archivo de componente en
  **PascalCase** (`UserTable.vue`).
- Importá con el alias `@` (`import { cn } from "@/lib/utils"`), no con rutas relativas largas.
- Para UI nueva, **reutilizá los componentes de `components/ui` (shadcn-vue)** antes de crear
  unos desde cero. Clases utilitarias de Tailwind; combiná clases con el helper `cn()`.
- Estado compartido → store de Pinia en `src/stores`. Lógica reutilizable → composable en
  `src/hooks`.
- Llamadas a datos: hoy van contra el mock de `src/__mock__`. Si agregás endpoints, agregá su
  handler de mock para que el preview funcione sin backend.
- No agregues dependencias pesadas sin necesidad; preferí lo que ya está en `package.json`.

## Variables de entorno

Build-time (Vite las inyecta en el bundle, prefijo `VITE_`):

- `VITE_FIREBASE_*` — credenciales del proyecto Firebase (auth). Ver `.env.example`.
- `VITE_API_BASE_URL` — URL base de la API. En previews de Railway apunta a la API efímera
  del PR; en local/preview por defecto se usa el mock.

> **Nunca** hardcodees secretos en el código ni los subas al repo. Las credenciales viven en
> **GitHub Secrets** (CI) y en **variables de Railway** (runtime). `.env` no se commitea.

## Flujo de trabajo de Neo

1. Trabajá siempre en una **rama nueva** (`neo/<breve-descripcion>` o `neo/issue-<n>`), nunca
   sobre `main` directo.
2. Hacé el cambio más chico que resuelva el pedido. Seguí el estilo del código vecino.
3. Verificá con `npm run build` (type-check + build). Si falla, arreglalo antes de abrir el PR.
4. Abrí un **Pull Request** con descripción clara de qué/por qué y cómo probarlo. Enlazá el
   issue (`Closes #N`) cuando corresponda.
5. **No mergees**: la rama `main` está protegida y Neo no puede aprobar/mergear sus propios PRs.
   Un humano revisa y mergea.

## Guardarraíles (no negociables)

- **No mergear** PRs propios. La protección de rama lo impide; no intentes saltarla.
- **Previews ≠ producción.** Nunca conectes un preview a bases o servicios productivos. En
  preview se usa **MongoDB efímero con datos sintéticos**. Si ves credenciales productivas en
  un contexto de preview, detenete y reportalo.
- **Secretos** solo en GitHub Secrets / variables de Railway. No los imprimas en logs, PRs ni
  comentarios.
- **Producción no se toca** desde este flujo: sigue desplegada en la VPS actual, fuera del
  alcance de Neo.
- No borres `src/__mock__` ni la config de Firebase sin pedido explícito: el preview depende de
  ellos para levantar sin backend.
- Cambios de alcance amplio (migraciones de stack, borrado masivo, refactors transversales):
  proponé un plan en el PR/issue antes de ejecutar.
