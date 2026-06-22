## Why

El listado, alta y edición de usuarios no permite registrar la edad de un usuario porque el
tipo `User` y sus consumidores (tabla, formulario y mock) no contemplan ese dato. El negocio
necesita poder ver y capturar la edad de cada usuario en el portal cliente.

## What Changes

- Agregar el campo `age` (número) a las interfaces `User` y `UserPayload` en
  `src/types/User.ts`.
- Mostrar la edad como una columna nueva en la tabla de usuarios
  (`src/sections/users/UserList.vue`).
- Agregar un campo de edad al formulario de alta/edición de usuarios
  (`src/sections/users/UserForm.vue`), con validación de que sea un número requerido y positivo.
- Agregar el valor `age` a cada usuario semilla del mock
  (`src/__mock__/users/users.ts`) para mantener paridad entre mock y API real cuando
  `VITE_API_BASE_URL` no está configurada.

## Capabilities

### New Capabilities
- `user-management`: gestión de usuarios del portal cliente (listado, alta, edición), incluyendo
  los datos de perfil que se muestran y capturan para cada usuario.

### Modified Capabilities
(ninguna; no existen specs previas en `openspec/specs/`)

## Impact

- `src/types/User.ts` — nuevo campo `age` en `User` y `UserPayload`.
- `src/sections/users/UserList.vue` — nueva columna "Age" en la tabla.
- `src/sections/users/UserForm.vue` — nuevo campo de formulario con validación (Yup).
- `src/__mock__/users/users.ts` — nuevo dato `age` en cada usuario semilla.
- No afecta rutas, stores ni la API real (`api_portal_cliente`), que queda fuera del alcance de
  este repo.
