
import sqlite3
import subprocess
from pathlib import Path

N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")

def list_credentials():
    subprocess.run(
        ["docker", "cp", "n8n:/home/node/.n8n/database.sqlite", str(N8N_DB_PATH)],
        capture_output=True
    )
    
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT type, name FROM credentials_entity")
    rows = cursor.fetchall()
    conn.close()
    
    print("Found credentials:")
    for row in rows:
        print(f"Type: {row[0]}, Name: {row[1]}")

if __name__ == "__main__":
    list_credentials()
