from db import get_db_connection

conn = get_db_connection()
print("✅ Connected:", conn.is_connected())
conn.close()
