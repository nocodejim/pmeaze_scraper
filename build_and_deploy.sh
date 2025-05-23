#!/bin/bash

# This script sets up the environment and runs the scraper.

VENV_DIR="venv"
LOG_FILE="deployment.log"

# --- Logging Setup ---
log() {
    echo "$(date) - $1" | tee -a $LOG_FILE
}

log "Starting build and deploy process..."

# --- Dependency Check: Python and Pip ---
if ! command -v python3 &> /dev/null; then
    log "ERROR: python3 is not installed. Please install it and try again."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    log "ERROR: pip3 is not installed. Please install it and try again."
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
cat <<EOL > requirements.txt
requests
beautifulsoup4
EOL

pip3 install -r requirements.txt >> $LOG_FILE 2>&1

# --- Run the Scraper ---
log "Running the scraper..."
python3 scraper/scraper.py

# --- Deactivate Virtual Environment ---
log "Deactivating virtual environment."
deactivate

log "Build and deploy process finished."