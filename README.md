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

## Next Steps

After scraping, you can:
1. **Use the combined files** (`all_content.json` or `all_content.txt`) as input for RAG systems
2. **Build an interactive agent** that can answer questions about QuickBuild
3. **Create embeddings** from the structured content for vector search

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