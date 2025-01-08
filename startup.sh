#!/bin/bash  
# Setup Script for Project  
# ------------------------  
  
echo "Creating the virtual environment..."  
python3 -m venv .venv  
  
if [ ! -f ".venv/bin/activate" ]; then  
    echo "Error: Virtual environment creation failed."  
    exit 1  
fi  
  
echo "Activating the virtual environment..."  
source .venv/bin/activate  
  
echo "Upgrading pip and installing required packages..."  
python -m pip install --upgrade pip  
if [ $? -ne 0 ]; then  
    echo "Error: Failed to upgrade pip."  
    exit 1  
fi  
  
pip install -r requirements.txt  
if [ $? -ne 0 ]; then  
    echo "Error: Failed to install required packages."  
    exit 1  
fi  
  
echo "Extracting Poppler..."  
if [ ! -f "poppler-24.08.0.zip" ]; then  
    echo "Error: poppler-24.08.0.zip not found."  
    exit 1  
fi  
  
# Using unzip to extract the ZIP file  
unzip -o "poppler-24.08.0.zip" -d ./  
if [ ! -d "./poppler-24.08.0" ]; then  
    echo "Error: Failed to extract Poppler files."  
    exit 1  
fi  
  
echo "Setting POPPLER_PATH in .env file..."  
if [ ! -f ".env" ]; then  
    touch .env  
fi  
  
# Remove existing POPPLER_PATH entry if it exists  
sed -i '/^POPPLER_PATH=/d' .env  
  
# Append the new POPPLER_PATH  
echo "POPPLER_PATH=$(pwd)/poppler-24.08.0/Library/bin" >> .env  
  
echo "Setup complete."  