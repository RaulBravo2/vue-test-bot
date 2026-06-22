## ADDED Requirements

### Requirement: User age field
El sistema SHALL almacenar y exponer la edad (`age`) de cada usuario como un dato numérico
entero positivo, tanto en los datos servidos por la API/mock como en el tipo `User` usado por el
front-end.

#### Scenario: Usuario con edad definida
- **WHEN** se obtiene un usuario desde la fuente de datos (API real o mock)
- **THEN** el objeto de usuario incluye la propiedad `age` con un valor numérico

### Requirement: Age column in user list
La tabla de usuarios SHALL mostrar una columna "Age" con la edad de cada usuario listado.

#### Scenario: Listado de usuarios con edades
- **WHEN** el usuario administrador visualiza la tabla de usuarios en `UserList.vue`
- **THEN** cada fila muestra la edad del usuario correspondiente en una columna "Age"

### Requirement: Age input in user form
El formulario de alta/edición de usuarios SHALL incluir un campo numérico para capturar la edad,
el cual es obligatorio y debe ser un número entero positivo.

#### Scenario: Alta de usuario sin edad
- **WHEN** el usuario administrador intenta crear un usuario nuevo sin completar el campo de edad
- **THEN** el formulario muestra un error de validación y no envía el formulario

#### Scenario: Alta de usuario con edad válida
- **WHEN** el usuario administrador completa el formulario de alta con una edad numérica positiva
  y envía el formulario
- **THEN** el usuario se crea con la edad ingresada

#### Scenario: Edición de usuario existente precarga la edad
- **WHEN** el usuario administrador abre el formulario de edición de un usuario existente
- **THEN** el campo de edad se precarga con el valor `age` actual de ese usuario
