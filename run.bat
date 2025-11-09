@echo off
REM AI Video Enhancer - Quick Start Script for Windows

echo ========================================
echo AI Video Enhancer
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run setup first:
    echo   python setup.py
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)

echo.
echo Starting AI Video Enhancer...
echo.
echo The application will open in your browser.
echo Press Ctrl+C to stop the server.
echo.

REM Run the application
streamlit run app.py

REM Deactivate on exit
deactivate
