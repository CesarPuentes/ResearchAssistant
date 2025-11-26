# System Architecture & Component Manual

This document provides a detailed breakdown of the News Aggregation System's structure and components. Use this as a reference to understand how the application is organized.

## 📂 Project Root
The entry point and configuration center of the application.

- **`main.py`**
  The "brain" of the application. It handles command-line arguments (like `instant`, `schedule`, `aggregate`), initializes components, and coordinates data flow.

- **`news-cli`**
  A Bash launcher script. It automatically manages the Python virtual environment and dependencies. **Always use this script to run the application.**

- **`config.yaml` / `.env`**
  Configuration files storing secrets (API keys, email passwords) and operational settings (search depth, intervals).

- **`requirements.txt`**
  Lists all required Python libraries (LangChain, OpenAI, APScheduler, etc.).

---

## 📂 `src/` (Source Code)
The core logic is modularized into specific domains within this directory.

### 1. `src/agents/` (The Researcher)
Responsible for web searching and content extraction.
- **`news_agent.py`**: Contains the `NewsAgent` class. It interprets search prompts and orchestrates the search process.
- **`tools.py`**: Defines capabilities like the **DuckDuckGo Search** tool and **Content Extractor** for reading full articles.

### 2. `src/api/` (The Analyst)
Handles communication with the AI model.
- **`api_client.py`**: A wrapper for the DeepSeek API. It sends raw articles to the AI to:
  - Analyze and summarize findings.
  - Generate "Aggregate Reports" from historical data.

### 3. `src/reporters/` (The Publisher)
Transforms raw data into formatted reports.
- **`report_generator.py`**: Formats articles and analysis into professional HTML (with styling) and plain text.
- **`email_reporter.py`**: Manages SMTP connections (Gmail, Outlook, etc.) to deliver reports to your inbox.

### 4. `src/scheduler/` (The Manager)
Manages timing and long-term data persistence.
- **`scheduler.py`**: Uses `APScheduler` to execute background tasks at set intervals (e.g., "every 6 hours").
- **`data_manager.py`**: Manages the **SQLite database** (`data/news_aggregator.db`). It records every session, article, and report, enabling historical aggregate reporting.

### 5. `src/config/` (The Settings)
- **`config_manager.py`**: A utility that unifies settings from `.env` and `config.yaml`, ensuring the app has necessary credentials at runtime.

---

## 📂 Generated Directories
These folders are created automatically during operation.

- **`data/`**
  Contains the `news_aggregator.db` SQLite database file.

- **`logs/`**
  Contains application log files for debugging and monitoring system activity.
