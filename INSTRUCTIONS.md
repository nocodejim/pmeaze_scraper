# Enhanced Documentation Scraper: Complete Guide

This document provides a comprehensive guide to the enhanced QuickBuild documentation scraper.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Getting Started: Quick Start](#getting-started-quick-start)
3. [Detailed Setup and Execution](#detailed-setup-and-execution)
4. [Output Formats and Structure](#output-formats-and-structure)
5. [Advanced Usage](#advanced-usage)
6. [RAG Integration Guide](#rag-integration-guide)
7. [Developer Guide](#developer-guide)
8. [Troubleshooting](#troubleshooting)

---

## Project Overview

This enhanced scraper extracts the complete QuickBuild documentation from `https://wiki.pmease.com/display/QB14` and creates structured output suitable for RAG (Retrieval-Augmented Generation) systems and AI agents.

### Key Improvements
- **Structured Content Extraction**: Preserves document sections, headers, and metadata
- **Multiple Output Formats**: JSON for AI systems, text for simple processing
- **Combined Files**: Ready-to-use files for RAG systems
- **Progress Tracking**: Real-time progress indication
- **Robust Error Handling**: Comprehensive logging and error recovery

---

## Getting Started: Quick Start

For immediate results:

```bash
# Clone and run
git clone <your-repo-url>
cd <repo-name>
bash build_and_deploy.sh
```

**Result**: Combined documentation files in `scraper/output/all_content.json` and `scraper/output/all_content.txt`

---

## Detailed Setup and Execution

### 1. Environment Preparation

The `build_and_deploy.sh` script handles everything:

```bash
bash build_and_deploy.sh
```

**What it does:**
- Creates Python virtual environment in `venv/`
- Installs dependencies: `requests`, `beautifulsoup4`, `tqdm`, `lxml`
- Runs the scraper with default settings
- Creates output summary and logs

### 2. Manual Setup (Optional)

If you prefer manual control:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Run scraper
python3 scraper/scraper.py
```

---

## Output Formats and Structure

### Directory Structure
```
scraper/output/
├── json/                    # Individual JSON files
│   ├── index.json           # Homepage
│   ├── User_s_Guide.json    # User guide page
│   ├── Configuration.json   # Configuration page
│   └── ...                  # All other pages
├── text/                    # Individual text files
│   ├── index.txt
│   ├── User_s_Guide.txt
│   └── ...
├── all_content.json         # Combined JSON (for RAG)
└── all_content.txt          # Combined text file
```

### JSON Format (Structured)

Each JSON file contains:

```json
{
  "url": "https://wiki.pmease.com/display/QB14/Configuration",
  "title": "Configuration Guide",
  "breadcrumb": ["Home", "QuickBuild", "User Guide", "Configuration"],
  "full_text": "Complete page content as plain text...",
  "sections": [
    {
      "header": "Build Configuration",
      "content": "Content about build configuration..."
    },
    {
      "header": "Step Configuration", 
      "content": "Content about step configuration..."
    }
  ],
  "links": [
    "https://wiki.pmease.com/display/QB14/Build+Steps",
    "https://wiki.pmease.com/display/QB14/Triggers"
  ]
}
```

### Text Format (Simple)

Each text file contains:
```
Title: Configuration Guide
URL: https://wiki.pmease.com/display/QB14/Configuration
Breadcrumb: Home > QuickBuild > User Guide > Configuration

Complete page content as plain text...
```

---

## Advanced Usage

### Command Line Options

```bash
# Test with single page
python3 scraper/scraper.py --single --url https://wiki.pmease.com/display/QB14

# Limit pages (for testing)
python3 scraper/scraper.py --max_pages 5

# Custom output location
python3 scraper/scraper.py --output /path/to/custom/output

# Start from specific URL
python3 scraper/scraper.py --url https://wiki.pmease.com/display/QB14/User+Guide
```

### Customizing the Scraper

Key configuration in `scraper/scraper.py`:

```python
# Change base URL
BASE_URL = "https://wiki.pmease.com/display/QB14"

# Change output directory
OUTPUT_DIR = "scraper/output"

# Modify request delay (be respectful to servers)
time.sleep(1)  # 1 second between requests
```

---

## RAG Integration Guide

### Using the Combined JSON File

The `all_content.json` file is ready for RAG systems:

```python
import json

# Load the scraped documentation
with open('scraper/output/all_content.json', 'r') as f:
    docs = json.load(f)

# Each document has:
for doc in docs:
    print(f"Title: {doc['title']}")
    print(f"URL: {doc['url']}")
    print(f"Sections: {len(doc['sections'])}")
    
    # Use sections for chunking
    for section in doc['sections']:
        print(f"  - {section['header']}: {len(section['content'])} chars")
```

### Recommended RAG Architecture

1. **Document Chunking**: Use the `sections` array for natural chunks
2. **Metadata**: Include `title`, `breadcrumb`, and `url` for context
3. **Embeddings**: Create embeddings for each section's content
4. **Retrieval**: Use semantic search on section content
5. **Context**: Provide breadcrumb and URL for source attribution

### Example with LangChain

```python
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Convert to LangChain documents
documents = []
for page in json_data:
    for section in page['sections']:
        doc = Document(
            page_content=section['content'],
            metadata={
                'title': page['title'],
                'section': section['header'],
                'url': page['url'],
                'breadcrumb': ' > '.join(page['breadcrumb'])
            }
        )
        documents.append(doc)

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)
```

---

## Developer Guide

### Project Architecture

```
├── scraper/
│   ├── __init__.py          # Package marker
│   └── scraper.py           # Main scraper class and logic
├── build_and_deploy.sh      # Build automation
├── requirements.txt         # Dependencies
├── deployment.log           # Runtime logs
└── venv/                    # Virtual environment (created)
```

### Key Classes and Functions

**QuickBuildScraper Class:**
- `__init__()`: Setup directories and session
- `is_valid_url()`: Filter valid documentation URLs
- `extract_content()`: Parse HTML and extract structured content
- `scrape_page()`: Scrape single page with error handling
- `recursive_scrape()`: Crawl entire documentation
- `create_combined_output()`: Generate combined files

**Main Function:**
- Argument parsing
- Error handling with detailed output
- Integration with build system

### Adding New Features

To extend the scraper:

1. **New Content Types**: Modify `extract_content()` method
2. **Different Output Formats**: Add new methods to `QuickBuildScraper`
3. **Enhanced Filtering**: Update `is_valid_url()` method
4. **Progress Tracking**: Extend tqdm usage in `recursive_scrape()`

### Testing Changes

```bash
# Test single page
python3 scraper/scraper.py --single --url https://wiki.pmease.com/display/QB14

# Test limited crawl
python3 scraper/scraper.py --max_pages 3

# Full test
bash build_and_deploy.sh
```

---

## Troubleshooting

### Common Issues

**1. No output files created**
- Check `deployment.log` for errors
- Verify internet connection
- Confirm QuickBuild wiki is accessible

**2. Incomplete scraping**
- Website may have changed structure
- Rate limiting by server
- Network timeouts
- Check logs for specific URLs that failed

**3. Python/dependency errors**
- Ensure Python 3.6+ is installed
- Virtual environment activation failed
- Check `pip3 install -r requirements.txt` output in logs

**4. Permission errors**
- Make build script executable: `chmod +x build_and_deploy.sh`
- Check write permissions in output directory

### Debugging Steps

1. **Check logs first**: `tail -f deployment.log`
2. **Test single page**: `python3 scraper/scraper.py --single`
3. **Verify dependencies**: `pip3 list`
4. **Test network**: `curl https://wiki.pmease.com/display/QB14`

### Performance Tuning

**For faster scraping:**
- Reduce delay: Change `time.sleep(1)` to `time.sleep(0.5)` 
- Increase timeout: Change `timeout=10` to `timeout=30`
- Use `--max_pages` for testing

**For more respectful scraping:**
- Increase delay: Change to `time.sleep(2)`
- Add random delays: `time.sleep(1 + random.random())`

### Log Analysis

Key log entries to watch:
```
ERROR scraping [URL]: [details]  # Failed page
Scraping: [URL]                  # Current page  
Scraped X pages.                 # Final count
SUCCESS: Combined output files   # Completion
```

---

## Next Steps: Building an Interactive Agent

With the scraped documentation, you can now:

### 1. Simple Text Search Agent
```python
# Load combined text
with open('scraper/output/all_content.txt', 'r') as f:
    docs = f.read()

# Simple keyword search
def search_docs(query):
    lines = docs.split('\n')
    results = [line for line in lines if query.lower() in line.lower()]
    return results[:10]  # Top 10 matches
```

### 2. Vector-Based RAG Agent
```python
# Using the JSON structure for better context
import json
from sentence_transformers import SentenceTransformer

# Load structured data
with open('scraper/output/all_content.json', 'r') as f:
    docs = json.load(f)

# Create embeddings for each section
model = SentenceTransformer('all-MiniLM-L6-v2')
sections = []
embeddings = []

for page in docs:
    for section in page['sections']:
        sections.append({
            'content': section['content'],
            'title': page['title'],
            'section_header': section['header'],
            'url': page['url']
        })
        embeddings.append(model.encode(section['content']))
```

### 3. Full RAG Pipeline
- **Retrieval**: Use vector similarity for relevant sections
- **Augmentation**: Combine multiple relevant sections
- **Generation**: Use LLM (OpenAI, local model) to generate answers

### Example Questions the Agent Should Handle
- "How do I add a step to an existing configuration?"
- "What are the different types of build triggers?"
- "How do I set up email notifications for failed builds?"
- "What's the difference between build configurations and build steps?"

---

## Contributing

### Code Style
- Follow existing patterns in `scraper.py`
- Add error handling for new features  
- Update documentation for changes
- Test with `--single` before full runs

### Git Workflow
1. Create feature branch: `git checkout -b feature/enhancement-name`
2. Make changes and test
3. Update documentation
4. Commit with clear messages
5. Create pull request

### Release Process
1. Test full scraping run
2. Verify all output files created
3. Update version documentation
4. Tag release: `git tag v1.1.0`

---

## Security and Best Practices

### Web Scraping Ethics
- Respects robots.txt (check manually)
- 1-second delay between requests
- Handles errors gracefully
- Only scrapes documentation pages

### Data Privacy
- No user data collected
- Only public documentation
- Local storage only
- No external data transmission

### Maintenance
- Monitor QuickBuild site changes
- Update selectors if HTML structure changes
- Keep dependencies updated
- Regular testing with `--single` mode

---

## Version History

### v1.1.0 (Enhanced Version)
- Added structured JSON output
- Implemented section extraction  
- Added combined output files
- Enhanced error handling
- Added progress tracking
- RAG-ready output format

### v1.0.0 (Original Version)
- Basic text scraping
- Simple output structure
- Manual dependency management
