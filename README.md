# MCP Filesystem Server - Python

Servidor MCP (Model Context Protocol) para acceso seguro al sistema de archivos, implementado en Python basado en el repositorio oficial de TypeScript de [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem).

## Características

- **14 herramientas** para operaciones completas de archivos
- **Seguridad primero**: Validación de rutas y prevención de ataques de traversal
- **Soporte MCP Roots Protocol**: Actualización dinámica de directorios permitidos
- **Multiplataforma**: Compatible con Windows, Linux y macOS (incluyendo WSL)

## Instalación

```bash
# Clonar o descargar el repositorio
cd MCP-Server-filesystem

# Instalar dependencias
pip install mcp
```

> **Nota**: El paquete `mcp` incluye FastMCP, que es el framework utilizado para este servidor.

## Uso

### Método 1: Argumentos de línea de comandos

```bash
python server.py /ruta/al/directorio/permitido /otra/ruta/permitida
```

### Método 2: Configuración en Cliente MCP

#### Para LM Studio

Crea o edita el archivo de configuración de LM Studio:

**Ubicación**: `C:\Users\TU_USUARIO\.lmstudio\config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": [
        "i:/MCP-Server-filesystem/server.py",
        "C:/Users/TU_USUARIO/Documents",
        "C:/Users/TU_USUARIO/Desktop"
      ],
      "env": {},
      "disabled": false
    }
  }
}
```

**Después de editar, reinicia LM Studio completamente.**

Ver guía completa: [LMSTUDIO_CONFIG.md](LMSTUDIO_CONFIG.md)

#### Para Claude Desktop

Edita el archivo de configuración de Claude Desktop:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": ["i:/MCP-Server-filesystem/server.py", "i:/MCP-Server-filesystem"]
    }
  }
}
```

También puedes usar el archivo de ejemplo incluido: `claude_desktop_config.json`

## Configuración de Rutas Permitidas

El servidor MCP filesystem **solo puede acceder a las rutas que especifiques**. Esto es una característica de seguridad importante.

### Opción 1: Configuración en Claude Desktop (Recomendado)

Edita el archivo de configuración de Claude Desktop y especifica las rutas en el array `args`:

**Ejemplo con una sola ruta:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": [
        "i:/MCP-Server-filesystem/server.py",
        "C:/Users/tu_usuario/Documents"
      ]
    }
  }
}
```

**Ejemplo con múltiples rutas:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": [
        "i:/MCP-Server-filesystem/server.py",
        "C:/Users/tu_usuario/Documents",
        "C:/Users/tu_usuario/Projects",
        "D:/Trabajo"
      ]
    }
  }
}
```

**Después de editar el archivo, reinicia Claude Desktop.**

### Opción 2: Línea de Comandos

Si ejecutas el servidor manualmente:

```bash
# Una sola ruta
python server.py C:/Users/tu_usuario/Documents

