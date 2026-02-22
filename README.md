# NFL Game Data Web Scraper & Analyzer

A Python-based web scraping and data analysis tool that collects NFL game data, including betting lines, team statistics, and final scores. The project uses Selenium for web scraping and SQLite for data storage.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Data Collection](#data-collection)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Output](#output)
- [Notes](#notes)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project automates the collection and organization of NFL game data from multiple sources:
- **ESPN**: Current week/year, betting lines, and final scores
- **Pro Football Reference**: Team statistics and game logs

The collected data is stored in a SQLite database and exported to CSV for analysis and reporting.

## Features

- **Automated Week/Year Detection**: Automatically fetches the current NFL week and year from ESPN
- **Betting Line Collection**: Scrapes spread and total lines from ESPN before games start
- **Team Statistics**: Collects comprehensive offensive and defensive statistics from Pro Football Reference
- **Score Tracking**: Retrieves final scores after games complete
- **Data Persistence**: Stores all data in SQLite with duplicate prevention
- **CSV Export**: Exports complete dataset to CSV format
- **Configurable Output**: User-defined output directory via JSON settings

## Project Structure

```
.
├── main.py                 # Entry point with settings management
├── nfl_data.py            # Main workflow orchestrator
├── data_collection.py     # Web scraping with Selenium
├── data_storage.py        # SQLite database operations
├── json/
│   ├── settings.json      # User settings (auto-created from template)
│   └── settings.template.json  # Settings template
├── sqlite/
│   └── nfl_bets.sqlite    # SQLite database
└── csv/
    └── nfl_game_data.csv  # Exported data
```

## Prerequisites

- Python 3.7+
- Chrome browser (for Selenium WebDriver)
- ChromeDriver (compatible with your Chrome version)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/leonej815/nfl_bets.git
   cd nfl_bets
   ```

2. **Install dependencies**
   ```bash
   pip install selenium
   ```

3. **Download ChromeDriver**
   - Download from [ChromeDriver](https://chromedriver.chromium.org/)
   - Ensure it's in your system PATH or specify the path in code

4. **Create directory structure**
   ```bash
   mkdir -p json sqlite csv
   ```

## Configuration

### Settings File

Create `json/settings.json` based on `settings.template.json`:

```json
{
  "csv_output_directory": "/path/to/output/directory"
}
```

**Required Fields:**
- `csv_output_directory`: Absolute or relative path where CSV files will be exported

The application will automatically create `settings.json` from the template if it doesn't exist.

## Usage

### Basic Execution

```bash
python main.py
```

The script will:
1. Load settings from `settings.json`
2. Collect pre-game data (lines and stats) for the current week
3. Update final scores for games that have completed
4. Export all data to CSV

### Workflow Overview

```
main.py
  └── nfl_data(csv_output_directory)
      ├── add_pregame_data()
      │   ├── Get current week/year
      │   ├── Fetch betting lines
      │   └── Collect team statistics
      ├── update_scores()
      │   └── Retrieve final scores
      └── output_csv()
          └── Export to CSV
```

## Data Collection

### Betting Lines (get_line_data)

Collects pre-game betting information from ESPN NFL scoreboard:
- Away team and home team abbreviations
- Point spread (away_spread, home_spread)
- Total line
- Filters games with insufficient data

**Filtering Criteria:**
- Minimum 4 games played by each team
- Valid spread values (excludes 'OFF')
- Games not yet started

### Team Statistics (get_stats)

Collects last 4 games of team statistics from Pro Football Reference:

**Offensive Stats:**
- Points per game (ppg)
- Pass completions, attempts, yards, TDs, INTs per game
- Sacks taken per game
- Rush attempts, yards, TDs per game
- Field goals made/attempted per game
- Punts per game
- 3rd/4th down conversions
- Time of possession

**Defensive Stats:**
- Opponent versions of all offensive stats above

## Database Schema

### Table: nfl_game_data

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| year | INTEGER | Season year |
| week | INTEGER | Week number |
| away | TEXT | Away team abbreviation |
| home | TEXT | Home team abbreviation |
| away_spread | REAL | Away team spread |
| home_spread | REAL | Home team spread |
| total_line | REAL | Total points line |
| away_score | INTEGER | Away team final score |
| home_score | INTEGER | Home team final score |

**Away Team Statistics** (prefixed with `away_`):
- Game counts: `home_game_count`, `away_game_count`
- Offensive stats: `ppg`, `pass_comp_pg`, `pass_yd_pg`, `pass_td_pg`, `int_thrown_pg`, `sacks_taken_pg`, `rush_att_pg`, `rush_yds_pg`, `rush_td_pg`, `fgm_pg`, `fga_pg`, `pnt_pg`, `3d_conv_pg`, `3d_att_pg`, `4d_conv_pg`, `4d_att_pg`, `top`
- Defensive stats: `opp_ppg`, `opp_pass_comp_pg`, `opp_pass_yd_pg`, `opp_pass_td_pg`, `opp_int_thrown_pg`, `opp_sacks_taken_pg`, `opp_rush_att_pg`, `opp_rush_yds_pg`, `opp_rush_td_pg`, `opp_fgm_pg`, `opp_fga_pg`, `opp_pnt_pg`, `opp_3d_conv_pg`, `opp_3d_att_pg`, `opp_4d_conv_pg`, `opp_4d_att_pg`, `opp_top`

**Home Team Statistics** (prefixed with `home_`):
- Same structure as away team statistics

**Constraints:**
- UNIQUE constraint on (year, week, away, home) to prevent duplicates

## API Reference

### Data_Collection Class

#### get_week_year()
Returns the current NFL week and year from ESPN scoreboard.

**Returns:**
```python
{
  'year': '2024',
  'week': '5'
}
```

#### get_line_data(year, week)
Fetches betting lines for all games in a given week.

**Parameters:**
- `year` (str): Season year
- `week` (str): Week number

**Returns:**
```python
[
  {
    'away': 'buf',
    'home': 'mia',
    'away_spread': '-2.5',
    'home_spread': '2.5',
    'total_line': '45.5'
  },
  ...
]
```

#### get_stats(year)
Collects team statistics for all 32 NFL teams.

**Parameters:**
- `year` (str): Season year

**Returns:**
```python
{
  'bills': {
    'ppg': 25.5,
    'pass_yd_pg': 250.3,
    'rush_yd_pg': 120.2,
    ...
  },
  ...
}
```

#### retrieve_scores(year, week)
Fetches final scores for all completed games in a week.

**Parameters:**
- `year` (str): Season year
- `week` (str): Week number

**Returns:**
```python
[
  {
    'away': 'buf',
    'home': 'mia',
    'away_score': '28',
    'home_score': '23'
  },
  ...
]
```

### Data_Storage Class

#### __init__()
Initializes SQLite connection and creates the game data table if it doesn't exist.

#### insert_line_data(year, week, line_data_list)
Creates game records and inserts betting line information.

#### select_stats_needed()
Returns list of games that need team statistics added.

**Returns:**
```python
[
  {
    'year': 2024,
    'week': 5,
    'away': 'buf',
    'home': 'mia'
  },
  ...
]
```

#### insert_stats(stats_needed_list, stats)
Updates game records with team statistics.

#### find_yearweeks_to_update()
Finds all weeks that need score updates.

**Returns:**
```python
[
  {'year': '2024', 'week': '4'},
  ...
]
```

#### update_scores(year, week, game_scores_list)
Updates game records with final scores.

#### select_all_data()
Retrieves all records from the database.

#### select_headers()
Returns column names for CSV export.

## Output

### CSV Export

The project exports data to `nfl_game_data.csv` containing all collected information:
- Game identifiers (year, week, teams)
- Betting information (spreads, totals)
- Final scores
- Team statistics (offensive and defensive metrics)

The CSV is written to two locations:
1. **Local**: `./csv/nfl_game_data.csv`
2. **Output Directory**: Path specified in `settings.json`

## Notes

- The web scraper uses CSS selectors based on current ESPN and Pro Football Reference HTML structure. Selector updates may be needed if websites change their layouts.
- Selenium runs Chrome in non-headless mode by default (comment line in `web_driver()` to enable headless mode)
- Statistics are collected from the last 4 completed games for each team
- Home/away game counts are included to track team rest advantages
- The database uses REPLACE ON CONFLICT IGNORE to prevent duplicate entries

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Add your license information here]

---

**Author**: Joseph Leone (@leonej815)
**Last Updated**: 2026-02-22