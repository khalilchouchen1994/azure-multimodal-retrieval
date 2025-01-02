#!/bin/bash  
  
# Create a virtual environment  
python3 -m venv .venv  
  
# Activate the virtual environment  
source .venv/bin/activate  
  
# Upgrade pip  
python -m pip install --upgrade pip  
  
# Install required packages  
pip install -r requirements.txt
  
# Extract Poppler files  
echo "Extracting Poppler..."  
7z x poppler-24.08.0.7z -o"$PWD/poppler-24.08.0" -y  
  
# Set POPPLER_PATH in .env file  
echo "Setting POPPLER_PATH in .env file..."  
echo "POPPLER_PATH=$PWD/poppler-24.08.0/Library/bin" > .env  
  
# Deactivate virtual environment  
deactivate  
  
echo "Setup complete."  







