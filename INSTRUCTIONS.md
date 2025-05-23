# Documentation Scraper: Complete Guide

This document provides a comprehensive guide to setting up, running, and maintaining the documentation scraper.

## Table of Contents
1.  [Project Overview](#project-overview)
2.  [Getting Started: Quick Start](#getting-started-quick-start)
3.  [Detailed Setup and Execution](#detailed-setup-and-execution)
4.  [Developer Guide](#developer-guide)
    * [Project Structure](#project-structure)
    * [Code Explanation](#code-explanation)
    * [Versioning and Releases](#versioning-and-releases)
    * [Security Considerations](#security-considerations)

---

### Project Overview

This project provides a Python script to scrape the QuickBase documentation website (`https://wiki.pmease.com/display/QB14`). The goal is to create a local corpus of text files that can be used as a knowledge base for a support agent.

---

### Getting Started: Quick Start

For those who want to get up and running immediately:

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <repo-name>
    ```
2.  **Run the build and deploy script:**
    ```bash
    bash build_and_deploy.sh
    ```
    The scraped `.txt` files will appear in the `scraper/output` directory.

---

### Detailed Setup and Execution

This section is for developers who want to understand the setup process in more detail.

1.  **Initial Environment Setup:**
    The `setup_environment.sh` script prepares your project.
    ```bash
    bash setup_environment.sh
    ```
    This command:
    * Creates the `scraper/` and `scraper/output/` directories.
    * Creates the necessary Python and documentation files.
    * Initializes a Git repository for version control.

2.  **Building and Running the Scraper:**
    The `build_and_deploy.sh` script handles the execution.
    ```bash
    bash build_and_deploy.sh
    ```
    This script performs the following steps:
    * **Checks for Python:** Ensures you have `python3` and `pip3` installed.
    * **Creates a Virtual Environment:** Creates a `venv/` directory to isolate the project's Python dependencies. This is a best practice to avoid conflicts with other Python projects on your system.
    * **Installs Dependencies:** Reads the `requirements.txt` file and installs the `requests` and `beautifulsoup4` libraries.
    * **Runs the Scraper:** Executes `scraper/scraper.py`.
    * **Logs a record** of its actions in `deployment.log`.

---

### Developer Guide

#### Project Structure
.
├── .git/               # Git directory (hidden)
├── .gitignore          # Files and folders for Git to ignore
├── build_and_deploy.sh # Script to setup and run the application
├── INSTRUCTIONS.md     # This file
├── README.md           # A brief project overview
├── deployment.log      # Log file for the build script
├── requirements.txt    # Python dependencies
├── scraper/
│   ├── init.py     # Makes the scraper directory a Python package
│   ├── scraper.py      # The main scraping script
│   └── output/         # Where the scraped text files are saved (ignored by Git)
└── venv/               # Python virtual environment (ignored by Git)


#### Code Explanation (`scraper/scraper.py`)

* **`requests`:** This library is used to send HTTP requests to the website to download the page content.
* **`BeautifulSoup`:** This library is used to parse the HTML content of the pages. It allows us to easily navigate the HTML structure and find the specific data we need.
* **`BASE_URL`:** This is the starting point for our scraper and the boundary. The scraper will not visit pages outside of this URL path.
* **`scrape_page(url)` function:** This is the main recursive function. It takes a URL, scrapes its content, saves it, and then finds all the valid links on that page to scrape next.
* **Content Extraction:** The line `soup.find('div', id='main-content')` is crucial. It targets the specific `div` element on the page that contains the main article content. This is a more robust way to get the data you want instead of just grabbing all text on the page.

#### Versioning and Releases (GitHub Best Practices)

* **Commits:** Make small, logical commits. Your commit messages should be clear and concise, explaining *what* changed and *why*.
* **Branches:** Do not commit directly to the `main` branch. Create a new branch for each new feature or bug fix (e.g., `feature/improve-scraping-logic` or `fix/handle-404-errors`).
* **Pull Requests (PRs):** When your feature is complete, open a Pull Request to merge your branch into `main`. This allows for code review and discussion before changes are integrated.
* **Tags and Releases:** When you reach a stable version, create a tag in Git (e.g., `v1.0`). On GitHub, you can create a "Release" from this tag, which can include release notes and packaged files.

#### Security Considerations

* **Dependabot:** Enable Dependabot on your GitHub repository. It will automatically scan your `requirements.txt` file for known vulnerabilities and create Pull Requests to update your dependencies.
* **Rate Limiting:** For this project, scraping a documentation site is unlikely to cause issues. However, be aware that aggressive scraping can overload a website's server. A more advanced scraper might include delays between requests.
* **robots.txt:** While not implemented in this simple solution, it's good practice to check a website's `robot