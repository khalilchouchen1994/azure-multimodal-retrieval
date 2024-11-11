#!/bin/bash  
  
# Create a virtual environment  
python -m venv .venv  
  
# Activate the virtual environment  
source .venv/bin/activate  
  
# Install required packages  
python -m pip install --upgrade pip
pip install azure-search-documents==11.6.0b4 openai python-dotenv azure-storage-blob azure-identity pymupdf langchain