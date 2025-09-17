import pandas as pd
import os

def combine_and_tag_csvs(file_paths: dict, output_filepath: str):
    """
    Combines multiple formatted CSV files into a single master CSV, adding a
    'system' column to identify the source of each row.

    Args:
        file_paths (dict): A dictionary where keys are the system names (e.g., 'Ayurveda')
                           and values are the file paths to the formatted CSVs.
        output_filepath (str): The path for the final combined CSV file.
    """
    all_dataframes = []
    
    print("Starting the combination process...")

    for system_name, path in file_paths.items():
        if not os.path.exists(path):
            print(f"⚠️ WARNING: File not found at '{path}'. Skipping this file.")
            continue
        
        try:
            # Read the formatted CSV into a DataFrame
            df = pd.read_csv(path)
            
            # Add the 'system' column to tag the data source
            df['system'] = system_name
            
            all_dataframes.append(df)
            print(f"  - Successfully processed: {path}")
            
        except Exception as e:
            print(f"❌ ERROR processing {path}: {e}")

    if not all_dataframes:
        print("❌ ERROR: No dataframes were loaded. Please check your input file paths.")
        return

    # Concatenate all the dataframes in the list into a single one
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Reorder columns to have 'system' first for better readability
    combined_df = combined_df[['system', 'namaste_code', 'name']]

    # Save the final combined dataframe to a new CSV
    combined_df.to_csv(output_filepath, index=False)
    
    print(f"\n✅ All files have been successfully combined!")
    print(f"Master file saved to: {output_filepath}")
    print(f"Total rows in combined file: {len(combined_df)}")
    
    print("\n--- Preview of the combined file ---")
    # Show a few rows from the top and bottom to confirm combination
    print(combined_df.head())
    print("...")
    print(combined_df.tail())
    print("------------------------------------\n")


# --- How to use the script ---
if __name__ == "__main__":
    # Define the input files and the system name for each
    # The script will look for these files in the same directory it is run from.
    files_to_combine = {
        'Ayurveda': 'ayurveda_formatted.csv',
        'Siddha': 'siddha_formatted.csv',
        'Unani': 'unani_formatted.csv'
    }

    # Define the name of the final output file
    output_filename = "combined_namaste_codes.csv"

    combine_and_tag_csvs(files_to_combine, output_filename)
