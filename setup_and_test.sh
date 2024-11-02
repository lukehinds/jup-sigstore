#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies and package
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -e .

# Run the test script
echo "Running test script..."
python test_signing.py

# Deactivate virtual environment
deactivate
