from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os
from datetime import datetime

# Load connection string from environment variable (never hardcode this!)
CONN_STR = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

def process_nutritional_data():
    start_time = datetime.now()
    print(f"Function started at: {start_time}")

    # Connect to real Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)
    container_name = 'datasets'
    blob_name = 'All_Diets.csv'

    print("Connecting to Azure Blob Storage...")
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    print(f"Downloading {blob_name} from Azure Blob Storage...")
    stream = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(stream))
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # Clean data
    numeric_columns = ['Protein(g)', 'Carbs(g)', 'Fat(g)']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].mean())

    # Analysis 1: Average macronutrients per diet type
    print("Calculating average macronutrients per diet type...")
    avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean().round(2)

    # Analysis 2: Recipe count per diet type
    print("Counting recipes per diet type...")
    recipe_counts = df['Diet_type'].value_counts().reset_index()
    recipe_counts.columns = ['Diet_type', 'Count']

    # Analysis 3: Protein vs Carbs scatter data (sample 100 rows)
    print("Preparing scatter plot data...")
    scatter_data = df[['Diet_type', 'Protein(g)', 'Carbs(g)']].dropna().head(100).to_dict(orient='records')

    # Build result
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    result = {
        "execution_time_seconds": execution_time,
        "avg_macros": avg_macros.reset_index().to_dict(orient='records'),
        "recipe_counts": recipe_counts.to_dict(orient='records'),
        "scatter_data": scatter_data
    }

    print(f"Function completed at: {end_time}")
    print(f"Execution time: {execution_time:.2f} seconds")

    return result

if __name__ == "__main__":
    result = process_nutritional_data()
    print(json.dumps(result, indent=2))
