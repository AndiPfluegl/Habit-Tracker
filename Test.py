import pytest
import sqlite3
import datetime

from main import Users
from main import Habit

currentDate = datetime.date.today()
current_user = ""
con = sqlite3.connect("Habit.db")
cur = con.cursor()

#creates lists to save the data in lists before the test runs, in case of fatal errors to avoid data loss:
cur.execute("SELECT * FROM Habits")
Habitlist = cur.fetchall()
cur.execute("SELECT * FROM User")
Userlist = cur.fetchall()
con.commit()

# here additional testdata can be created: The entries will be inserted in the Habits table:
testdata = [
    #testdata for Check Off Habits:
    (-1, currentDate, 'Testuser', 'Test_Check_off_Habit1', 'Daily', 'Open', currentDate, currentDate, 5, 'Active'),
    (-3, currentDate, 'Testuser', 'Test_Check_off_Habit2', 'Monthly', 'Open', currentDate, currentDate, 0, 'Active'),
    #testdate for Delete Habits:
    (-2, currentDate, 'Testuser', 'Test_Delete_Habit1', 'Daily', 'Done', currentDate, currentDate, 1, 'Active'),
    #new testdata can be inserted here:
]
cur.executemany("INSERT INTO Habits VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", testdata)
con.commit()

class TestUsers:
    def setup_method(self):
        self.test_users = Users("Testuser")

    def test_register(self):
        # tests the register function, and creates a new User named "Testuser"
        self.test_users.register("Max", "Mustermann", "max@gmail.com", "123", "123")
        cur.execute("SELECT * FROM User WHERE User='Testuser'")
        result = cur.fetchone()
        assert result == ("Testuser", "Max", "Mustermann", "max@gmail.com", "123", currentDate.strftime('%Y-%m-%d'))

    def test_login(self):
        # tests the login function with the "Testuser"
        x = self.test_users.login('123')
        assert x == "Login successful"

    # new testcases at the user functions can be inserted here:

class TestHabits:
    def setup_method(self):
        self.test_habits = Habit()

    def test_create_habit(self):
        # a new habit "Test_Create_Habit" is created and tested
        self.test_habits.create_habit("Test_Create_Habit", "Daily", "Testuser")
        result = []
        for row in cur.execute("SELECT * FROM Habits WHERE Name='Test_Create_Habit'"):
            result.append(row[1:])
        assert result == [(currentDate.strftime('%Y-%m-%d'), 'Testuser', 'Test_Create_Habit', 'Daily', 'Open', currentDate.strftime('%Y-%m-%d'), currentDate.strftime('%Y-%m-%d'), 0, 'Active')]


    def test_check_off_habit(self):
        # tests the check off function and the streak, here the testdata "Test_Check_off_Habit1" is used
        self.test_habits.check_off_habit("Test_Check_off_Habit1", "Testuser", currentDate.strftime('%Y-%m-%d'))
        result = []
        for row in cur.execute("SELECT * FROM Habits WHERE Name='Test_Check_off_Habit1'"):
            result.append(row[1:])
        assert result == [(currentDate.strftime('%Y-%m-%d'), 'Testuser', 'Test_Check_off_Habit1', 'Daily', 'Done', currentDate.strftime('%Y-%m-%d'), currentDate.strftime('%Y-%m-%d'), 6, 'Active')]

    def test_check_off_habit2(self):
        # tests the check off function and the streak, here the testdata "Test_Check_off_Habit2" is used
        self.test_habits.check_off_habit("Test_Check_off_Habit2", "Testuser", currentDate.strftime('%Y-%m-%d'))
        result = []
        for row in cur.execute("SELECT * FROM Habits WHERE Name='Test_Check_off_Habit2'"):
            result.append(row[1:])
        assert result == [(currentDate.strftime('%Y-%m-%d'), 'Testuser', 'Test_Check_off_Habit2', 'Monthly', 'Done', currentDate.strftime('%Y-%m-%d'), currentDate.strftime('%Y-%m-%d'), 1, 'Active')]

    # you can create further testcases here:



    def test_delete_habit(self, close_db):
        self.test_habits.delete_habit("Test_Delete_Habit1", "Testuser")
        result = []
        for row in cur.execute("SELECT * FROM Habits WHERE Name='Test_Delete_Habit1'"):
            result.append(row[1:])
        assert result == [(currentDate.strftime('%Y-%m-%d'), 'Testuser', 'Test_Delete_Habit1', 'Daily', 'Done', currentDate.strftime('%Y-%m-%d'), currentDate.strftime('%Y-%m-%d'), 1, 'Inactive')]


    @pytest.fixture
    # to delete the test-entries from the table user and habits these code must execute at the last testcase
    # has to be inserted at the function parameter from the last tests!
    def close_db(self):
        yield
        cur.execute("DELETE FROM Habits")
        cur.execute("DELETE FROM User")
        con.commit()

        cur.executemany("INSERT INTO Habits VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", Habitlist)
        cur.executemany("INSERT INTO User VALUES(?, ?, ?, ?, ?, ?)", Userlist)
        con.commit()
        con.close()


