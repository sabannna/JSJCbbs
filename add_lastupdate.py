import sqlite3
import sys

dbname = 'database.db'

conn = sqlite3.connect(dbname)

c = conn.cursor()

c.execute('''ALTER TABLE threads ADD lastupdate int DEFAULT 0 NOT NULL''');

conn.commit()
conn.close()

