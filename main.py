import sqlite3
import datetime
from datetime import timedelta
from datetime import date
import tkinter as tk
from tkinter import messagebox

currentDate = datetime.date.today()
current_user = ""

# connects to the habit.db:
con = sqlite3.connect("Habit.db")
cur = con.cursor()

class EndOfDay:
    def __init__(self):
        pass

    def do_EoD(self):
        """ has to run end of day before the next day starts (<= 23:59) and the users has finished their inputs for the day.
        The function sets all active habits with Status open on Status failed and set the Streak to 0 and updates it in the database habits.
        It also copies the row in the Habits database for all active habits for tomorrow and set the Status on open. """

        #creates two empty help-lists:
        self.list = []
        self.list2 = []

        # selects all open and active entries in the table Habits in the database and compares the DateFinishtask with the current Date:
        # if the currentdate <= the DateFinishtask the user missed to check of the habit and this row gets the status
        # "failed" in the table Habits in the database and the Streak will be resetted to 0:
        for row in cur.execute("SELECT * FROM Habits WHERE Active = ? AND Status = ?", ("Active", "Open")):
            if row[6] <= str(currentDate):
                id = (row[0],)
                self.list.append(id)
        cur.executemany("UPDATE Habits SET Status = 'Failed', Streak = 0 WHERE ID = ?", self.list)
        con.commit()

        # selects all active and DateToday entries in the table Habits in the database and safes it to the help-list (self.list2):
        for row in cur.execute("SELECT * FROM Habits WHERE Active = ? AND Date = ?", ("Active", currentDate)):
            self.list2.append(row[0])

        # for all entries in the self.list to the method self.copy_row is computed and will create a new row in the database with
        # status open and new Date Finishtask (if necessary):
        for x in self.list2:
            self.copy_row(x)

        print("EoD completed")

    def copy_row(self, key):
        """ copies one row in the Database, the key in the input is the ID, which row is copied. """

        # sets the self.ID variable from the input:
        self.ID = (int(key),)

        # selects the row from the table Habits from the Database, where the input-Key value = the ID-value in the table:
        for row in cur.execute("SELECT * FROM Habits WHERE ID = ?", (self.ID)):
            # creates a help-list and inserts a new row in the table habit in the database, there a few methods are computed:
            # * ID: self.get_ID(): to get a new, unique ID
            # * Date: to set the date on tomorrow, the timedelta function is computed
            # * User, Name, Period is copied
            # * Status: is set to open
            # * DateFinishTask: the method self.set_datefinishtask is computed to return the correct date
            # * CreationDate, Streak, Active is compied
            self.list = [(Habit().get_id(), currentDate + timedelta(days=1), row[2], row[3], row[4], self.set_status(self.ID), Habit().set_datefinishtask(row[4], row[6], "yes"), row[7], row[8], row[9])]
            cur.executemany("INSERT INTO Habits VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", self.list)
            con.commit()
        return

    def set_status(self, ID):
        """checks the field status in the Habits table of the input ID and return the correct status for the EoD run:
        * if the status is Failed then the return status will be Open
        * if the status is Done then it checks the DateFinishTask and if it is lower then DateToday the status stays on Done
        * otherwise the returned status will be Open"""

        self.ID = ID
        for row in cur.execute("SELECT * FROM Habits WHERE ID = ?", (self.ID)):
            if row[5] == "Failed":
                return "Open"
            elif row[5] == "Done" and (row[1] < row[6]):
                return "Done"
            else:
                return "Open"

