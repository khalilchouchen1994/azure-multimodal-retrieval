@echo off  
REM Setup Script for Project  
REM ------------------------  
  
echo Creating the virtual environment...  
python -m venv .venv  
  
IF NOT EXIST ".venv\Scripts\activate.bat" (  
    echo Error: Virtual environment creation failed.  
    exit /b 1  
)  
  
echo Activating the virtual environment...  
call .venv\Scripts\activate.bat  
  
echo Upgrading pip and installing required packages...  
python -m pip install --upgrade pip  
IF NOT %ERRORLEVEL%==0 (  
    echo Error: Failed to upgrade pip.  
    exit /b 1  
)  
pip install -r requirements.txt  
IF NOT %ERRORLEVEL%==0 (  
    echo Error: Failed to install required packages.  
    exit /b 1  
)  
  
echo Extracting Poppler...  
IF NOT EXIST "poppler-24.08.0.zip" (  
    echo Error: poppler-24.08.0.zip not found.  
    exit /b 1  
)  
REM Using PowerShell to extract the ZIP file  
powershell -Command "Expand-Archive -Path 'poppler-24.08.0.zip' -DestinationPath '%cd%' -Force"  
IF NOT EXIST "%cd%\poppler-24.08.0" (  
    echo Error: Failed to extract Poppler files.  
    exit /b 1  
)  
  
echo Setting POPPLER_PATH in .env file...  
IF NOT EXIST ".env" (  
    echo. > .env  
)  
echo POPPLER_PATH=%cd%\poppler-24.08.0\Library\bin>> .env  
  
echo Setup complete.  
pause  