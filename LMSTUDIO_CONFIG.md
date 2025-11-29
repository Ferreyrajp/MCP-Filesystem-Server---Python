# Configuración para LM Studio

## MCP Filesystem Server en LM Studio

LM Studio tiene su propia forma de configurar servidores MCP.

### Paso 1: Ubicar el archivo de configuración

El archivo de configuración de LM Studio está en:

**Windows**: `%USERPROFILE%\.lmstudio\config.json`

O también puede estar en:
- `C:\Users\TU_USUARIO\.lmstudio\config.json`
- Dentro de la carpeta de instalación de LM Studio

### Paso 2: Configurar el servidor MCP

Abre el archivo `config.json` de LM Studio y agrega la configuración del servidor MCP:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": [
        "i:/MCP-Server-filesystem/server.py",
        "C:/Users/ferre/Documents",
        "C:/Users/ferre/Desktop",
        "i:/MCP-Server-filesystem"
      ],
      "env": {}
    }
  }
}
```

### Paso 3: Configuración alternativa con ruta completa a Python

Si Python no está en el PATH:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "C:/Users/ferre/AppData/Local/Programs/Python/Python313/python.exe",
      "args": [
        "i:/MCP-Server-filesystem/server.py",
        "C:/Users/ferre/Documents",
        "C:/Users/ferre/Desktop"
      ],
      "env": {}
    }
  }
}
```

### Paso 4: Reiniciar LM Studio

1. Cierra completamente LM Studio
2. Abre LM Studio nuevamente
3. El servidor MCP debería iniciarse automáticamente

### Paso 5: Verificar en LM Studio

En LM Studio, deberías poder:

1. Ver el servidor "filesystem" en la lista de MCP servers
2. Ver las herramientas disponibles (read_text_file, list_directory, etc.)
3. Usar las herramientas en el chat

### Ejemplo de uso en LM Studio

Una vez configurado, puedes pedirle al modelo:

```
"Lista los archivos en C:/Users/ferre/Documents"
```

Y el modelo debería usar la herramienta `list_directory` automáticamente.

### Configuración completa de ejemplo para LM Studio

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": [
        "i:/MCP-Server-filesystem/server.py",
        "C:/Users/ferre/Documents",
        "C:/Users/ferre/Desktop",
        "C:/Users/ferre/Downloads",
        "C:/Users/ferre/Projects",
        "i:/MCP-Server-filesystem"
      ],
      "env": {},
      "disabled": false
    }
  }
}
```

### Verificar que el servidor funciona

Antes de configurar en LM Studio, verifica que el servidor funciona:

```bash
cd i:/MCP-Server-filesystem
python server.py C:/Users/ferre/Documents
```

El servidor debería mostrar:
```
Usage: python server.py [allowed-directory] [additional-directories...]
...
Initialized with allowed directories: ['C:\\Users\\ferre\\Documents']
```

### Troubleshooting para LM Studio

1. **El servidor no aparece**: Verifica que el archivo config.json esté en la ubicación correcta
2. **Error de Python**: Usa la ruta completa a python.exe en `command`
3. **No puede acceder a archivos**: Verifica que las rutas en `args` sean correctas
4. **Servidor no inicia**: Revisa los logs de LM Studio (usualmente en la interfaz)

### Diferencias con Claude Desktop

- LM Studio usa `config.json` en lugar de `claude_desktop_config.json`
- La ubicación del archivo es diferente (`%USERPROFILE%\.lmstudio\`)
- LM Studio puede tener una interfaz para configurar MCP servers (depende de la versión)

### Notas importantes

- Asegúrate de que `pip install mcp` esté ejecutado
- Las rutas deben ser absolutas
- Reinicia LM Studio después de modificar la configuración
- Verifica que la versión de LM Studio soporte MCP (versiones recientes)
