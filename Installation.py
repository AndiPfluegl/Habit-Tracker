import sqlite3

# creates a new database: "Habit.db":
con = sqlite3.connect("Habit.db")
cur = con.cursor()

# creates two tables in the Habit.db database: Habits and User:
cur.execute("CREATE TABLE Habits(ID PRIMARY KEY, Date TIMESTAMP, User, Name, Period, Status, DateFinishTask TIMESTAMP, CreationDate TIMESTAMP, Streak, Active)")
cur.execute("CREATE TABLE User(User, FirstName, LastName, EMail, Password, CreationDate TIMESTAMP)")

con.close()

