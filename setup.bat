@echo off  
  
REM Create a virtual environment  
python -m venv .venv  
  
REM Activate the virtual environment  
call .venv\Scripts\activate  
  
REM Install required packages  
pip install azure-search-documents==11.6.0b4 openai python-dotenv azure-storage-blob azure-identity pymupdf langchain