from nfl_data import nfl_data
import json
import os
import shutil

def main():
    try:
        settings_file = './json/settings.json'
        settings_template_file = './json/settings.template.json'

        # check if using settings.json or settings.template.json
        if not os.path.exists(settings_file):
            if os.path.exists(settings_template_file):
                print("Local settings not found. Creating settings.json from template...")
                shutil.copyfile(settings_template_file, settings_file)
            else:
                print("Error: No settings or template file found.")
                return

        # load the settings from the JSON configuration file
        with open(settings_file) as f:
        # with open('./json/settings.template.json') as f:
            settings = json.loads(f.read())

        # extract the output directory for CSV files
        csv_output_directory = settings.get('csv_output_directory')
        print(csv_output_directory)
        if not csv_output_directory:
            raise KeyError("Missing 'csv_output_directory' in settings.json")

        # execute the NFL data workflow
        print("Starting NFL data processing...")
        nfl_data(csv_output_directory)
        print(f"Data successfully exported to {csv_output_directory}")

    except FileNotFoundError:
        print("Error: 'settings.json' file not found. Please ensure the file exists in the './json/' directory.")
    except json.JSONDecodeError:
        print("Error: 'settings.json' contains invalid JSON. Please check the file for syntax errors.")
    except KeyError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()