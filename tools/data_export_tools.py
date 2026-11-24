import os
from dotenv import load_dotenv
import pandas as pd
from langchain_core.tools import tool
from pathlib import Path
import mssql_python

load_dotenv()


def get_connection():

    connection_string = (
        f"Server={os.getenv('AZURE_SQL_SERVER')};"
        f"Database={os.getenv('AZURE_SQL_DATABASE')};"
        "Authentication=ActiveDirectoryServicePrincipal;"
        f"UID={os.getenv('AZURE_CLIENT_ID')};"
        f"PWD={os.getenv('AZURE_CLIENT_SECRET')};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    return mssql_python.connect(connection_string)


@tool
def export_result(data, file_name, file_format=None):
    """Use this tool to export the results"""
    connection=get_connection()
    file_name = Path(file_name)

    # Determine format from file extension
    if file_format is None:
        file_format = file_name.suffix.lower().replace(".", "")

    # Add extension if not provided
    if not file_name.suffix:
        file_name = file_name.with_suffix(f".{file_format}")

    # If data is a SQL query and connection is provided
    if isinstance(data, str) and connection is not None:
        data = pd.read_sql(data, connection)

    # Convert different types of data into DataFrame
    if isinstance(data, pd.DataFrame):
        df = data

    elif isinstance(data, dict):
        df = pd.DataFrame([data])

    elif isinstance(data, list):
        df = pd.DataFrame(data)

    elif isinstance(data, str):
        df = pd.DataFrame({"Text": [data]})

    else:
        raise TypeError(f"Unsupported data type: {type(data)}")

    # Export to file
    if file_format.lower() == "csv":
        df.to_csv(file_name, index=False)

    elif file_format.lower() in ["xlsx", "excel"]:
        df.to_excel(file_name, index=False)

    else:
        raise ValueError("Supported formats are CSV and Excel")

    return str(file_name.resolve())
