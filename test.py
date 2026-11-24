import mssql_python
import os
from dotenv import load_dotenv

load_dotenv()

def connection():
    connection_string = (
        f"Server=tcp:{os.getenv('AZURE_SQL_SERVER')},1433;"
        f"Database={os.getenv('AZURE_SQL_DATABASE')};"
        f"Authentication=ActiveDirectoryServicePrincipal;"
        f"UID={os.getenv('AZURE_CLIENT_ID')};"
        f"PWD={os.getenv('AZURE_CLIENT_SECRET')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )

    return mssql_python.connect(connection_string,timeout=90)


for i in range(3):
    print(i)
    # try:
    #     conn=connection()   
    #     print("Connected successfully!")
    #     break
    # except Exception as e:
    #     print(f"Connection failed: {e}")



