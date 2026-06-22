## Why

El texto de bienvenida de la tarjeta de introducción en la vista de gestión de aprendizaje
("Welcome Back! Watson") debe reemplazarse por un texto de prueba solicitado explícitamente
por el usuario, en mayúsculas.

## What Changes

- Reemplazar el texto "Welcome Back! Watson" por "HOLA SOY NEO Y ESTO ES UN TEST" en el
  encabezado de la tarjeta de introducción de la vista de gestión de aprendizaje.

## Capabilities

### New Capabilities
- `learning-management-intro-card`: Encabezado de bienvenida mostrado en la tarjeta de
  introducción de la vista de gestión de aprendizaje.

### Modified Capabilities
(ninguna; no existen specs previas para esta capability)

## Impact

- Archivo afectado: `src/sections/learning-management/intro/IntroCard.vue` (línea con el
  `<h5>` de bienvenida).
- No afecta API, datos mockeados, ni otras vistas.
