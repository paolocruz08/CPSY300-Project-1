from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os
from datetime import datetime

CONN_STR = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

def process_nutritional_data_from_azurite():
    print(f"Function started at: {datetime.now()}")
    blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)
    container_name = 'datasets'
    blob_name = 'All_Diets.csv'
    print("Connecting to Azurite blob storage...")
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    print(f"Downloading {blob_name} from Azurite...")
    stream = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(stream))
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    numeric_columns = ['Protein(g)', 'Carbs(g)', 'Fat(g)']
    for col in numeric_columns:
        df[col] = df[col].fillna(df[col].mean())
    print("Calculating average macronutrients per diet type...")
    avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()
    print(avg_macros)
    os.makedirs('simulated_nosql', exist_ok=True)
    result = avg_macros.reset_index().to_dict(orient='records')
    with open('simulated_nosql/results.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nResults saved to simulated_nosql/results.json")
    print(f"Function completed at: {datetime.now()}")
    return "Data processed and stored successfully."

print(process_nutritional_data_from_azurite())
