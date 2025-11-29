@echo off
REM Activar entorno virtual
call venv\Scripts\activate

REM Ejecutar MCP Server
mcp dev .\server.py

pause
