@echo off
REM Spanish NER Service - Setup Script for Windows
REM This script sets up a virtual environment and installs all dependencies

echo 🚀 Setting up Spanish NER Service...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo [SUCCESS] Python found

REM Create virtual environment
echo [INFO] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists. Removing old environment...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo [INFO] Installing Python dependencies...
if not exist requirements.txt (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

REM Download spaCy model
echo [INFO] Downloading Spanish NER model...
python -m spacy download es_core_news_md
if %errorlevel% neq 0 (
    echo [WARNING] Could not download primary model (es_core_news_md)
)

REM Try to download fallback model
echo [INFO] Downloading fallback Spanish NER model...
python -m spacy download es_core_news_sm
if %errorlevel% neq 0 (
    echo [WARNING] Could not download fallback model (es_core_news_sm)
)

echo [SUCCESS] Setup completed!

echo.
echo 📋 Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Test the CLI:
echo    python -m src.cli "Juan vive en Madrid y trabaja en Google España."
echo.
echo 3. Start the web server:
echo    python -m src.web_server
echo.
echo 4. Access the API documentation:
echo    http://localhost:8000/docs
echo.
echo 5. To deactivate the virtual environment when done:
echo    deactivate

pause