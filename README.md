# QuickBuild Documentation Scraper

This project contains an enhanced Python script to scrape the QuickBuild documentation from https://wiki.pmease.com/display/QB14. The scraper creates both individual files and combined output suitable for RAG (Retrieval-Augmented Generation) systems.

## Features

- **Complete Documentation Extraction**: Recursively scrapes the entire QuickBuild documentation
- **Multiple Output Formats**: Creates both JSON and text files for each page
- **Combined Output**: Generates `all_content.json` and `all_content.txt` for easy import into AI systems
- **Progress Tracking**: Shows real-time progress with progress bars
- **Structured Content**: Preserves document structure, sections, and metadata
- **Automated Setup**: Handles virtual environment and dependency management

## Quick Start

1. **Setup and run the scraper:**
   ```bash
   bash build_and_deploy.sh
   ```

That's it! The script will:
- Create a virtual environment
- Install all dependencies
- Scrape the documentation
- Create combined output files

## Output Structure

After running, you'll find:

```
scraper/output/
├── json/                    # Individual JSON files for each page
│   ├── index.json
│   ├── User_s_Guide.json
│   └── ...
├── text/                    # Individual text files for each page  
│   ├── index.txt
│   ├── User_s_Guide.txt
│   └── ...
├── all_content.json         # Combined JSON with all pages (for RAG systems)
└── all_content.txt          # Combined text file (for simple text processing)
```

## Advanced Usage

### Command Line Options

```bash
# Test with a single page
python3 scraper/scraper.py --single --url https://wiki.pmease.com/display/QB14

# Limit the number of pages
python3 scraper/scraper.py --max_pages 10

# Custom output directory
python3 scraper/scraper.py --output my_custom_output
```

### Using with RAG Systems

The `all_content.json` file is structured for easy integration with RAG systems:

```json
[
  {
    "url": "https://wiki.pmease.com/display/QB14/User's+Guide",
    "title": "User's Guide",
    "breadcrumb": ["Home", "QuickBuild", "User's Guide"],
    "full_text": "Complete page content...",
    "sections": [
      {
        "header": "Section Title",
        "content": "Section content..."
      }
    ],
    "links": ["..."]
  }
]
```

## Dependencies

The scraper automatically installs:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `tqdm` - Progress bars
- `lxml` - Fast XML/HTML parser

## Next Steps: Interactive RAG Agent

After scraping, you can build an AI agent that answers questions about QuickBuild:

### 1. Setup RAG System
```bash
# Install RAG dependencies
source venv/bin/activate
pip3 install -r rag_system/requirements.txt
```

### 2. Test Performance (Recommended First Step)
```bash
# Test your machine's performance with a single page
python3 rag_system/simple_rag.py

# Run with interactive mode for manual testing
python3 rag_system/simple_rag.py --interactive
```

### 3. Run Full RAG Agent
```bash
# Interactive mode - ask questions continuously
python3 rag_system/rag_agent.py

# Single question mode
python3 rag_system/rag_agent.py --question "How do I add a step to an existing configuration?"
```

### Example Questions the Agent Can Answer:
- "How do I add a step to an existing configuration?"
- "What are the different types of build triggers?"
- "How do I set up email notifications for failed builds?"
- "What's the difference between build configurations and build steps?"

### Performance Notes:
- **First run**: Downloads models (~350MB), takes 20-30 seconds
- **Subsequent runs**: Uses cached models, starts in 2-3 seconds
- **Processing**: Answers questions in ~0.1 seconds on modern hardware

## Troubleshooting

- **Python not found**: Install Python 3.6+ 
- **Permission errors**: Make sure the script is executable: `chmod +x build_and_deploy.sh`
- **Network errors**: Check your internet connection and the QuickBuild wiki availability
- **Empty output**: Check `deployment.log` for detailed error messages

## Logs

Check `deployment.log` for detailed information about each run, including:
- Dependencies installed
- Pages scraped
- Any errors encountered
- Final output summary