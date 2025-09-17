"""
prepare_data.py: The master script to automate the entire data ETL pipeline.
This script can be stopped and restarted, resuming from the last completed step.
"""
import os
import sys
import json

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Configuration ---
STATUS_FILE = 'data/pipeline_status.json'

# --- State Management Functions ---
def read_status():
    """Reads the status file. Returns an empty dict if not found."""
    if not os.path.exists(STATUS_FILE):
        return {}
    with open(STATUS_FILE, 'r') as f:
        return json.load(f)

def write_status(step_name, is_complete):
    """Updates the status of a given step in the status file."""
    status = read_status()
    status[step_name] = is_complete
    # Ensure the directory exists before writing
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=4)

# --- Import ETL modules ---
try:
    from scripts import ayur_filter, siddha_filter, unani_filter
    from scripts import combine_format
    from scripts import mapper
except ImportError as e:
    print(f"Error: Could not import a script module. Details: {e}")
    sys.exit(1)

def run_pipeline():
    """
    Executes the data preparation pipeline, skipping completed steps.
    """
    print("--- Starting Data Preparation Pipeline ---")
    status = read_status()

    try:
        # Step 1: Filter individual system data
        print("\n[Step 1/3] Filtering NAMASTE data for each system...")
        if status.get('step_1_filter'):
            print("✅ Step 1 already complete. Skipping.")
        else:
            ayur_filter.main()
            siddha_filter.main()
            unani_filter.main()
            write_status('step_1_filter', True)
            print("Filtering complete.")

        # Step 2: Combine and format the filtered data
        print("\n[Step 2/3] Combining and formatting data...")
        if status.get('step_2_combine'):
            print("✅ Step 2 already complete. Skipping.")
        else:
            combine_format.main()
            write_status('step_2_combine', True)
            print("Combining complete.")

        # Step 3: Map NAMASTE codes to ICD-11 codes
        print("\n[Step 3/3] Mapping NAMASTE to ICD-11...")
        # The mapper script has its own internal resume logic,
        # so we don't need to mark it as 'complete' until it finishes.
        mapper.main() # This will run until it's fully done.
        write_status('step_3_mapper', True)
        print("Mapping complete.")

        print("\n--- Data Preparation Pipeline Finished Successfully! ---")
        print(f"The final output file is ready at '{mapper.OUTPUT_FILE}'")

    except KeyboardInterrupt:
        print("\n\n🛑 Ctrl+C detected. Exiting pipeline gracefully. Run again to resume.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred during the pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()