class Habit:
    def __init__(self):
        # defines the standard parameters for the habits:
        self.status = "Open"
        self.creationdate = currentDate
        self.streak = 0
        self.Id = 0
        self.date = currentDate
        self.datefinishtask = currentDate
        self.streak = 0
        self.active = "Active"
        self.list = []

    def get_Habits(self, user):
        """returns a list of all habits with all fields of the User from the Input"""
        self.user = user
        self.list = []
        for row in cur.execute("SELECT * FROM Habits WHERE User = ?", (self.user, )):
            self.list.append(row)
        return self.list

    def delete_habit(self, name, user):
        """writes the status "Inactive" in the database for the given habit and user"""
        cur.execute("UPDATE Habits SET Active = 'Inactive' WHERE Name = ? AND User = ?", (name, user))
        con.commit()
        return "Habit changed to Inactive"

    def check_off_habit(self, name, user, date):
        """writes the status done and Streak +1 in the database for the given habit name, user and date and returns
        'Habit checked off'. If it fails, the function returns 'Error check_off_habit'"""
        for row in cur.execute("SELECT * FROM Habits WHERE Name = ? AND User = ? AND Date = ?", (name, user, date)):
            streak = row[8] + 1
            cur.execute("UPDATE Habits SET Status = 'Done', Streak = ? WHERE Name = ? AND User = ? and Date = ?", (streak, name, user, date))
            con.commit()
            return "Habit checked off"

        return "error check_off_habit"

    def get_id(self):
        """ returns a new ID value, that is unique """
        # the ID in the table habits must be unique, so always a new ID is necessary, then this function will look
        # at the table habits and return the highest ID + 1

        # selects all entries in the table habits and return the highest ID value:
        for row in cur.execute("SELECT ID FROM Habits"):
            if row[0] >= self.Id:
                self.Id = row[0]
        self.Id += 1
        # return the highest ID value + 1:
        return self.Id

    def create_habit(self, name, period, user):
        """ creates a new entry (row) in the table habits from the input parameters. For period only "Daily", "Weekly"
        or "Monthly" is permitted. The function will return 'Habit created', if it was successful"""
        # takes the entry values from the GUI Habits and converts them into strings and saves them to variables:
        self.name = name
        self.period = period
        self.user = user

        # The user can only give the input "Daily", "Weekly" or "Monthly", otherwise it will return "Wrong Period"
        if self.period != "Daily" and self.period != "Weekly" and self.period != "Monthly":
            return "Wrong Period"

        # creates a help-list with the variables for the habits and store them in the Habit-table in the database:
        # in the list two functions are computed:
        # * self.get_id(): returns a new, unique ID
        # * self.set_datefinishtask: returns the finish task date, given from the input period. fe. Weekly = Date-Today + 7
        self.list = [(self.get_id(), self.date, self.user, self.name, self.period, self.status, self.set_datefinishtask(self.period, self.datefinishtask, "no"), self.creationdate, self.streak, self.active)]
        cur.executemany("INSERT INTO Habits VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", self.list)
        con.commit()
        return "Habit created"


    def set_datefinishtask(self, period, startdate, EoD):
        """ calculates from the input period and startdate the correct Datefinishtask and return the output.
        Period = "Daily", "Weekly" and "Monthly" are permitted. Furthermore if EoD = "yes" than one Day is added
        to the daily tasks. (is necessary for the EoD function) """

        # variabels and parameters are stored, the self.startdate must be converted correctly
        self.period = period
        self.startdate = date.fromisoformat(str(startdate))
        self.EoD = EoD

        # if the set_datefinishtask is computed for the EndOfDay task, the startdate is added 1 day for daily tasks
        if EoD == "yes":
            if self.startdate > currentDate:
                return self.startdate
            elif self.period == "Daily":
                self.startdate = self.startdate + timedelta(days=1)

            elif self.period == "Weekly":
                self.startdate = self.startdate + timedelta(days=7)

            elif self.period == "Monthly":
                self.startdate = self.startdate + timedelta(days=30)
            else:
                print("error set_datefinishtask!")
            return self.startdate
        # if the set_datefinishtask is computed for the new habit tasks, the startdate is added 0 day for daily tasks,
        # 7 days for weekly tasks and 30 days for monthly tasks:
        else:
            if self.period == "Daily":
                self.startdate = self.startdate

            elif self.period == "Weekly":
                self.startdate = self.startdate + timedelta(days=7)

            elif self.period == "Monthly":
                self.startdate = self.startdate + timedelta(days=30)
            else:
                print("error set_datefinishtask!")
            return self.startdate



