@echo off
echo ============================================================
echo Verificacion Rapida del Servidor MCP Filesystem
echo ============================================================
echo.

echo [1/4] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado en PATH
    echo Intenta con: python3 --version
    python3 --version
)
echo.

echo [2/4] Verificando paquete MCP...
pip show mcp
if %errorlevel% neq 0 (
    echo ERROR: Paquete MCP no instalado
    echo Ejecuta: pip install mcp
)
echo.

echo [3/4] Verificando herramientas registradas...
python verify_tools.py
echo.

echo [4/4] Ubicacion del archivo de configuracion de Claude:
echo %APPDATA%\Claude\claude_desktop_config.json
echo.

echo ============================================================
echo Verificacion completada
echo ============================================================
echo.
echo Si todo esta OK arriba, verifica:
echo 1. Que claude_desktop_config.json tenga la configuracion correcta
echo 2. Que hayas reiniciado Claude Desktop COMPLETAMENTE
echo 3. Que las rutas en args[] sean las que quieres permitir
echo.
pause
