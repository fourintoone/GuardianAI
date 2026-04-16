#!/bin/bash

# Set environment variables for M1 Mac
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export TF_CPP_MIN_LOG_LEVEL=2

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Run with correct Python from .venv
/Users/javid/Desktop/Ujain-Hackathon-Original/.venv/bin/python3 app.py
