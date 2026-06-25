@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo Groq MCP Server Setup (Windows)
echo ==================================================

:: Navigate to project root directory
cd /d "%~dp0.."

:: Check if uv is installed
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: uv is not installed.
    echo Please install uv first. You can run:
    echo   pip install uv
    echo Or install it from: https://github.com/astral-sh/uv
    exit /b 1
)

:: Create or update virtual environment
if not exist .venv (
    echo Creating virtual environment...
    uv venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
) else (
    echo Virtual environment already exists. Skipping creation...
)

:: Install dependencies
echo Installing dependencies with uv...
uv pip install -e ".[dev]"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install dependencies.
    exit /b 1
)

:: Install pre-commit hooks (if pre-commit is available)
where pre-commit >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Setting up pre-commit hooks...
    pre-commit install || echo Info: pre-commit install failed. Skipping.
) else (
    if exist .venv\Scripts\pre-commit.exe (
        echo Setting up pre-commit hooks...
        .venv\Scripts\pre-commit.exe install || echo Info: pre-commit install failed. Skipping.
    ) else (
        echo Info: pre-commit command not found. Skipping pre-commit install.
    )
)

echo.
echo ==================================================
echo Setup complete! Virtual environment is ready.
echo To activate the virtual environment, run:
echo   .venv\Scripts\activate.bat
echo ==================================================
exit /b 0
