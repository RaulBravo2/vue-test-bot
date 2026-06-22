## ADDED Requirements

### Requirement: Imagen decorativa de Condorito en el login
La pantalla de login (`src/pages/sessions/Login.vue`) SHALL mostrar una imagen de Condorito
servida desde un asset estático del proyecto (`public/images/condorito.png`), ubicada en el
panel izquierdo de branding o como elemento decorativo cercano al formulario de Sign In.

#### Scenario: La imagen se muestra en el panel de branding
- **WHEN** un usuario carga la pantalla de login en un viewport `lg` o mayor (donde el panel
  izquierdo de branding es visible)
- **THEN** la imagen de Condorito se renderiza dentro de ese panel, junto al logo `Uko`,
  usando un `<img>` con `src="/images/condorito.png"`

#### Scenario: La imagen tiene texto alternativo
- **WHEN** se inspecciona el elemento `<img>` de Condorito en el DOM
- **THEN** dicho elemento tiene un atributo `alt` no vacío que describe la imagen (por ejemplo,
  `alt="Condorito"`)

### Requirement: El layout existente del login no se rompe
El agregado de la imagen de Condorito SHALL preservar el layout responsivo y las clases
Tailwind existentes de `Login.vue`, sin desplazar ni ocultar el logo `Uko`, el título de
bienvenida, ni el formulario de Sign In.

#### Scenario: El formulario de Sign In permanece funcional y visible
- **WHEN** se agrega el `<img>` de Condorito al template de `Login.vue`
- **THEN** el formulario de Sign In (campos de email, password, checkbox "Remember me" y botón
  "Sign In") sigue visible y funcional, sin cambios en su comportamiento de validación o envío

#### Scenario: El panel de branding mantiene su estructura en pantallas chicas
- **WHEN** la pantalla de login se visualiza en un viewport menor a `lg` (donde el panel
  izquierdo de branding está oculto por `hidden lg:flex`)
- **THEN** la imagen de Condorito tampoco se muestra en ese viewport, preservando el
  comportamiento responsivo actual del panel
