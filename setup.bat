@echo off  
  
REM Create a virtual environment  
python -m venv .venv  
  
REM Activate the virtual environment  
call .venv\Scripts\activate  
  
REM Upgrade pip  
python -m pip install --upgrade pip  
  
REM Install required packages  
pip install -r requirements.txt
  
REM Extract Poppler files  
echo Extracting Poppler...  
7z x poppler-24.08.0.7z -o"%cd%\poppler-24.08.0" -y  
  
REM Set POPPLER_PATH in .env file  
echo Setting POPPLER_PATH in .env file...  
echo POPPLER_PATH=%cd%\poppler-24.08.0\Library\bin> .env  
  
REM Deactivate virtual environment  
deactivate  
  
echo Setup complete.  