## 1. Configuración de entorno

- [x] 1.1 Documentar en `.env.example`/`README.md` que `VITE_API_BASE_URL` habilita
      datos reales en la tabla de usuarios (y el resto de módulos que pegan a
      `/api/*`), incluyendo el valor esperado para previews full-stack y producción.
      (`.env.example` ya lo documentaba; se agregó una sección "Configuración /
      Variables de entorno" en `README.md`.)
- [ ] 1.2 Configurar `VITE_API_BASE_URL` en las variables de Railway (preview y/o
      producción correspondiente) y/o GitHub Secrets de CI apuntando a la API real
      `api_portal_cliente`. **Pendiente**: requiere acceso a Railway/GitHub Secrets,
      fuera del alcance de este cambio de código (queda para quien administre esos
      entornos).

## 2. Verificación del contrato API

- [ ] 2.1 Confirmar contra `api_portal_cliente` el shape exacto de la respuesta de
      `GET /api/users` (envoltorio `{ users, meta }`, nombres de parámetros de
      paginación/filtro) y compararlo con lo que espera `src/stores/users.ts`.
      **Pendiente**: el repo `api_portal_cliente` no está disponible desde este
      working tree; no se pudo verificar contra la API real. `src/stores/users.ts`
      ya asume el contrato `{ users, meta }` descripto en el spec.
- [x] 2.2 Si el shape real difiere (paginación, nombres de campos), ajustar
      `getUsers`/`getUserById`/`deleteUser`/`createNewUser`/`updateUser` en
      `src/stores/users.ts` para normalizar la respuesta sin romper `UserList.vue`.
      (Ya pegan a `/api/users` con el shape `{ users, meta }` esperado; sin acceso a
      `api_portal_cliente` no hay diferencia detectada que ajustar.)
- [ ] 2.3 Verificar si `GET /api/users` requiere autenticación (token Firebase) y, de
      ser así, definir cómo adjuntarlo a las peticiones axios (confirmar si esto forma
      parte de este cambio o de uno aparte). **Pendiente**: no hay interceptor de
      axios que adjunte token hoy; queda fuera de este cambio según lo planteado en
      la propuesta.

## 3. Validación

- [ ] 3.1 Probar la tabla de usuarios en preview con `VITE_API_BASE_URL` apuntando a la
      API real: listado, búsqueda, filtro por estado, paginación, alta/baja/edición.
      **Pendiente**: requiere una instancia accesible de `api_portal_cliente`, no
      disponible en este entorno de ejecución.
- [ ] 3.2 Probar que sin `VITE_API_BASE_URL` el preview sigue funcionando con el mock
      (regresión). **Pendiente**: requiere levantar el dev server interactivamente;
      no se ejecutó en esta sesión (el mock no se tocó, por lo que el comportamiento
      debería preservarse).
- [x] 3.3 Dejar `yarn build` en verde (type-check + build). Verificado: `yarn build`
      compila sin errores de tipos.
