import psycopg2


DATABASE_URL='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'



conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

#cur.execute("INSERT INTO patients (name, phone) VALUES ('Amina', '255700000000');")
cur.execute("INSERT INTO patients (name, phone) VALUES ('Samwel', '259788700001');")
cur.execute("INSERT INTO patients (name, phone) VALUES ('Nkyakjd', '258788700002');")


conn.commit()

cur.execute("SELECT * FROM patients;")
rows = cur.fetchall()
print(rows)

cur.close()
conn.commit()
conn.close()

