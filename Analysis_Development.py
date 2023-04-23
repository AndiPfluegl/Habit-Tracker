import sqlite3

con = sqlite3.connect("Habit.db")
cur = con.cursor()

# all entries from the habits table:
for row in cur.execute("SELECT * FROM Habits"):
    print(row)

# all entries from the habits table:
for row in cur.execute("SELECT * FROM User"):
    print(row)

con.close()