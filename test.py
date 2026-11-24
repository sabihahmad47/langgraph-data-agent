import mssql_python
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = (
    f"Server=tcp:{os.getenv('AZURE_SQL_SERVER')},1433;"
    f"Database={os.getenv('AZURE_SQL_DATABASE')};"
    f"Authentication=ActiveDirectoryServicePrincipal;"
    f"UID={os.getenv('AZURE_CLIENT_ID')};"
    f"PWD={os.getenv('AZURE_CLIENT_SECRET')};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
)

try:
    conn = mssql_python.connect(connection_string)

    cursor = conn.cursor()
    cursor.execute("SELECT DB_NAME(), GETDATE()")

    print("Connection successful:", cursor.fetchone())

    conn.close()

except Exception as e:
    print("Connection failed:", repr(e))