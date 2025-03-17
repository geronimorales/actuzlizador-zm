import pandas as pd

def extract_and_save_brands(input_file, output_file):
    # Read the CSV file into a DataFrame
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: File '{input_file}' is empty.")
        return
    except pd.errors.ParserError:
        print(f"Error: Unable to parse '{input_file}' as a CSV file.")
        return

    # Drop duplicates and empty rows
    df = df.drop_duplicates(subset=['Brand'], keep='first').dropna(subset=['Brand']).sort_values('Brand',axis=0)

    # Save the cleaned data to a new CSV file
    df.to_csv(output_file, index=False)

    print(f"Successfully extracted and saved brands to '{output_file}'.")

# Replace 'input.csv' and 'output.csv' with your file names
extract_and_save_brands('./exporter/marcas.csv', './exporter/marcas2.csv')
