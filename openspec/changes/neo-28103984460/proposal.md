## Why

El stakeholder pidió agregar una tabla con datos de ejemplo (hardcodeados) en la vista de
usuarios (`src/pages/users/Users.vue`) para poder visualizar rápidamente un layout de
referencia sin depender de la API mock ni del store de usuarios existente.

## What Changes

- Agregar un nuevo componente de sección (p. ej. `src/sections/users/UserHardcodedTable.vue`)
  que renderiza una tabla con un set fijo de filas y columnas de ejemplo (datos hardcodeados
  en el propio componente, sin pasar por `useUsers()` ni por `src/__mock__/`).
- Mostrar esa tabla dentro de `src/pages/users/Users.vue`, debajo de la tabla dinámica
  existente (`UserList`), sin alterar el comportamiento de filtros, búsqueda ni paginación
  de la tabla actual.
- Reutilizar los componentes de tabla de `components/ui/table` (shadcn-vue) para mantener
  consistencia visual con `UserList.vue`.

## Capabilities

### New Capabilities
- `users-hardcoded-table`: tabla estática con valores de ejemplo embebidos en el componente,
  visible en la vista de usuarios, independiente del store/API.

### Modified Capabilities
(ninguna — no se modifica el comportamiento de la tabla dinámica de usuarios existente)

## Impact

- Código afectado: `src/pages/users/Users.vue` (agrega el nuevo componente a la plantilla),
  nuevo archivo `src/sections/users/UserHardcodedTable.vue`.
- No afecta `src/stores/users`, `src/__mock__/` ni rutas.
- No requiere cambios de API, variables de entorno ni dependencias nuevas.
