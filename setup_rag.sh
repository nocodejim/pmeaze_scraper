#!/bin/bash

# Setup script for RAG system
# This installs the RAG dependencies and tests the system

VENV_DIR="venv"
LOG_FILE="rag_setup.log"

log() {
    echo "$(date) - $1" | tee -a $LOG_FILE
}

> $LOG_FILE

log "Setting up QuickBuild RAG system..."

# Check if scraper has run
if [ ! -f "scraper/output/all_content.json" ]; then
    log "ERROR: No scraped data found. Run the scraper first:"
    log "  bash build_and_deploy.sh"
    exit 1
fi

# Create rag_system directory
mkdir -p rag_system

# Activate virtual environment (created by scraper)
if [ ! -d "$VENV_DIR" ]; then
    log "ERROR: Virtual environment not found. Run scraper first."
    exit 1
fi

log "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install RAG dependencies
log "Installing RAG system dependencies..."
pip3 install -r rag_system/requirements.txt >> $LOG_FILE 2>&1

# Test the simple RAG system first
log "Testing RAG system with simple tester..."
python3 rag_system/simple_rag.py --json scraper/output/all_content.json | tee -a $LOG_FILE

log "RAG system setup complete!"
log "Try these commands:"
log "  # Interactive mode:"
log "  python3 rag_system/rag_agent.py"
log "  # Single question:"
log "  python3 rag_system/rag_agent.py --question 'How do I configure builds?'"
log "  # Performance test:"
log "  python3 rag_system/simple_rag.py"

deactivate