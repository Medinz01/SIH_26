import pandas as pd
import re

def format_unani_csv(input_filepath: str, output_filepath: str):
    """
    Reads, cleans, and formats a Unani NAMASTE Code CSV. It handles
    compound codes, term prefixes, and qualifiers in parentheses.

    Args:
        input_filepath (str): The path to the source Unani CSV file.
        output_filepath (str): The path where the formatted CSV will be saved.
    """
    print(f"Reading data from: {input_filepath}")

    try:
        df = pd.read_csv(input_filepath)

        # 1. Select the relevant columns and rename them
        # For Unani, we use NUMC_CODE and NUMC_TERM
        columns_to_keep = ['NUMC_CODE', 'NUMC_TERM']
        df_formatted = df[columns_to_keep].copy()
        df_formatted = df_formatted.rename(columns={
            'NUMC_CODE': 'namaste_code',
            'NUMC_TERM': 'name'
        })
        
        # Ensure columns are string type for cleaning
        df_formatted['namaste_code'] = df_formatted['namaste_code'].astype(str)
        df_formatted['name'] = df_formatted['name'].astype(str)

        # --- ADVANCED CLEANING STEPS (Applying same logic) ---
        print("Cleaning 'namaste_code' and 'name' columns...")

        # 2. Clean 'namaste_code': Keep only the part before the first space
        df_formatted['namaste_code'] = df_formatted['namaste_code'].str.split(' ').str[0]

        # 3. Clean 'name' column in multiple passes:
        # a) Remove secondary terms/synonyms separated by two or more spaces
        df_formatted['name'] = df_formatted['name'].str.split(r'\s\s+').str[0]
        
        # b) Remove leading prefixes like '(a)', '(b)'
        df_formatted['name'] = df_formatted['name'].str.replace(r'^\s*\([a-zA-Z]\)\s*', '', regex=True)

        # c) Remove any other text in parentheses
        df_formatted['name'] = df_formatted['name'].str.replace(r'\s*\([^)]*\)', '', regex=True)

        # d) Strip any remaining leading/trailing whitespace from both columns
        df_formatted['namaste_code'] = df_formatted['namaste_code'].str.strip()
        df_formatted['name'] = df_formatted['name'].str.strip()
        # --- END OF CLEANING ---

        # 4. Save the cleaned DataFrame to the output CSV file
        df_formatted.to_csv(output_filepath, index=False)

        print(f"✅ Successfully formatted and cleaned file, saved to: {output_filepath}")
        print("\n--- Preview of the final, cleaned file ---")
        print(df_formatted.head(20)) 
        print("-------------------------------------------\n")

    except FileNotFoundError:
        print(f"❌ ERROR: Could not find the input file at '{input_filepath}'")
        print(f"Please make sure '{input_csv}' is in the same directory as the script.")
    except KeyError as e:
        print(f"❌ ERROR: A required column was not found in the CSV: {e}")
        print("Please ensure your CSV contains 'NUMC_CODE' and 'NUMC_TERM'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- How to use the script ---
if __name__ == "__main__":
    # Assumes your source file is named 'unani.csv'
    input_csv = "unani.csv"
    output_csv = "unani_formatted.csv"

    format_unani_csv(input_csv, output_csv)
