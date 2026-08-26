import sqlite3

conn = sqlite3.connect("database.db")

try:
    conn.execute(
        "ALTER TABLE orders ADD COLUMN estimated_date TEXT"
    )
except:
    pass

try:
    conn.execute(
        "ALTER TABLE orders ADD COLUMN estimated_time TEXT"
    )
except:
    pass

conn.commit()
conn.close()

print("Database Updated Successfully")