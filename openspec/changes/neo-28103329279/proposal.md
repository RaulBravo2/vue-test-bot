# Agregar archivo NOTAS.md en la raíz del repo

## Why

RaulBravo2 pidió, vía issue de GitHub, contar con un archivo `NOTAS.md` en la raíz del
repositorio con el contenido `hola raul`. Es un pedido puntual y de bajo riesgo (no toca
código de la app ni configuración), pero se formaliza como cambio OpenSpec para dejar
trazabilidad de qué se agregó y por qué.

## What Changes

- Crear el archivo `NOTAS.md` en la raíz del repo (mismo nivel que `package.json` y
  `CLAUDE.md`).
- El archivo debe contener una única línea de texto: `hola raul`.
- No se modifica código de la aplicación (`src/`), configuración de build, ni el mock de la
  API.
