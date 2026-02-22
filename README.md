# NFL Bets Data Pipeline

This project is a Python-based data pipeline designed to automate the collection, storage, and export of NFL game data, betting lines, and team statistics. It scrapes data from sources like ESPN and Pro Football Reference using Selenium, stores it in a SQLite database, and exports the final dataset to CSV.

---

## Features

* **Automated Web Scraping:** Uses Selenium to retrieve current NFL week/year info, betting spreads, totals, and final scores from ESPN.
* **Detailed Team Statistics:** Collects comprehensive offensive and defensive stats (passing, rushing, third-down conversions, time of possession, etc.) from Pro Football Reference for the last 4 games played.
* **Persistent Storage:** Manages a local SQLite database (`nfl_bets.sqlite`) to track historical game data and ensure no duplicate records are created via `UNIQUE` constraints.
* **Dual CSV Export:** Automatically generates a local CSV file and allows for a custom secondary export path (e.g., Google Drive) defined in your settings.

---

## Project Structure

* `nfl_bets.py`: The main entry point that handles configuration loading and initiates the workflow.
* `nfl_data.py`: Orchestrates the high-level logic for collecting pre-game data, updating scores, and exporting CSVs.
* `data_collection.py`: Contains the `Data_Collection` class for all Selenium-based web scraping.
* `data_storage.py`: Contains the `Data_Storage` class for managing SQLite database operations.
* `json/settings.template.json`: A template for your local configuration to keep personal paths out of Version Control.

---

## Installation & Setup

### 1. Prerequisites
* Python 3.x
* Chrome Browser (for Selenium)
* Required Python packages:
    ```bash
    pip install selenium
    ```

### 2. Configuration (Git-Safe)
To keep your personal file paths private while using Git, this project uses a template system:
1.  Navigate to the `json/` directory.
2.  The script will automatically copy `settings.template.json` to `settings.json` on the first run if it doesn't exist.
3.  Open `json/settings.json` and update the `csv_output_directory` to your preferred export path (e.g., your Google Drive folder):
    ```json
    {
      "csv_output_directory": "G:/My Drive/Documents/Spreadsheets/csv"
    }
    ```
    > **Note:** Ensure `json/settings.json` is added to your `.gitignore` to keep your local paths private.

---

## Usage

Simply run the main script to start the pipeline:
```bash
python nfl_bets.py