import os
import mssql_python
from dotenv import load_dotenv
import pandas as pd
from langchain_core.tools import tool


load_dotenv()

def get_connection():

    connection_string = (
    f"Server=tcp:{os.getenv('AZURE_SQL_SERVER')},1433;"
    f"Database={os.getenv('AZURE_SQL_DATABASE')};"
    f"Authentication=ActiveDirectoryServicePrincipal;"
    f"UID={os.getenv('AZURE_CLIENT_ID')};"
    f"PWD={os.getenv('AZURE_CLIENT_SECRET')};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    )

    
    return mssql_python.connect(connection_string)

    
@tool
def exec_query(query):
    """Execute SQL queries against Azure SQL to retrieve business data.

    Use this tool for business data analysis, filtering, aggregations,
    joins and calculations.

    Do not use this tool to retrieve database schema metadata.
    Use get_schema for schema discovery."""
    conn=None
    for i in range(3):
        try:
            conn = get_connection()
            print("Connected successfully!")
            break
        except Exception as e:
            print(f"Connection failed: {e}")
    
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(cursor.fetchall(), columns=columns)
    conn.close()
    return df.to_string(index=False)

@tool
def get_schema():
    """Retrieve database schema information, including schema name, 
    table name, column name and data types.

    Use this tool whenever database schema information is required.
    Do not retrieve schema information using exec_query."""
    conn=None
    for i in range(3):
        try:
            conn = get_connection()
            print("Connected successfully!")
            break
        except Exception as e:
            print(f"Connection failed: {e}")
    cursor = conn.cursor()
    query="""SELECT
        TABLE_SCHEMA,
        TABLE_NAME,
        COLUMN_NAME,
        DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA='gold'
        ORDER BY TABLE_SCHEMA,TABLE_NAME
        """
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(cursor.fetchall(), columns=columns)
    conn.close()
    return df.to_string(index=False)

