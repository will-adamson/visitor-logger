import sqlite3

conn = sqlite3.connect('logDB.db')
c = conn.cursor()
c.execute('''DROP TABLE IF EXISTS VISITS''')
conn.commit()
conn.close()