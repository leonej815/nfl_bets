from data_collection import Data_Collection
from data_storage import Data_Storage
import csv
import os

def nfl_data(csv_output_directory):
    add_pregame_data()
    update_scores()
    output_csv(csv_output_directory)

def add_pregame_data():
    data_collection = Data_Collection()
    
    # get week and year of current day
    week_year = data_collection.get_week_year()
    week = week_year['week']
    year = week_year['year']

    # get lines for given week
    line_data = data_collection.get_line_data(year, week)
    if len(line_data) == 0:
        return
    
    # store lines in database
    data_storage = Data_Storage()
    data_storage.insert_line_data(year, week, line_data)

    # retrieve stats for given games and update
    stats_needed_list = data_storage.select_stats_needed()
    if len(stats_needed_list) == 0:
        return
    stats = data_collection.get_stats(year, week)
    data_storage.insert_stats(stats_needed_list, stats)

def update_scores():
    data_collection = Data_Collection()
    data_storage = Data_Storage()

    # find weeks that need update
    year_week_list = data_storage.find_yearweeks_to_update()
    if len(year_week_list) == 0: # end if nothing to update
        return
    
    # update missing scores for given weeks
    for year_week in year_week_list:
        year = year_week['year']
        week = year_week['week']        
        game_scores_list = data_collection.retrieve_scores(year, week)
        data_storage.update_scores(year, week, game_scores_list)

def output_csv(output_directory):
    # initialize data storage and retrieve data
    data_storage = Data_Storage()
    headers = data_storage.select_headers()
    table_data = data_storage.select_all_data()
    output_path = f'{output_directory}/nfl_game_data.csv'
    local_csv_path = './csv/nfl_game_data.csv' 

    # Write data to a CSV file in the ./csv directory for local use
    with open(local_csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(table_data)

    # Write data to the user-specified output directory
    if not os.path.samefile(output_path, local_csv_path):
        with open(output_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(headers)
            csv_writer.writerows(table_data)     