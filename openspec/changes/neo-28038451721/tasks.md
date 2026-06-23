## 1. Store y mock de contacto

- [x] 1.1 Crear `src/stores/contact.ts` (Pinia) con una acción `sendContactMessage(payload)`
      que haga `axios.post("/api/contact", payload)`, siguiendo el patrón de
      `src/stores/users.ts`
- [x] 1.2 Crear `src/__mock__/contact/index.ts` con `Mock.onPost("/api/contact")` que
      responda `200` con el payload recibido y `400` si falta algún campo requerido
- [x] 1.3 Registrar el mock de contacto en `src/__mock__/index.ts`

## 2. Página y formulario de contacto

- [x] 2.1 Crear `src/pages/dashboard/Contact.vue` con un formulario usando `TextField`
      (nombre, email, asunto), `SelectField` (motivo/categoría) y `TextAreaField` (mensaje) de
      `src/components/form`, dentro de un `Card` de `src/components/ui`
- [x] 2.2 Definir el `validationSchema` con `vee-validate` + `yup`: nombre, email, asunto y
      mensaje requeridos; email con formato válido
- [x] 2.3 Implementar `onSubmit` con `handleSubmit`/`isSubmitting`: llamar al store de
      contacto, deshabilitar el botón mientras se envía, resetear el formulario y notificar
      éxito con `notivue` en caso exitoso
- [x] 2.4 Manejar el caso de error de la petición mostrando una notificación de error y
      conservando los valores ingresados

## 3. Ruteo y navegación

- [x] 3.1 Agregar la entrada `contact` (`name: "dashboardContact"`, `path: "/contact-us"`) en
      `src/router/dashboardRoutes.ts` apuntando a `Contact.vue`
- [x] 3.2 Agregar la entrada "Contact Us" en el grupo correspondiente de
      `src/data/navigation.ts`, enlazando a `/contact-us`

## 4. Verificación

- [x] 4.1 Correr `yarn build` (type-check + build) y dejarlo en verde
- [x] 4.2 Probar manualmente en `yarn dev`: navegar desde el sidebar a "Contact Us", enviar el
      formulario con datos válidos (mock) y verificar el caso de validación con campos vacíos