# here the analysis-functions are defined:
def selected_items(input, index, list):
    """returns all rows of the input-list, where the index-value is the value given in the input"""
    return filter(lambda x: x[index] == input, list)

def highest_value(index, list):
    """returns the highest value of the input-list from the field, which is given from the input index"""
    selected_index = index
    highest = max(map(lambda x: x[selected_index], filter(lambda x: len(x) > selected_index, list)))
    return highest

class Users:
    # User Administration (registration, login, store in Database)

    # Gets the values from the input fields and stores them in variables:
    def __init__(self,  username):
        self.username = username


    def register(self, firstname, lastname, email, password, confirm):
        """ store a new user in the table user in the database and return 'Registration successful' or 'Registration unsuccessful' """
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.confirm_password = confirm



        # selects all current users from the user table in the database and checks if the username already exists. If so
        # an error message occur. If not, the new user is stored in the user table:
        cur.execute("SELECT * FROM User WHERE User = ?", (self.username, ))
        x = cur.fetchall()
        if x == []:
            self.list = [
                ((self.username), (self.firstname), (self.lastname), (self.email), (self.password), currentDate)]
            cur.executemany("INSERT INTO User VALUES(?, ?, ?, ?, ?, ?)", self.list)
            con.commit()
            return "Registration successful"
        else:
            return "Registration unsuccessful"


    def login(self, password):
        """compares the input username and password with the table user in the database and opens returns 'Login successful'
        if the user is found in the table, and 'Login unsuccessful' if not"""
        self.password = password
        # select all user and password with the same user and password from the input fields. If a value is found, then
        # the User with the correct Password exists and the Main_Page GUI will be created. Otherwise an error message
        # occurs:
        cur.execute("SELECT * FROM User WHERE User = ? AND Password = ?", (self.username, self.password))
        x = cur.fetchall()
        if x != []:
            self.set_currentuser(self.username)
            return "Login successful"

        else:
            return "Login unsuccessful"

    def set_currentuser(self, username):
        """takes the given username and sets the global variable current_user"""
        global current_user
        current_user = username


