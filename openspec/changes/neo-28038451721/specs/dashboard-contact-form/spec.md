## ADDED Requirements

### Requirement: Página de contacto en el dashboard
El sistema SHALL exponer una página de contacto accesible en la ruta `/contact-us`,
registrada en `src/router/dashboardRoutes.ts` y renderizada a partir de
`src/pages/dashboard/Contact.vue`, dentro del layout estándar del dashboard.

#### Scenario: Usuario navega a la URL de contacto
- **WHEN** un usuario autenticado navega a `/contact-us`
- **THEN** el sistema renderiza la página de contacto dentro del layout del dashboard, con un
  formulario visible para nombre, email, asunto y mensaje

### Requirement: Entrada de navegación en el sidebar
El sistema SHALL incluir una entrada "Contact Us" en la navegación del sidebar
(`src/data/navigation.ts`) que enlace a la ruta `/contact-us`.

#### Scenario: Usuario abre el sidebar
- **WHEN** el usuario despliega el menú de navegación lateral
- **THEN** el sistema muestra una opción "Contact Us" en el grupo de navegación del dashboard
- **AND** al hacer click en esa opción el usuario es dirigido a `/contact-us`

### Requirement: Validación de campos del formulario
El formulario de contacto SHALL validar, antes de permitir el envío, que los campos nombre,
email, asunto y mensaje estén completos y que el email tenga formato válido, usando los
componentes `TextField`, `SelectField` y `TextAreaField` de `src/components/form`.

#### Scenario: Envío con campos incompletos
- **WHEN** el usuario intenta enviar el formulario sin completar un campo obligatorio
- **THEN** el sistema muestra un mensaje de error debajo del campo correspondiente
- **AND** no envía la petición al endpoint de contacto

#### Scenario: Email con formato inválido
- **WHEN** el usuario completa el campo email con un valor que no tiene formato de email
- **THEN** el sistema muestra un mensaje de error de validación en el campo email
- **AND** no envía la petición al endpoint de contacto

### Requirement: Envío del mensaje al endpoint de contacto
Cuando todos los campos son válidos, el sistema SHALL enviar el mensaje mediante una petición
`POST /api/contact` (a través de un store de Pinia dedicado), deshabilitando el botón de envío
mientras la petición está en curso.

#### Scenario: Envío exitoso
- **WHEN** el usuario completa todos los campos requeridos con datos válidos y confirma el
  envío
- **THEN** el sistema deshabilita el botón de envío mientras la petición está en curso
- **AND** envía una petición `POST /api/contact` con nombre, email, asunto y mensaje
- **AND** al recibir una respuesta exitosa, limpia el formulario y muestra una notificación de
  éxito

#### Scenario: Error en el envío
- **WHEN** la petición `POST /api/contact` responde con un error
- **THEN** el sistema muestra una notificación de error
- **AND** conserva los valores ingresados por el usuario en el formulario
- **AND** vuelve a habilitar el botón de envío

### Requirement: Mock del endpoint de contacto para preview sin backend
El sistema SHALL incluir un handler de `axios-mock-adapter` para `POST /api/contact` en
`src/__mock__/contact/`, registrado en `src/__mock__/index.ts`, que solo se carga cuando no
hay `VITE_API_BASE_URL` configurada (modo mock), de forma consistente con el resto de
`src/__mock__`.

#### Scenario: Preview sin variable VITE_API_BASE_URL
- **WHEN** la aplicación arranca sin `VITE_API_BASE_URL` definida
- **THEN** el sistema usa el mock de `/api/contact` y el formulario de contacto puede enviarse
  exitosamente sin backend real

#### Scenario: Preview con variable VITE_API_BASE_URL definida
- **WHEN** la aplicación arranca con `VITE_API_BASE_URL` definida
- **THEN** el sistema envía la petición `POST /api/contact` directamente contra esa URL base,
  sin cargar el mock de contacto
