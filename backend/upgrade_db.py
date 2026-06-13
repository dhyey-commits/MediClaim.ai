import sqlite3

conn = sqlite3.connect('mediclaim.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE benchmark_runs ADD COLUMN review_time_sec FLOAT")
    cursor.execute("ALTER TABLE benchmark_runs ADD COLUMN correction_time_sec FLOAT")
    cursor.execute("ALTER TABLE benchmark_runs ADD COLUMN approval_time_sec FLOAT")
    conn.commit()
    print("Database upgraded.")
except Exception as e:
    print(e)
conn.close()
