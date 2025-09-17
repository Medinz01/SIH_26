"""
prepare_data.py: The master script to automate the entire data ETL pipeline.
This script runs all necessary filtering, combining, fetching, and mapping
operations to produce the final enriched data file for the application.
"""
import os
import sys

# Add the root directory to the Python path to allow for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We are assuming your scripts can be imported.
# If they run code at the global level, you might need to wrap their
# logic in a main() function and call it here.
try:
    from scripts import ayur_filter, siddha_filter, unani_filter
    from scripts import combine_format
    from scripts import fetch, ch_26
    from scripts import mapper
except ImportError as e:
    print(f"Error: Could not import a necessary script module. Make sure all scripts exist. Details: {e}")
    sys.exit(1)

def run_pipeline():
    """
    Executes the entire data preparation pipeline in sequence.
    """
    print("--- Starting Data Preparation Pipeline ---")

    # Step 1: Filter individual system data
    print("\n[Step 1/4] Filtering NAMASTE data for each system...")
    ayur_filter.main()
    siddha_filter.main()
    unani_filter.main()
    print("Filtering complete.")

    # Step 2: Combine and format the filtered data
    print("\n[Step 2/4] Combining and formatting data...")
    combine_format.main()
    print("Combining complete.")

    # Step 3: Fetch and process ICD-11 Chapter 26 data
    print("\n[Step 3/4] Fetching and processing ICD-11 data...")
    # Assuming fetch.py and ch_26.py create necessary intermediate files
    fetch.main() 
    ch_26.main()
    print("ICD-11 data processing complete.")

    # Step 4: Map NAMASTE codes to ICD-11 codes
    print("\n[Step 4/4] Mapping NAMASTE to ICD-11...")
    mapper.main()
    print("Mapping complete.")

    print("\n--- Data Preparation Pipeline Finished Successfully! ---")
    print("The final output file 'data/enriched_namaste_codes_with_icd11.csv' is ready.")

if __name__ == "__main__":
    run_pipeline()