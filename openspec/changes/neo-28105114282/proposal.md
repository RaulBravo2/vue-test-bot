## Why

La tabla de usuarios (`UserList.vue`, vista `Users.vue`, store `useUsers`) consume hoy el
dataset mockeado de `src/__mock__/users/users.ts`. Ya existe una API real
(`api_portal_cliente`) que expone `GET /api/users` con el mismo shape de usuario
(`id, name, email, phone, role, status, address, image, createAt`), y el cliente axios ya
soporta apuntar a esa API mediante `VITE_API_BASE_URL` (`src/main.ts`). Falta dejar
configurada y verificada esa integración para que la tabla de usuarios deje de depender
del mock cuando hay una API real disponible (previews full-stack, producción futura).

## What Changes

- Configurar `VITE_API_BASE_URL` (documentación + valores de entorno en Railway/GitHub
  Secrets) para los entornos donde la tabla de usuarios debe consumir la API real.
- Verificar y, si es necesario, ajustar el store `useUsers` (`getUsers`, `getUserById`,
  `deleteUser`, `createNewUser`, `updateUser`) para que el contrato de petición/respuesta
  (paginación, filtros, shape `{ users, meta }`) coincida con el de `GET /api/users` (y
  demás verbos usados por el CRUD de usuarios) de la API real.
- Mantener sin cambios el fallback a `src/__mock__/users` cuando `VITE_API_BASE_URL` no
  está configurada (mecanismo ya implementado en `src/main.ts`), para no romper previews
  sin backend.
- Documentar cómo configurar la variable para que la tabla de usuarios use datos reales.

## Capabilities

### New Capabilities
- `user-directory-data-source`: define el origen de datos (API real vs mock) del listado
  y CRUD de usuarios, y la configuración de entorno que lo controla.

### Modified Capabilities
(ninguna — no existen specs previos en `openspec/specs/` para este repo)

## Impact

- Código: `src/stores/users.ts`, `src/sections/users/UserList.vue`,
  `src/pages/users/Users.vue`.
- `src/main.ts`: mecanismo de toggle mock/real ya existente; no se esperan cambios
  funcionales, sólo verificación.
- Variables de entorno: `VITE_API_BASE_URL` (Railway preview/producción, GitHub Secrets
  en CI).
- Documentación: `.env.example`, `README.md`.
- Sin cambios en `src/__mock__/users` (se preserva como fallback, tal como exigen los
  guardarraíles del proyecto).
