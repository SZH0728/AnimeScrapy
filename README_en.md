# AnimeScrapy - Anime Information Scraper Project

<div align="right">
  <a href="./README.md">中文</a> | <a href="./README_en.md">English</a>
</div>

AnimeScrapy is a multi-source anime information collection system based on the Scrapy framework. It can collect anime information from multiple anime database websites, including anime title, ratings, cast, director, tags and other detailed information, and store this information in a database.
### This project is no longer maintained. The refactored version will be released at [AnimeScrapyV2](https://github.com/SZH0728/AnimeScrapyV2)

## Project Structure

```
AnimeScrapy/
├── AnimeScrapy/           # Main Scrapy project directory
│   ├── spiders/           # Spider modules
│   │   ├── Anikore.py     # Anikore website spider
│   │   ├── Bangumi.py     # Bangumi website spider
│   │   ├── MyAnimeList.py # MyAnimeList website spider
│   │   └── aniDB.py       # aniDB website spider
│   ├── items.py           # Data model definitions
│   ├── middlewares.py     # Middlewares
│   ├── pipelines.py       # Data processing pipelines
│   └── settings.py        # Project settings
├── cover/                 # Cover image storage directory
├── dbmanager.py           # Database management module
├── main.py                # Main program entry point
├── scheduler.py           # Task scheduler
├── scrapy.cfg             # Scrapy configuration file
└── README.md              # Project documentation
```

## Features

1. **Multi-source Data Collection**: Supports data collection from the following four major anime database websites:
   - [Bangumi](https://bangumi.tv/)
   - [Anikore](https://www.anikore.jp/)
   - [aniDB](https://anidb.net/)
   - [MyAnimeList](https://myanimelist.net/)

2. **Data Deduplication and Merging**: Identifies the same anime across different websites by name and intelligently merges the data.

3. **Automatic Scheduling**: Uses the schedule library to implement scheduled tasks, automatically collecting the latest data daily.

4. **Data Persistence**: Uses SQLAlchemy ORM to store collected data into MariaDB database.

5. **Image Download**: Automatically downloads anime cover images and saves them locally.

## Data Models

The project defines three main data models:

### DetailItem - Detailed Information
- `name`: Anime name
- `translation`: Translation
- `alias`: Alias list
- `season`: Season information
- `time`: Release time
- `tag`: Tag list
- `director`: Director
- `cast`: Cast list
- `description`: Description
- `web`: Source website
- `webId`: Source website ID
- `picture`: Cover image URL

### ScoreItem - Rating Information
- `name`: Anime name
- `score`: Score
- `vote`: Number of votes
- `source`: Source website
- `date`: Collection date

### PictureItem - Image Information
- `name`: Anime name
- `picture`: Image binary data

## Technical Architecture

### Database Design
Uses MariaDB database to store anime information, mainly including the following tables:
- `cache`: Cache table for temporarily storing unrated anime data
- `detail`: Anime detailed information table
- `nameid`: Anime name and ID mapping table
- `score`: Anime rating table
- `web`: Website information table

### Data Processing Flow
1. Spiders collect raw data from various websites
2. DetailItemPipeline processes detailed information, performing data deduplication and merging
3. ScoreItemPipeline processes rating information, calculating weighted average scores
4. PictureItemPipeline downloads and saves cover images
5. All data is ultimately stored in the database

### Scheduling Mechanism
- Automatically runs spiders to collect latest data at 18:00 every day
- Updates the anime name list file at 04:00 every day

## Configuration Instructions

### Database Configuration
Configure database connection information in the `scrapy.cfg` file:

```ini
[database]
host = localhost
port = 3306
username = your_username
password = your_password
db = your_database
```

### Spider Configuration
The following parameters can be adjusted in [settings.py](file:///D:/poject/AnimeScrapy/AnimeScrapy/settings.py#L1-L101):
- `DOWNLOAD_DELAY`: Download delay (default 10 seconds)
- `CONCURRENT_REQUESTS_PER_DOMAIN`: Concurrent requests per domain (default 1)
- `DEFAULT_REQUEST_HEADERS`: Default request headers

## Usage

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Project
```bash
python main.py
```

### Run a Specific Spider
```bash
scrapy crawl Bangumi
scrapy crawl Anikore
scrapy crawl aniDB
scrapy crawl MyAnimeList
```

## Notes

1. To avoid excessive pressure on target websites, the project has set conservative request frequency limits
2. The project automatically handles data merging of the same anime across different websites
3. The rating system standardizes ratings according to the rating rules of different websites
4. Image files are saved in the [cover/](file:///D:/poject/AnimeScrapy/cover/) directory with anime ID as the filename