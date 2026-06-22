## Why

El equipo quiere agregarle un toque visual distintivo (un guiño de marca/humor) a la pantalla
de login agregando una imagen de Condorito, sin alterar el flujo de autenticación ni el layout
existente del formulario de Sign In.

## What Changes

- Agregar un asset de imagen (`public/images/condorito.png`) al repo.
- Mostrar la imagen con un `<img>` en `src/pages/sessions/Login.vue`, dentro del panel
  izquierdo de branding (junto al logo `Uko`, cerca de la línea ~52) o como elemento
  decorativo cercano al formulario de Sign In.
- Mantener el layout responsivo y las clases Tailwind existentes: la imagen es un agregado
  visual, no debe desplazar ni romper la disposición actual del panel de branding ni del
  formulario.
- Incluir un atributo `alt` descriptivo para accesibilidad.

## Capabilities

### New Capabilities
- `login-branding`: imagen decorativa de marca/branding en el panel izquierdo de la pantalla
  de login.

### Modified Capabilities
(ninguna — no cambia el comportamiento de autenticación ni otros requisitos existentes)

## Impact

- Archivos afectados: `src/pages/sessions/Login.vue` (template), nuevo asset estático en
  `public/images/condorito.png`.
- No afecta la lógica de autenticación (`useAuth`), validaciones del formulario, ni rutas.
- No requiere cambios de backend ni de mocks (`src/__mock__`).
