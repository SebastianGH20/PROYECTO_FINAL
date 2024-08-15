import pandas as pd
import os

def load_csv_safely(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return None
    try:
        df = pd.read_csv(file_path, low_memory=False)
        print(f"Successfully loaded {file_path}")
        print(f"Columns in {os.path.basename(file_path)}: {df.columns}")
        print(f"Shape of {os.path.basename(file_path)}: {df.shape}")
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def combine_datasets(input_directory, output_file):
    print(f"Looking for CSV files in: {input_directory}")
    
    if not os.path.exists(input_directory):
        print(f"Error: The specified directory does not exist: {input_directory}")
        return

    csv_files = [f for f in os.listdir(input_directory) if f.endswith('.csv')]
    print(f"CSV files found: {csv_files}")

    dataframes = {}
    for file in csv_files:
        df = load_csv_safely(os.path.join(input_directory, file))
        if df is not None:
            # Reset index to avoid issues with duplicate labels
            df.reset_index(drop=True, inplace=True)
            dataframes[file] = df

    base_df_name = max(dataframes, key=lambda x: dataframes[x].shape[0])
    combined_df = dataframes[base_df_name]
    print(f"Using {base_df_name} as the base DataFrame")

    for name, df in dataframes.items():
        if name != base_df_name:
            print(f"Merging {name}...")
            # Add a suffix to all columns to avoid conflicts
            df = df.add_suffix(f'_{name}')
            # Perform an outer join
            combined_df = pd.concat([combined_df, df], axis=1)

    # Remove any completely empty columns
    combined_df.dropna(axis=1, how='all', inplace=True)

    combined_df.to_csv(output_file, index=False)
    print(f"Combined dataset saved to: {output_file}")
    print(f"Number of rows in the final dataset: {len(combined_df)}")
    print(f"Number of columns in the final dataset: {len(combined_df.columns)}")
    print("Columns in the final dataset:", combined_df.columns)
    
    print("\nFirst 5 rows of the final dataset:")
    print(combined_df.head())
    
    print("\nInformation about the final dataset:")
    print(combined_df.info())

if __name__ == "__main__":
    input_directory = r'E:\fma_metadata'  # Ajusta esta ruta
    output_file = 'combined_fma_dataset.csv'
    combine_datasets(input_directory, output_file)