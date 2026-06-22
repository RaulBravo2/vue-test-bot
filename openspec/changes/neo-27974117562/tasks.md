## 1. Tipos

- [x] 1.1 Agregar el campo `age: number` a la interfaz `User` en `src/types/User.ts`
- [x] 1.2 Agregar el campo `age: number` a la interfaz `UserPayload` en `src/types/User.ts`

## 2. Mock de datos

- [x] 2.1 Agregar el valor `age` a cada usuario semilla en `src/__mock__/users/users.ts`

## 3. Listado de usuarios

- [x] 3.1 Agregar "Age" a `tableHeads` en `src/sections/users/UserList.vue`
- [x] 3.2 Agregar una `TableCell` que muestre `user.age` en cada fila de la tabla
- [x] 3.3 Ajustar el `colspan` del mensaje "No users found" si corresponde al nuevo total de
      columnas

## 4. Formulario de alta/edición

- [x] 4.1 Agregar `age` al `validationSchema` de Yup en `UserForm.vue` (número entero positivo,
      requerido)
- [x] 4.2 Agregar `age` a `initialValues` del formulario, precargando `user?.age` en edición
- [x] 4.3 Agregar `age` al `payload` enviado en `onSubmit`
- [x] 4.4 Agregar un `TextField` (o campo numérico equivalente) para "Age" en el template del
      formulario

## 5. Verificación

- [x] 5.1 Correr `yarn build` (type-check + build) y dejarlo en verde