# Múltiples rutas
python server.py C:/Users/tu_usuario/Documents C:/Users/tu_usuario/Projects D:/Trabajo
```

### Notas Importantes sobre Rutas

1. **Múltiples rutas**: Puedes especificar tantas rutas como necesites, separadas por espacios
2. **Formato de rutas**:
   - Windows: `C:/Users/...` o `C:\\Users\\...` (ambos funcionan)
   - Linux/macOS: `/home/usuario/...`
   - El servidor normaliza automáticamente las rutas
3. **Rutas absolutas**: Siempre usa rutas absolutas para evitar confusiones
4. **Subdirectorios**: Si permites `C:/Users/tu_usuario/Documents`, automáticamente se permite acceso a todos sus subdirectorios
5. **Seguridad**: El servidor **rechazará** cualquier intento de acceder a rutas fuera de las permitidas

### Verificar Rutas Configuradas

Una vez que el servidor esté corriendo en Claude, puedes usar la herramienta `list_allowed_directories` para ver qué rutas están configuradas:

```
list_allowed_directories()
```

Esto mostrará todas las rutas a las que el servidor tiene acceso.

## Herramientas Disponibles

### Operaciones de Lectura

#### `read_text_file`
Lee el contenido completo de un archivo como texto.
- **Parámetros:**
  - `path` (string): Ruta al archivo
  - `head` (number, opcional): Primeras N líneas
  - `tail` (number, opcional): Últimas N líneas

#### `read_media_file`
Lee archivos de imagen o audio y devuelve datos en base64.
- **Parámetros:**
  - `path` (string): Ruta al archivo multimedia

#### `read_multiple_files`
Lee múltiples archivos simultáneamente.
- **Parámetros:**
  - `paths` (string[]): Array de rutas de archivos

### Operaciones de Escritura

#### `write_file`
Crea un archivo nuevo o sobrescribe uno existente.
- **Parámetros:**
  - `path` (string): Ruta al archivo
  - `content` (string): Contenido a escribir

#### `edit_file`
Realiza ediciones selectivas basadas en líneas con vista previa de diff.
- **Parámetros:**
  - `path` (string): Ruta al archivo
  - `edits` (array): Lista de operaciones de edición
    - `oldText` (string): Texto a buscar
    - `newText` (string): Texto de reemplazo
  - `dryRun` (boolean): Vista previa sin aplicar cambios

### Operaciones de Directorio

#### `create_directory`
Crea un directorio nuevo o asegura que existe.
- **Parámetros:**
  - `path` (string): Ruta al directorio

#### `list_directory`
Lista el contenido de un directorio con prefijos [FILE] o [DIR].
- **Parámetros:**
  - `path` (string): Ruta al directorio

#### `list_directory_with_sizes`
Lista el contenido con tamaños de archivo.
- **Parámetros:**
  - `path` (string): Ruta al directorio
  - `sortBy` (string, opcional): Ordenar por "name" o "size"

#### `directory_tree`
Obtiene estructura de árbol JSON recursiva.
- **Parámetros:**
  - `path` (string): Directorio inicial
  - `excludePatterns` (string[]): Patrones a excluir

### Gestión de Archivos

#### `move_file`
Mueve o renombra archivos y directorios.
- **Parámetros:**
  - `source` (string): Ruta origen
  - `destination` (string): Ruta destino

#### `search_files`
Búsqueda recursiva de archivos que coincidan con patrones.
- **Parámetros:**
  - `path` (string): Directorio inicial
  - `pattern` (string): Patrón de búsqueda (glob)
  - `excludePatterns` (string[]): Patrones a excluir

#### `get_file_info`
Obtiene metadatos detallados de archivo/directorio.
- **Parámetros:**
  - `path` (string): Ruta al archivo o directorio

### Gestión del Servidor

#### `list_allowed_directories`
Lista todos los directorios a los que el servidor puede acceder.
- Sin parámetros

## Características de Seguridad

1. **Validación de rutas**: Todas las operaciones validan que las rutas estén dentro de directorios permitidos
2. **Resolución de symlinks**: Previene ataques mediante enlaces simbólicos
3. **Escrituras atómicas**: Previene condiciones de carrera
4. **Sin bytes nulos**: Rechaza rutas con caracteres nulos
5. **Normalización de rutas**: Maneja diferentes formatos de ruta de forma segura

## Arquitectura

```
MCP-Server-filesystem/
├── server.py              # Servidor principal con 14 herramientas
├── lib.py                 # Biblioteca de operaciones de archivos
├── path_utils.py          # Utilidades de normalización de rutas
├── path_validation.py     # Validación de seguridad
├── roots_utils.py         # Soporte MCP roots protocol
└── requirements.txt       # Dependencias Python
```

## Ejemplos de Uso

### Leer un archivo
```python
# A través del cliente MCP
read_text_file(path="i:/MCP-Server-filesystem/README.md")
```

### Editar un archivo con vista previa
```python
edit_file(
    path="i:/MCP-Server-filesystem/config.json",
    edits=[{
        "oldText": "\"debug\": false",
        "newText": "\"debug\": true"
    }],
    dryRun=True  # Vista previa primero
)
```

### Buscar archivos
```python
search_files(
    path="i:/MCP-Server-filesystem",
    pattern="**/*.py",
    excludePatterns=["**/__pycache__/**", "**/venv/**"]
)
```

## Desarrollo

### Estructura de Módulos

- **path_utils.py**: Normalización de rutas multiplataforma
- **path_validation.py**: Verificaciones de seguridad
- **roots_utils.py**: Manejo del protocolo MCP roots
- **lib.py**: Operaciones de archivos core (I/O, edición, búsqueda)
- **server.py**: Implementación del servidor MCP

### Pruebas

```bash
# Ejecutar el servidor en modo de prueba
python server.py i:/MCP-Server-filesystem

# El servidor esperará conexiones MCP en stdio
```

## Licencia

MIT

## Créditos

Basado en la implementación oficial de TypeScript del [MCP Filesystem Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) por Anthropic.
