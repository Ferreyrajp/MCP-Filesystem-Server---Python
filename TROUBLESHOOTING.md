# Guía de Solución de Problemas - MCP Filesystem Server

## Problema: "No parece funcionar" / Claude no puede listar archivos

### Paso 1: Verificar la Configuración de Claude Desktop

1. **Ubicar el archivo de configuración:**
   - Presiona `Win + R`
   - Escribe: `%APPDATA%\Claude`
   - Presiona Enter
   - Busca el archivo `claude_desktop_config.json`

2. **Verificar el contenido del archivo:**
   
   El archivo debe tener esta estructura (ajusta las rutas a tu caso):

   ```json
   {
     "mcpServers": {
       "filesystem": {
         "command": "python",
         "args": [
           "i:/MCP-Server-filesystem/server.py",
           "C:/Users/TU_USUARIO/Documents",
           "C:/Users/TU_USUARIO/Desktop"
         ]
       }
     }
   }
   ```

   **IMPORTANTE**: 
   - Reemplaza `TU_USUARIO` con tu nombre de usuario real
   - Usa rutas absolutas completas
   - Puedes usar `/` o `\\` en las rutas

### Paso 2: Verificar que Python está en el PATH

Abre PowerShell o CMD y ejecuta:

```bash
python --version
```

Si no funciona, intenta:

```bash
python3 --version
```

Si ninguno funciona, necesitas agregar Python al PATH o usar la ruta completa en la configuración:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "C:/Users/TU_USUARIO/AppData/Local/Programs/Python/Python313/python.exe",
      "args": [
        "i:/MCP-Server-filesystem/server.py",
        "C:/Users/TU_USUARIO/Documents"
      ]
    }
  }
}
```

### Paso 3: Verificar que MCP está instalado

Ejecuta en la terminal:

```bash
pip show mcp
```

Si no está instalado:

```bash
pip install mcp
```

### Paso 4: Reiniciar Claude Desktop

**MUY IMPORTANTE**: Después de modificar `claude_desktop_config.json`:

1. Cierra completamente Claude Desktop (no solo minimizar)
2. Verifica en el Administrador de Tareas que no esté corriendo
3. Abre Claude Desktop nuevamente

### Paso 5: Verificar que el servidor está corriendo

En Claude Desktop, intenta usar esta herramienta:

```
list_allowed_directories
```

Si funciona, verás algo como:
```
Allowed directories:
C:/Users/TU_USUARIO/Documents
C:/Users/TU_USUARIO/Desktop
```

### Paso 6: Probar listar archivos

Si el paso anterior funcionó, prueba:

```
list_directory path="C:/Users/TU_USUARIO/Documents"
```

## Problemas Comunes y Soluciones

### Error: "No such file or directory"
- **Causa**: La ruta al `server.py` es incorrecta
- **Solución**: Verifica que la ruta en `args[0]` apunte correctamente a `server.py`

### Error: "Access denied"
- **Causa**: Intentas acceder a una ruta no permitida
- **Solución**: Agrega la ruta a la lista de `args` en la configuración

### Error: "python: command not found"
- **Causa**: Python no está en el PATH
- **Solución**: Usa la ruta completa a python.exe en `command`

### El servidor no aparece en Claude
- **Causa**: Configuración incorrecta o Claude no reiniciado
- **Solución**: 
  1. Verifica la sintaxis JSON (sin comas extras, comillas correctas)
  2. Reinicia Claude Desktop completamente

### Error: "Method not found"
- **Causa**: Versión incorrecta de MCP o servidor no iniciado
- **Solución**: 
  ```bash
  pip install --upgrade mcp
  ```

## Configuración de Ejemplo Completa

Aquí está una configuración completa que funciona:

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
        "i:/MCP-Server-filesystem"
      ]
    }
  }
}
```

## Verificación Manual del Servidor

Para probar que el servidor funciona fuera de Claude:

```bash
cd i:/MCP-Server-filesystem
python verify_tools.py
```

Deberías ver:
```
============================================================
MCP Filesystem Server - Tool Registration Test
============================================================

✅ Server initialized successfully
✅ Tools registered: 12

Registered tools:
------------------------------------------------------------
 1. read_text_file              - Read the complete contents...
 2. read_multiple_files         - Read multiple files...
...
```

## Logs de Diagnóstico

Para ver los logs de Claude Desktop:

1. Cierra Claude Desktop
2. Abre PowerShell
3. Ejecuta Claude desde la línea de comandos para ver los logs:
   ```bash
   & "C:\Users\TU_USUARIO\AppData\Local\Programs\Claude\Claude.exe"
   ```

Los errores del servidor MCP aparecerán en la consola.

## ¿Aún no funciona?

Si después de seguir todos estos pasos aún no funciona:

1. **Copia el contenido exacto de tu `claude_desktop_config.json`**
2. **Copia el error exacto que ves en Claude**
3. **Ejecuta y copia el resultado de:**
   ```bash
   python --version
   pip show mcp
   python verify_tools.py
   ```

Con esta información podré ayudarte mejor.
