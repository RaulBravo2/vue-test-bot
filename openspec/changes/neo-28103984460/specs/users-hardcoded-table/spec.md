## ADDED Requirements

### Requirement: Tabla estática en la vista de usuarios
La vista de usuarios (`Users.vue`) SHALL mostrar una tabla adicional con valores
hardcodeados en el propio componente, sin depender del store `useUsers()` ni de la
API mock de `src/__mock__/`.

#### Scenario: La tabla hardcodeada se muestra al entrar a la vista de usuarios
- **WHEN** un usuario autenticado navega a la vista de usuarios (`/users`)
- **THEN** se muestra, además de la tabla dinámica existente, una tabla con un conjunto
  fijo de filas de ejemplo definidas en el código del componente

#### Scenario: Los datos de la tabla no cambian con filtros ni búsqueda
- **WHEN** el usuario modifica el campo de búsqueda o el filtro de estado de la tabla
  dinámica existente
- **THEN** las filas de la tabla hardcodeada permanecen sin cambios, ya que no está
  conectada a `filters` ni a `useUsers()`

### Requirement: Consistencia visual con la tabla existente
La tabla hardcodeada SHALL reutilizar los componentes de `components/ui/table`
(shadcn-vue) usados por `UserList.vue`, de forma que mantenga el mismo estilo visual
(cabecera, filas, bordes) que el resto de tablas de la aplicación.

#### Scenario: La tabla usa los componentes de tabla compartidos
- **WHEN** se renderiza la nueva tabla en `Users.vue`
- **THEN** su markup utiliza `Table`, `TableHeader`, `TableRow`, `TableHead`,
  `TableBody` y `TableCell` de `@/components/ui/table`, igual que `UserList.vue`

### Requirement: Independencia del backend y del mock
La tabla hardcodeada SHALL renderizarse correctamente sin necesidad de que la API
mock (`src/__mock__/`) ni una API real (`VITE_API_BASE_URL`) estén disponibles.

#### Scenario: La tabla se ve igual con o sin backend disponible
- **WHEN** la aplicación se ejecuta en modo preview/dev sin que el mock de usuarios
  responda (por ejemplo, si la llamada de `useUsers()` falla o está pendiente)
- **THEN** la tabla hardcodeada de la vista de usuarios sigue mostrando sus filas de
  ejemplo sin verse afectada por el estado de carga ni por errores de la tabla dinámica