class Analyse_Habit:
    # opens the Analyse Habit GUI:
    def __init__(self, master, current_user):
        self.master = master
        self.user = current_user

        # creates several buttons and computed different commands, if the user clicks on them:
        self.current_habit_button = tk.Button(self.master, text="Current Habits", command=self.current_habits)
        self.current_habit_button.pack()

        self.daily_habit_button = tk.Button(self.master, text="Daily Habits", command=self.daily_habits)
        self.daily_habit_button.pack()

        self.weekly_habit_button = tk.Button(self.master, text="Weekly Habits", command=self.weekly_habits)
        self.weekly_habit_button.pack()

        self.monthly_habit_button = tk.Button(self.master, text="Monthly Habits", command=self.monthly_habits)
        self.monthly_habit_button.pack()

        self.longest_streak_button = tk.Button(self.master, text="Longest Streak", command=self.longest_streak)
        self.longest_streak_button.pack()

        self.habit_entry_label = tk.Label(self.master, text="Input Habit")
        self.habit_entry_label.pack()
        self.habit_entry = tk.Entry(self.master)
        self.habit_entry.pack()

        self.longest_streak_habit_button = tk.Button(self.master, text="Longest Streak Habit", command=lambda: self.longest_streak_habit(self.habit_entry.get()))
        self.longest_streak_habit_button.pack()

        self.detail_analysis_button = tk.Button(self.master, text="Detail Analysis", command=self.detail_analysis)
        self.detail_analysis_button.pack()

    def current_habits(self):
        """ creates a new window with all current habits (active)"""
        self.new_window = tk.Toplevel(self.master)
        self.liste = []
        self.habits = []
        # reads out all habits from the database and save them in a help-list (self.liste):
        for row in cur.execute("SELECT * FROM Habits"):
            self.liste.append(row)

        # computes the selected_items function several times to store the correct entries (Habit task name)
        # from the database in the help-list self.habits:
        for row in list(selected_items(str(currentDate), 1, selected_items("Active", 9, selected_items(self.user, 2, self.liste)))):
            self.habits.append(row[3])

        # creates a label with the entries of the self.habits list, to show the user his/her current habits:
        self.current_habits_label = tk.Label(self.new_window, text="Current Habits: {}".format(self.habits))
        self.current_habits_label.pack()

    def daily_habits(self):
        """ creates a new window with all daily habits"""
        self.new_window = tk.Toplevel(self.master)
        self.liste = []
        self.habits = []
        # reads out all habits from the database and save them in a help-list (self.liste):
        for row in cur.execute("SELECT * FROM Habits"):
            self.liste.append(row)

        # computes the selected_items function several times to store the correct entries (Habit task name)
        # from the database in the help-list self.habits:
        for row in list(selected_items("Daily", 4, selected_items(str(currentDate), 1, selected_items("Active", 9, selected_items(self.user, 2, self.liste))))):
            self.habits.append(row[3])

        # creates a label with the entries of the self.habits list, to show the user his/her daily habits:
        self.daily_habits_label = tk.Label(self.new_window, text="Daily Habits: {}".format(self.habits))
        self.daily_habits_label.pack()

    def weekly_habits(self):
        """ creates a new window with all weekly habits"""
        self.new_window = tk.Toplevel(self.master)
        self.liste = []
        self.habits = []
        # reads out all habits from the database and save them in a help-list (self.liste):
        for row in cur.execute("SELECT * FROM Habits"):
            self.liste.append(row)

        # computes the selected_items function several times to store the correct entries (Habit task name)
        # from the database in the help-list self.habits:
        for row in list(selected_items("Weekly", 4, selected_items(str(currentDate), 1, selected_items("Active", 9, selected_items(self.user, 2, self.liste))))):
            self.habits.append(row[3])

        # creates a label with the entries of the self.habits list, to show the user his/her weekly habits:
        self.weekly_habits_label = tk.Label(self.new_window, text="Weekly Habits: {}".format(self.habits))
        self.weekly_habits_label.pack()

    def monthly_habits(self):
        """ creates a new window with all monthly habits"""
        self.new_window = tk.Toplevel(self.master)
        self.liste = []
        self.habits = []
        # reads out all habits from the database and save them in a help-list (self.liste):
        for row in cur.execute("SELECT * FROM Habits"):
            self.liste.append(row)

        # computes the selected_items function several times to store the correct entries (Habit task name)
        # from the database in the help-list self.habits:
        for row in list(selected_items("Monthly", 4, selected_items(str(currentDate), 1, selected_items("Active", 9, selected_items(self.user, 2, self.liste))))):
            self.habits.append(row[3])

        # creates a label with the entries of the self.habits list, to show the user his/her monthly habits:
        self.monthly_habits_label = tk.Label(self.new_window, text="Monthly Habits: {}".format(self.habits))
        self.monthly_habits_label.pack()

    def longest_streak(self):
        """ creates a new window with the habit(s) with the longest streaks"""
        self.new_window = tk.Toplevel(self.master)
        self.liste = []
        self.habits = []
        self.streak = []
        # reads out all habits from the database and save them in a help-list (self.liste):
        for row in cur.execute("SELECT * FROM Habits"):
            self.liste.append(row)

        # computes the selected_items function store the correct entries
        # from the database in the help-list self.habits:
        for row in list(selected_items(self.user, 2, self.liste)):
            self.habits.append(row)

        # computes the highest_value function to return the highest value from the input list self.habits:
        self.highest_streak = highest_value(8, self.habits)
        for row in self.habits:
            if self.highest_streak == row[8]:
                self.streak.append(row[3])

        # to have only one habit in the self.streak list, we compute the set()-function to remove multiple values:
        self.streak_unique = list(set(self.streak))

        # creates a label with the entries of the self.streak list, to show the user his/her longest streak:
        self.longest_streak_label = tk.Label(self.new_window, text="Longest Streak: {}".format(self.streak_unique) + "Streak: " + str(self.highest_streak))
        self.longest_streak_label.pack()

    def longest_streak_habit(self, name):
        """ creates a new window with the longest streaks from the given habit (input name)"""
        self.new_window = tk.Toplevel(self.master)
        self.liste = []
        self.habits = []
        self.streak = []
        self.name = name

        # reads out all habits from the database and save them in a help-list (self.liste):
        for row in cur.execute("SELECT * FROM Habits WHERE Name = ?", (self.name, )):
            self.liste.append(row)

        # computes the selected_items function store the correct entries
        # from the database in the help-list self.habits:
        for row in list(selected_items(self.user, 2, self.liste)):
            self.habits.append(row)
        # computes the highest_value function to return the highest value from the input list self.habits:
        highest = highest_value(8, self.habits)
        for row in self.liste:
            if highest == row[8]:
                self.streak.append(row[3])

        # to have only one habit in the self.streak list, we compute the set()-function to remove multiple values:
        self.streak_unique = list(set(self.streak))
        # creates a label with the entries of the self.streak list, to show the user his/her longest streak of the given habit::
        self.longest_streak_habit_label = tk.Label(self.new_window, text="Longest Streak: {}".format(self.streak_unique) + "Streak: " + str(highest))
        self.longest_streak_habit_label.pack()


    def detail_analysis(self):
        """opens a new window with a list of all habits from the database"""
        self.new_window = tk.Toplevel(self.master)
        self.liste = []
        self.habits = []
        # reads out all habits from the database and save them in a help-list (self.liste):
        for row in cur.execute("SELECT * FROM Habits"):
            self.liste.append(row)

        # computes the selected_items function store the correct entries
        # from the database in the help-list self.habits:
        for row in list(selected_items(self.user, 2, self.liste)):
            self.habits.append(row)

        # creates a listbox and stores the values from the list self.habits:
        listbox = tk.Listbox(self.new_window, width=100, height=len(self.habits))

        for item in self.habits:
            listbox.insert(tk.END, item)

        listbox.pack()


