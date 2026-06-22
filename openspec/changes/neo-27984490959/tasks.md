## 1. Asset

- [x] 1.1 Agregar el archivo `public/images/condorito.png` al repo.

## 2. Implementación en Login.vue

- [x] 2.1 Agregar un `<img>` apuntando a `/images/condorito.png` con `alt` descriptivo, dentro
      del panel izquierdo de branding (junto al logo `Uko`, ~línea 52) o como elemento
      decorativo cercano al formulario de Sign In.
- [x] 2.2 Ajustar clases Tailwind del `<img>` (tamaño/márgenes) para que no desplace ni rompa el
      layout existente del panel de branding ni del formulario.

## 3. Verificación

- [x] 3.1 Correr `yarn build` (type-check + build) y dejarlo en verde.
- [x] 3.2 Verificar visualmente en `yarn dev` que la imagen se ve en viewport `lg+` y que el
      panel de branding se sigue ocultando correctamente en viewports chicos.
