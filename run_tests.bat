@echo off
REM Quick test runner for Windows
echo ====================================
echo Stock EDA Test Suite
echo ====================================
echo.

if not exist .venv (
    echo Error: Virtual environment not found
    echo Please run setup.py first
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing test dependencies...
python -m pip install -e ".[dev]" --quiet

echo.
echo Running tests...
echo.
python -m pytest -v

pause
