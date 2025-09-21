import pandas as pd
import re
import os

def process_ayurveda(df):
    """
    Processes the raw Ayurveda CSV data.
    - Selects relevant columns
    - Cleans and expands complex diacritical terms
    - Adds the 'system' column
    """
    df = df[['NAMC_CODE', 'NAMC_term_diacritical']].copy()
    df.rename(columns={'NAMC_CODE': 'namaste_code', 'NAMC_term_diacritical': 'namaste_term'}, inplace=True)
    
    new_rows = []
    for _, row in df.iterrows():
        code = row['namaste_code']
        term_string = str(row['namaste_term'])

        # Remove leading markers like (a), (b), etc.
        cleaned_terms = re.sub(r'\([a-z]\)\s*', '', term_string).strip()
        
        # Split term if it contains multiple distinct terms separated by significant whitespace
        individual_terms = re.split(r'\s{2,}', cleaned_terms)
        
        # Add each individual term as a new row
        for term in individual_terms:
            if term: # Ensure term is not empty
                new_rows.append({'namaste_code': code, 'namaste_term': term, 'system': 'ayurveda'})

        # Also add the combined term if there were multiple
        if len(individual_terms) > 1:
            combined_term = ' '.join(individual_terms)
            new_rows.append({'namaste_code': code, 'namaste_term': combined_term, 'system': 'ayurveda'})

    return pd.DataFrame(new_rows)

def process_siddha(df):
    """
    Processes the raw Siddha CSV data.
    """
    df = df[['NAMC_CODE', 'NAMC_TERM']].copy()
    df.rename(columns={'NAMC_CODE': 'namaste_code', 'NAMC_TERM': 'namaste_term'}, inplace=True)
    df['system'] = 'siddha'
    return df

def process_unani(df):
    """
    Processes the raw Unani CSV data.
    """
    df = df[['NUMC_CODE', 'NUMC_TERM']].copy()
    df.rename(columns={'NUMC_CODE': 'namaste_code', 'NUMC_TERM': 'namaste_term'}, inplace=True)
    df['system'] = 'unani'
    return df


def main():
    """
    Main function to run the ETL pipeline for NAMASTE codes.
    """
    # Define paths
    raw_path = 'data/raw'
    processed_path = 'data/processed'
    os.makedirs(processed_path, exist_ok=True)

    # Load raw data
    ayur_df = pd.read_csv(os.path.join(raw_path, 'ayurveda.csv'))
    siddha_df = pd.read_csv(os.path.join(raw_path, 'siddha.csv'))
    unani_df = pd.read_csv(os.path.join(raw_path, 'unani.csv'))

    # Process each dataframe
    print("Processing Ayurveda data...")
    ayur_processed = process_ayurveda(ayur_df)
    
    print("Processing Siddha data...")
    siddha_processed = process_siddha(siddha_df)

    print("Processing Unani data...")
    unani_processed = process_unani(unani_df)

    # Combine all processed dataframes
    print("Combining all NAMASTE data...")
    combined_df = pd.concat([ayur_processed, siddha_processed, unani_processed], ignore_index=True)
    
    # Final cleanup
    combined_df.dropna(subset=['namaste_code', 'namaste_term'], inplace=True)
    combined_df = combined_df[combined_df['namaste_term'].str.strip() != '']

    # Save to a new unified file
    output_file = os.path.join(processed_path, 'unified_namaste_codes.csv')
    combined_df.to_csv(output_file, index=False)
    
    print(f"Successfully created unified NAMASTE data file with {len(combined_df)} records.")
    print(f"File saved to: {output_file}")


if __name__ == "__main__":
    main()