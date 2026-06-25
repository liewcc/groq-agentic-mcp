@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo Installing Groq MCP Server in Claude Desktop...
echo ==================================================

:: Navigate to project root directory
cd /d "%~dp0.."

:: Check if uv is installed
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: uv is not installed. Please install it first.
    exit /b 1
)

:: Run config.py to register to Claude Desktop & Antigravity
echo Updating configuration files (Claude Desktop ^& Antigravity)...
uv run python config.py
set CONFIG_STATUS=%ERRORLEVEL%

:: Attempt standard mcp install (ignore errors as config.py is already done)
if %CONFIG_STATUS% EQU 0 (
    echo Attempting optional registration via standard mcp install command...
    uv run mcp install server.py --with python-dotenv --with rapidfuzz --with sounddevice --with soundfile --with-editable . -f .env >nul 2>&1
    
    echo.
    echo ==================================================
    echo Installation successful!
    echo Groq MCP Server is configured for Claude Desktop and Antigravity.
    echo Please restart or refresh your Claude Desktop client.
    echo ==================================================
    exit /b 0
) else (
    echo.
    echo Error: Failed to configure Groq MCP server.
    echo Make sure you have created your .env file with a valid GROQ_API_KEY.
    exit /b 1
)


