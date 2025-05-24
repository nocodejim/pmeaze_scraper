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

## Running with Docker Compose

This application can be run using Docker and Docker Compose, which simplifies setup and ensures consistency across environments.

### Prerequisites

*   **Docker:** Ensure Docker is installed on your system. For installation instructions, visit [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/).
*   **Docker Compose:** Docker Compose is typically included with Docker Desktop. If you need to install it separately, refer to [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/).

### Environment Configuration

Before running the application, you need to set up environment configuration files for both the backend and frontend.

1.  **Backend Configuration:**
    *   Create a file named `.env` in the `backend/` directory (e.g., by copying `backend/.env.example` if it exists).
    *   Set the following variables in `backend/.env`:
        *   `DATABASE_URL`: Specifies the connection string for the database (e.g., `sqlite:///./quickbuild_rag.db` for SQLite).
        *   `RAG_JSON_PATH`: Path to the RAG JSON data file within the container (e.g., `/app/scraper/output/all_content.json`).
        *   `CORS_ORIGINS`: Comma-separated list of allowed origins for CORS (e.g., `http://localhost:5173,http://localhost:80`).

2.  **Frontend Configuration:**
    *   Create a file named `.env` in the `frontend/` directory (e.g., by copying `frontend/.env.example` if it exists).
    *   Set the following variable in `frontend/.env`:
        *   `VITE_API_BASE_URL`: The base URL for the backend API (e.g., `http://localhost:8000`).

*(Note: `.env.example` files will be provided in a subsequent step to guide you. For now, ensure these files and variables are planned for.)*

### Development Setup

For a development environment with features like hot-reloading for the backend:

*   **Build and Start Services:**
    ```bash
    docker-compose up --build
    ```
*   **Stop Services:**
    ```bash
    docker-compose down
    ```
*   **Access Points:**
    *   Backend API: `http://localhost:8000` (e.g., health check at `http://localhost:8000/api/v1/system/health`)
    *   Frontend UI: `http://localhost:5173`

### Production Setup

For a production-like environment:

*   **Build and Start Services (detached mode):**
    ```bash
    docker-compose -f docker-compose.prod.yml up --build -d
    ```
*   **Stop Services:**
    ```bash
    docker-compose -f docker-compose.prod.yml down
    ```
*   **Access Points:**
    *   Backend API: `http://localhost:8000` (e.g., health check at `http://localhost:8000/api/v1/system/health`)
    *   Frontend UI: `http://localhost:80`

### Data Persistence

*   **Database:** The SQLite database (`quickbuild_rag.db`) used by the backend is stored in the project root directory on your host machine and mounted into the backend container. This ensures your data persists across container restarts.
*   **RAG Data:** The scraped documentation data located in `scraper/output/` on your host machine is mounted into the backend container at `/app/scraper/output/`, making it accessible to the RAG service.

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