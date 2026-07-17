import logging
import azure.functions as func
import json
import os
import io
import pandas as pd
import numpy as np
from datetime import datetime
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Process data function triggered.')
    start_time = datetime.now()

    try:
        # Get connection string from environment variable
        conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        
        if not conn_str:
            return func.HttpResponse(
                json.dumps({"error": "Storage connection string not configured"}),
                status_code=500,
                mimetype="application/json"
            )

        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_client = blob_service_client.get_container_client("datasets")
        blob_client = container_client.get_blob_client("All_Diets.csv")

        # Download and read CSV
        stream = blob_client.download_blob().readall()
        df = pd.read_csv(io.BytesIO(stream))

        # Clean data
        numeric_columns = ["Protein(g)", "Carbs(g)", "Fat(g)"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].mean())

        # Analysis 1: Average macronutrients per diet type
        avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().round(2)
        avg_macros_data = avg_macros.reset_index().to_dict(orient='records')

        # Analysis 2: Recipe count per diet type
        recipe_counts = df["Diet_type"].value_counts().reset_index()
        recipe_counts.columns = ["Diet_type", "Count"]
        recipe_counts_data = recipe_counts.to_dict(orient='records')

        # Analysis 3: Scatter data (protein vs carbs)
        scatter_data = df[["Diet_type", "Protein(g)", "Carbs(g)", "Fat(g)"]].dropna().head(100).to_dict(orient='records')

        # Analysis 4: Top protein recipes
        top_protein = df.nlargest(10, "Protein(g)")[["Recipe_name", "Diet_type", "Protein(g)"]].to_dict(orient='records')

        # Execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        result = {
            "execution_time_seconds": round(execution_time, 3),
            "total_recipes": len(df),
            "diet_types": df["Diet_type"].nunique(),
            "avg_macros": avg_macros_data,
            "recipe_counts": recipe_counts_data,
            "scatter_data": scatter_data,
            "top_protein_recipes": top_protein
        }

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )