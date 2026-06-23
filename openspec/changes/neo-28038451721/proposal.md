# neo-28038451721 — Formulario de contacto en el dashboard

## Why

El dashboard no tiene ninguna página propia para que un usuario autenticado envíe una
consulta o mensaje de contacto: la única pantalla de "Contact" existente vive en
`/support/contact` y es estática (tarjeta con mapa embebido y redes sociales, sin formulario
funcional). El equipo necesita una página nueva dentro del dashboard que use los componentes
de formulario ya existentes (`src/components/form`) y los de UI (`src/components/ui`) para
capturar nombre, email, asunto y mensaje, validarlos y enviarlos contra el nuevo endpoint de
contacto que expone `api_portal_cliente`, quedando accesible desde una ruta propia y desde la
navegación del sidebar.

## What Changes

- Se agrega una página nueva `src/pages/dashboard/Contact.vue` que renderiza un formulario de
  contacto reutilizando `TextField`, `SelectField` y `TextAreaField` de `src/components/form`
  y `Card`/`Button` de `src/components/ui`.
- Se agrega la ruta `contact` (`name: "dashboardContact"`, `path: "/contact-us"`) en
  `src/router/dashboardRoutes.ts`, apuntando a esa página.
- Se agrega una entrada "Contact Us" en `src/data/navigation.ts` (grupo "Overview", junto al
  resto de páginas de `src/pages/dashboard`) que enlaza a `/contact-us`.
- Se agrega un store de Pinia `src/stores/contact.ts` que expone una acción para enviar el
  mensaje vía `axios` (`POST /api/contact`), siguiendo el patrón ya usado por
  `src/stores/users.ts`.
- El formulario valida los campos con `vee-validate` + `yup` (nombre, email, asunto y mensaje
  obligatorios; email con formato válido) antes de habilitar el envío, deshabilita el botón de
  envío mientras la petición está en curso, y notifica éxito/error con `notivue`.
- Se agrega el mock `src/__mock__/contact/index.ts` (registrado en `src/__mock__/index.ts`)
  que simula `POST /api/contact` para que el preview funcione sin backend, sin afectar el modo
  con `VITE_API_BASE_URL` (API real) ya soportado en `src/main.ts`.

## Capabilities

### New Capabilities
- `dashboard-contact-form`: página y formulario de contacto del dashboard (ruta, entrada de
  sidebar, validación de campos, envío al endpoint de contacto y manejo de éxito/error).

### Modified Capabilities
(ninguna — no existen specs previos en `openspec/specs/` que cubran navegación o rutas del
dashboard; esta es la primera propuesta OpenSpec del repo)

## Impact

- **Código nuevo**: `src/pages/dashboard/Contact.vue`, `src/stores/contact.ts`,
  `src/__mock__/contact/index.ts`.
- **Código modificado**: `src/router/dashboardRoutes.ts`, `src/data/navigation.ts`,
  `src/__mock__/index.ts`.
- **API**: consume el endpoint `POST /api/contact` del repo `api_portal_cliente` (fuera de
  este repo). En preview/local sin `VITE_API_BASE_URL` se usa el mock equivalente.
- **Dependencias**: ninguna nueva; se reutilizan `vee-validate`, `yup`, `axios`, `pinia` y
  `notivue`, ya presentes en `package.json`.
