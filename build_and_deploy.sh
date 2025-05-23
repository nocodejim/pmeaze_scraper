#!/bin/bash

# This script sets up the environment and runs the scraper.

VENV_DIR="venv"
LOG_FILE="deployment.log"

# --- Logging Setup ---
# This function adds a timestamp to our log messages
log() {
    echo "$(date) - $1" | tee -a $LOG_FILE
}

# Clear previous log file for a clean run
> $LOG_FILE

log "Starting build and deploy process..."

# --- Dependency Check ---
if ! command -v python3 &> /dev/null; then
    log "ERROR: python3 is not installed. Please install it and try again."
    exit 1
fi

# --- Virtual Environment Setup ---
if [ ! -d "$VENV_DIR" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv $VENV_DIR
fi

log "Activating virtual environment..."
source $VENV_DIR/bin/activate

# --- Install Dependencies ---
log "Installing dependencies from requirements.txt..."
# We send the output (stdout and stderr) to the log file for inspection
pip3 install -r requirements.txt >> $LOG_FILE 2>&1

# NEW: Add a check to see what's actually installed in our environment.
log "Checking installed packages in the virtual environment..."
pip3 list >> $LOG_FILE 2>&1

# --- Run the Scraper ---
log "Running the scraper..."
# NEW: Use 'tee' to show Python output on screen AND append to log file
python3 scraper/scraper.py | tee -a $LOG_FILE

# --- Deactivate Virtual Environment ---
log "Deactivating virtual environment."
deactivate

log "Build and deploy process finished."