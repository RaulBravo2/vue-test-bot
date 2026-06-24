## ADDED Requirements

### Requirement: Archivo NOTAS.md en la raíz
El repositorio SHALL contener un archivo `NOTAS.md` en su directorio raíz (al mismo nivel
que `package.json`).

#### Scenario: El archivo existe con el saludo esperado
- **WHEN** se inspecciona la raíz del repositorio tras aplicar el cambio
- **THEN** existe un archivo `NOTAS.md`
- **AND** su contenido incluye la línea de texto `hola raul`