class GUI:
    # opens the Start_GUI window
    def __init__(self):
        pass

    def Start_GUI(self):
        self.GUI_Start = tk.Tk()
        self.GUI_Start.title("Habit Tracker")
        # creates the Buttons Registration and Log in and if the user clicks on it, the functions open_registration and
        # open_login are computed
        self.button1 = tk.Button(self.GUI_Start, text="Registration", command=self.registration_GUI)
        self.button1.pack()

        self.button2 = tk.Button(self.GUI_Start, text="Log In", command=self.login_GUI)
        self.button2.pack()

        self.GUI_Start.mainloop()


    def registration_GUI(self):
        # opens the Registration GUI:

        self.GUI_Registration = tk.Toplevel()
        self.GUI_Registration.title("Registration")

        # creates the labels and entries for the inputs for the registration:
        self.firstname_label = tk.Label(self.GUI_Registration, text="First Name")
        self.firstname_label.pack()
        self.firstname_entry = tk.Entry(self.GUI_Registration)
        self.firstname_entry.pack()

        self.lastname_label = tk.Label(self.GUI_Registration, text="Last Name")
        self.lastname_label.pack()
        self.lastname_entry = tk.Entry(self.GUI_Registration)
        self.lastname_entry.pack()

        self.email_label = tk.Label(self.GUI_Registration, text="EMail")
        self.email_label.pack()
        self.email_entry = tk.Entry(self.GUI_Registration)
        self.email_entry.pack()

        self.username_label = tk.Label(self.GUI_Registration, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.GUI_Registration)
        self.username_entry.pack()

        self.password_label = tk.Label(self.GUI_Registration, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.GUI_Registration, show="*")
        self.password_entry.pack()

        self.confirm_label = tk.Label(self.GUI_Registration, text="Confirm Password")
        self.confirm_label.pack()
        self.confirm_entry = tk.Entry(self.GUI_Registration, show="*")
        self.confirm_entry.pack()

        # creates the button for registration and computed the method register, if the user clicks on it:

        self.register_button = tk.Button(self.GUI_Registration, text="Register", command=self.registration_button)
        self.register_button.pack()

    def registration_button(self):
        # checks if all input fields are filled out by the user, if not, an error message occurs and
        if self.firstname_entry.get() == "" or self.lastname_entry.get() == "" or self.email_entry.get() == "" or self.username_entry.get() == "" or self.lastname_entry.get() == "" or self.password_entry.get() == "" or self.confirm_entry.get() == "":
            messagebox.showerror("Error", "All fields must be filled!")
            return

        # Check if the passwords match and returns an error message if not
        if self.password_entry.get() != self.confirm_entry.get():
            messagebox.showerror("Error", "Passwords do not match")
            return

        # computes the Users.register function with the entries from the GUI:
        x = Users(self.username_entry.get()).register(self.firstname_entry.get(), self.lastname_entry.get(), self.email_entry.get(), self.password_entry.get(), self.confirm_entry.get())
        if x == "Registration successful":
            messagebox.showinfo("Success", "Registration successful!")
        else:
            messagebox.showerror("Error", "Username already exists - choose another one!")

    def login_GUI(self):
        # opens the Login GUI:

        self.GUI_Login = tk.Toplevel()
        self.GUI_Login.title("Login")

        # creates the labels and entries for the inputs for the Log In:
        self.username_label = tk.Label(self.GUI_Login, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.GUI_Login)
        self.username_entry.pack()

        self.password_label = tk.Label(self.GUI_Login, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.GUI_Login, show="*")
        self.password_entry.pack()

        # creates the button for Login and computed the method log, if the user clicks on it:
        self.login_button = tk.Button(self.GUI_Login, text="Login", command=self.login_button)
        self.login_button.pack()

    def login_button(self):
        """compares the input username and password with the table user in the database and opens the Main-Page GUI"""
        # Gets the values from the input fields and stores them in variables:
        x = Users(self.username_entry.get()).login(self.password_entry.get())
        if x == "Login successful":
            messagebox.showinfo("Success", "Login successful!")
            self.main_page(current_user)

        else:
            messagebox.showerror("Error", "Invalid username or password")



    def main_page(self, current_user):
        # opens the Main Page GUI with the current User (from the Login):
        self.GUI_main_page = tk.Toplevel()
        self.GUI_main_page.title("My Habits")
        # stores the input value in variabels and shows a welcome text with the username of the user:
        self.user = current_user
        self.current_user = tk.StringVar(value="Hallo " + current_user)
        self.GUI_main_page.title("My Habits")
        self.username_label = tk.Label(self.GUI_main_page, textvariable=self.current_user)
        self.username_label.pack()

        # creates different buttons and the methods are computed, if the user clicks on them:
        self.check_off_habit_button = tk.Button(self.GUI_main_page, text="Check off Habits", command=lambda: self.check_off_Habit_GUI(self.user))
        self.check_off_habit_button.pack()

        self.new_habit_button = tk.Button(self.GUI_main_page, text="New Habit", command=lambda: self.create_Habit_GUI(self.user))
        self.new_habit_button.pack()

        self.delete_habit_button = tk.Button(self.GUI_main_page, text="Delete Habit", command=lambda: self.delete_Habit_GUI(self.user))
        self.delete_habit_button.pack()

        self.analyse_habit_button = tk.Button(self.GUI_main_page, text="Analyse Habits", command=self.open_Analyse_Habit)
        self.analyse_habit_button.pack()

        if current_user == "admin":
            self.EoD_button = tk.Button(self.GUI_main_page, text="Do EoD - only for development!", command=lambda: EndOfDay().do_EoD())
            self.EoD_button.pack()


    def open_Analyse_Habit(self):
        """ opens a new window and computes the Analyse_Habit-class"""
        self.GUI_Analyse_habit = tk.Toplevel()
        self.app = Analyse_Habit(self.GUI_Analyse_habit, self.user)

    def delete_Habit_GUI(self, current_user):
        """creates the GUI to check off the habits"""
        self.GUI_Delete_habit = tk.Toplevel()
        self.user = current_user

        # selects the relevant habits (active and currentDate and saves it to a help-list)
        self.list = list(selected_items(str(currentDate), 1, selected_items("Active", 9, Habit().get_Habits(self.user))))
        habits = []
        commands = []

        # saves only the habit names in the habits list to use it later for the button names:
        for row in self.list:
            habits.append(row[3])

        # creates the command lines for the buttons later to check off the habits:
        for habit in habits:
            commands.append(lambda habit=habit: Habit().delete_habit(habit, self.user))

        # creates the buttons on the GUI for all active, open habits for the current user: Clicking on the button
        # computes the check_off_habit method:
        for i in range(len(habits)):
            button_name = habits[i]
            button = tk.Button(self.GUI_Delete_habit, text=button_name, command=commands[i])
            button.pack()

    def check_off_Habit_GUI(self, current_user):
        """creates the GUI to check off the habits:"""
        self.GUI_check_off_habit = tk.Toplevel()
        self.user = current_user

        # reads out all habits from the database and save them in a help-list (self.liste):

        # selects the relevant habits (active, current user and open) and saves it to another help-list x)
        self.liste = list(selected_items(str(currentDate), 1, selected_items("Active", 9, selected_items("Open", 5, Habit().get_Habits(self.user)))))
        habits = []
        commands = []

        # saves only the habit names in the habits list to use it later for the button names:
        for row in self.liste:
            habits.append(row[3])

        # creates the command lines for the buttons later to check off the habits:
        for habit in habits:
            commands.append(lambda habit=habit: (lambda: (Habit().check_off_habit(habit, self.user, currentDate),
                                               messagebox.showinfo("Success", "Well done! Habit task checked off!")))())

        # creates the buttons on the GUI for all active, open habits for the current user: Clicking on the button
        # computes the check_off_habit method:
        for i in range(len(habits)):
            button_name = habits[i]
            button = tk.Button(self.GUI_check_off_habit, text=button_name, command=commands[i])
            button.pack()


    def create_Habit_GUI(self, current_user):
        self.GUI_Create_Habit = tk.Toplevel()
        self.user = current_user
        # define the standard parameters for the habits:

        # creates the label and the entry field at the GUI to let the user save new habits:
        self.habit_label = tk.Label(self.GUI_Create_Habit, text="New Habit")
        self.habit_label.pack()
        self.habit_entry = tk.Entry(self.GUI_Create_Habit)
        self.habit_entry.pack()

        # creates the label and the entry field at the GUI to let the user save the period:
        self.period_label = tk.Label(self.GUI_Create_Habit, text="Period (Daily, Weekly, Monthly)")
        self.period_label.pack()
        self.period_entry = tk.Entry(self.GUI_Create_Habit)
        self.period_entry.pack()

        # creates the New Habit button and clicking on the button computes the create_habit method:
        self.new_habit_button = tk.Button(self.GUI_Create_Habit, text="Create new Habit", command=lambda: self.create_habit_GUI_confirmation(current_user))
        self.new_habit_button.pack()

    def create_habit_GUI_confirmation(self, current_user):
        # creates the messageboxes for the user at the create_habit process
        x = Habit().create_habit(self.habit_entry.get(), self.period_entry.get(), current_user)
        if x == "Wrong Period":
            messagebox.showerror("Error", "Only Daily, Weekly and Monthly tasks are permitted")
        elif x == "Habit created":
            messagebox.showinfo("Success", "New Habit created!")


GUI().Start_GUI()
