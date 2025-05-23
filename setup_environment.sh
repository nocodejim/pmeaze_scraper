#!/bin/bash

# This script initializes the project environment.

echo "Creating project directories..."
mkdir -p scraper/output

echo "Creating project files..."
touch scraper/__init__.py
touch scraper/scraper.py
touch build_and_deploy.sh
touch .gitignore
touch README.md
touch INSTRUCTIONS.md

echo "Initializing Git repository..."
git init

echo "Populating .gitignore..."
cat <<EOL > .gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/

# Output
scraper/output/
EOL

echo "Populating README.md..."
cat <<EOL > README.md
# Documentation Scraper

This project contains a Python script to scrape the QuickBase documentation from https://wiki.pmease.com/display/QB14.

## To Use

1.  **Setup the environment:**
    \`\`\`bash
    bash setup_environment.sh
    \`\`\`
2.  **Build and run the scraper:**
    \`\`\`bash
    bash build_and_deploy.sh
    \`\`\`
EOL

echo "Project setup complete. You are ready to start developing."