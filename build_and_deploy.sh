#!/bin/bash

# This script sets up the environment and runs the enhanced scraper.

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

# Check what's actually installed in our environment
log "Checking installed packages in the virtual environment..."
pip3 list >> $LOG_FILE 2>&1

# --- Clean Previous Output ---
if [ -d "scraper/output" ]; then
    log "Cleaning previous output directory..."
    rm -rf scraper/output/*
fi

# --- Run the Enhanced Scraper ---
log "Running the enhanced scraper..."
# Use default settings (full scrape) - can be customized with arguments
python3 scraper/scraper.py | tee -a $LOG_FILE

# --- Verify Output ---
if [ -f "scraper/output/all_content.json" ] && [ -f "scraper/output/all_content.txt" ]; then
    log "SUCCESS: Combined output files created successfully."
    log "Output structure:"
    find scraper/output -type f | head -10 | while read file; do
        log "  - $file"
    done
    
    # Count files and show summary
    json_count=$(find scraper/output/json -name "*.json" 2>/dev/null | wc -l)
    text_count=$(find scraper/output/text -name "*.txt" 2>/dev/null | wc -l)
    log "Summary: $json_count JSON files, $text_count text files created."
else
    log "WARNING: Expected output files not found. Check scraper output above."
fi

# --- Deactivate Virtual Environment ---
log "Deactivating virtual environment."
deactivate

log "Build and deploy process finished."
log "Combined files available at:"
log "  - scraper/output/all_content.json"
log "  - scraper/output/all_content.txt"