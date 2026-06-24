## 1. Componente de tabla hardcodeada

- [x] 1.1 Crear `src/sections/users/UserHardcodedTable.vue` con un array local de filas de
      ejemplo (datos hardcodeados en el `<script setup>`, sin llamadas a store ni API)
- [x] 1.2 Construir el markup de la tabla reutilizando `Table`, `TableHeader`, `TableRow`,
      `TableHead`, `TableBody` y `TableCell` de `@/components/ui/table`
- [x] 1.3 Definir columnas de ejemplo coherentes con `UserList.vue` (p. ej. nombre, email,
      estado) usando solo los datos hardcodeados del paso 1.1

## 2. Integración en la vista de usuarios

- [x] 2.1 Importar y renderizar `UserHardcodedTable` en `src/pages/users/Users.vue`, debajo
      de `UserList`
- [x] 2.2 Verificar que los filtros de búsqueda/estado de la tabla dinámica no afecten a la
      tabla hardcodeada

## 3. Verificación

- [x] 3.1 Ejecutar `yarn build` (type-check + build) y dejarlo en verde
- [x] 3.2 Revisar visualmente la vista `/users` en `yarn dev` para confirmar que ambas tablas
      se muestran correctamente
