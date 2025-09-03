# AnimeScrapyV2

AnimeScrapyV2 is a web crawler system designed to collect anime data from multiple platforms, supporting the aggregation of anime information from different sources for unified storage and management.

<div align="right">
  <a href="./README.md">中文</a> | English
</div>

## Table of Contents

- [Features](#features)
- [Supported Platforms](#supported-platforms)
- [Technical Architecture](#technical-architecture)
- [Tech Stack](#tech-stack)
- [Installation and Deployment](#installation-and-deployment)
  - [Docker Deployment (Recommended)](#docker-deployment-recommended)
  - [Local Execution](#local-execution)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Design](#database-design)
- [Development Guide](#development-guide)

## Features

- Multi-platform anime data crawling
- Unified data storage and management
- Scheduled task scheduling
- Image downloading and saving
- Data aggregation with priority sorting
- Modular design for easy extension
- Docker containerized deployment support

## Supported Platforms

- [Bangumi](https://bangumi.tv/)
- [Anikore](https://www.anikore.jp/)
- [aniDB](https://anidb.net/)
- [MyAnimeList](https://myanimelist.net/)

## Technical Architecture

AnimeScrapyV2 adopts a modular architecture design, primarily consisting of the following modules:

1. **Spider Module** - Responsible for crawling anime data from different platforms
2. **Database Module** - Responsible for data persistence storage
3. **Frame Module** - Provides basic crawler framework functionality
4. **Picture Module** - Handles image downloading and saving
5. **Scheduler Module** - Task scheduling
6. **Summarize Module** - Data aggregation and priority sorting

Modules communicate through bridge patterns, with separated responsibilities for easy maintenance and extension.

## Tech Stack

- Python 3.13
- httpx 0.28.1 (Asynchronous HTTP requests)
- lxml 6.0.1 (HTML/XML parsing)
- pytz 2025.2 (Timezone handling)
- SQLAlchemy 2.0.43 (ORM database operations)
- PyMySQL 1.1.2 (MySQL database connection)
- MariaDB (Data storage)

## Installation and Deployment

Enable the required crawlers in main.py before deployment

### Docker Deployment (Recommended)

1. Clone the project:
   ```bash
   git clone <repository-url>
   cd AnimeScrapyV2
   ```

2. Build the project based on Dockerfile

3. Copy and modify the docker-compose configuration:
   ```bash
   cp docker-compose-example.yml docker-compose.yml
   # Modify configurations in docker-compose.yml
   ```
   Refer to [Usage](#usage) for environment variable settings

4. Build and start services:
   ```bash
   docker-compose up -d
   ```

### Local Execution

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure database environment variables

3. Run the main program:
   ```bash
   python main.py
   ```

## Project Structure

```
AnimeScrapyV2/
├── database/           # Database related files
│   ├── create.sql      # Database initialization script
│   ├── data.py         # Database operation module
│   └── model.py        # Data model definitions
├── frame/              # Crawler framework base module
├── picture/            # Image processing module
├── scheduler/          # Task scheduling module
├── spider/             # Platform-specific crawler implementations
│   ├── AniDB.py
│   ├── Anikore.py
│   ├── Bagumi.py
│   └── MAL.py
├── summarize/          # Data aggregation module
├── constant.py         # Constant configurations
├── main.py             # Program entry point
└── requirements.txt    # Project dependencies
```

## Configuration

The project is configured through environment variables:

- `USERNAME` - Database username
- `PASSWORD` - Database password
- `HOST` - Database host address
- `PORT` - Database port
- `LOG_PATH` - Log file path
- `PICTURE_PATH` - Image save path

On Windows systems, default constant values are used; on POSIX systems (Linux/Mac), configurations are obtained from environment variables.

## Usage

By default, the project executes a crawling task at 2 AM Beijing time daily. You can adjust the execution frequency by modifying the scheduling configuration in [main.py](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/main.py):

```python
@schedule.repeat(Every().hour(2))
def task():
    # Crawling task implementation
```

## Database Design

The database contains the following main table structures:

1. `detail` - Stores detailed anime information
2. `score` - Stores rating information
3. `web` - Stores website information and priorities
4. `cache` - Cache data table

See [database/create.sql](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/database/create.sql) for specific table structures.

## Development Guide

### Adding New Data Sources

1. Create a new crawler module in the [spider/](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/spider/) directory
2. Inherit from the base class provided by the framework to implement data crawling logic
3. Register the new crawler module in [main.py](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/main.py)
4. Modify the Web table in the database to add corresponding website information

### Extending Framework Functionality

The core framework modules are located in the [frame/](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/frame/) directory and can be extended as needed.