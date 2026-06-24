## ADDED Requirements

### Requirement: Origen de datos real para el listado de usuarios
El sistema SHALL obtener el listado de usuarios desde el endpoint real `GET /api/users`
de la API del portal cliente cuando la variable de entorno `VITE_API_BASE_URL` está
configurada, en lugar de usar el dataset mockeado de `src/__mock__/users/users.ts`.

#### Scenario: VITE_API_BASE_URL configurada
- **WHEN** la aplicación se construye/ejecuta con `VITE_API_BASE_URL` apuntando a una
  instancia accesible de la API real
- **THEN** el store `useUsers` y la tabla `UserList.vue` SHALL mostrar los usuarios
  devueltos por `GET /api/users` de esa API, y no los datos de
  `src/__mock__/users/users.ts`

### Requirement: Fallback a datos mockeados sin configuración de API
El sistema SHALL continuar usando el dataset mockeado de `src/__mock__/users/users.ts`
(vía `axios-mock-adapter`) cuando `VITE_API_BASE_URL` no esté configurada, para que el
preview siga funcionando sin backend.

#### Scenario: VITE_API_BASE_URL ausente
- **WHEN** la aplicación se construye/ejecuta sin `VITE_API_BASE_URL` definida
- **THEN** el store `useUsers` SHALL obtener los usuarios del mock de
  `src/__mock__/users` y la tabla SHALL renderizarlos sin requerir un backend real

### Requirement: Compatibilidad del contrato de petición/respuesta
La respuesta real de `GET /api/users` SHALL incluir, para cada usuario, los campos `id, name, email, phone, role, status, address, image, createAt`, y SHALL soportar los parámetros de paginación y filtro ya usados por el store (`page`, `search`, `status`), devolviendo una estructura `{ users, meta }` compatible con la que consumen `UserList.vue` y `TablePagination` (`meta.page`, `meta.total`, `meta.totalPages`, `meta.firstIndex`, `meta.lastIndex`).

#### Scenario: Filtros y paginación contra la API real
- **WHEN** se cambia la página, el texto de búsqueda o el filtro de estado en la vista
  de usuarios con la API real configurada
- **THEN** el store SHALL enviar esos parámetros a `GET /api/users` y SHALL actualizar
  `state.users` y `state.meta` con la respuesta real, sin errores de tipo ni de UI

### Requirement: Manejo de errores de la API real
El sistema SHALL exponer un estado de error visible (`state.error`) sin romper la tabla cuando la petición a la API real falle (error de red, status HTTP de error o respuesta con shape inesperado), de forma equivalente a como ocurre hoy con el mock.

#### Scenario: La API real responde con error
- **WHEN** `GET /api/users` contra la API real responde con un error de red o un status
  de error
- **THEN** el store SHALL setear `state.error` con un mensaje y SHALL dejar
  `state.isLoading` en `false`, y la tabla SHALL seguir siendo usable (sin quedar en
  loading infinito ni crashear)
