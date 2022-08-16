from ctypes import windll, c_int64
from tkinter import CENTER
windll.user32.SetProcessDpiAwarenessContext(c_int64(-1))
import datetime
from hashlib import md5
from turtle import width
from pyexpat import model
import warnings
# from time import sleep
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from matplotlib import axis
import mysql.connector
import weakref
import os
import sys
from dotenv import load_dotenv
import random
import bcrypt
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.datatables import MDDataTable
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import MDList
from kivymd.uix.label import MDLabel
import numpy as np
# from numpy import size, spacing
# import openpyxl
import shelve
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
# from pyparsing import one_of
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense
from sklearn.preprocessing import StandardScaler
from pyparsing import one_of
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from kivy.metrics import dp
import threading
from pathlib import Path
from kivymd.uix.list.list import OneLineListItem
import sqlite3
from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '600')
Config.write()
# from sklearn.model_selection import train_test_split

# rcParams['figure.figsize']=20,10

sendmailfile = os.path.join(os.path.split(sys.argv[0])[0][0], 'emailclient').replace('\\', '/')

sys.path.insert(0, sendmailfile)


gardenpath = os.path.join(os.path.split(sys.argv[0])[0][0], 'garden').replace('\\', '/')

sys.path.insert(0, gardenpath)

import garden
from garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import sendmail

load_dotenv()

Window.size = (1000, 600)

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
START = int(os.getenv('START'))
END = int(os.getenv('END'))


class SignInScreen(Screen):
    pass


class SignUpScreen(Screen):
    pass


class UserDashboard(Screen):
    pass


class ForgotPassScreen(Screen):
    pass


class AuthManager(ScreenManager):
    pass


class HomeScreen(Screen):
    pass


class DashboardTabs(TabbedPanel):
    pass


class MainApp(MDApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.filterwarnings('ignore')
        Window.size = (1000, 600)
        # self.elapse = 0
        self.dialog = False
        self.dialog1 = False
        self.loadfiles = False
        self.waitmsg = False
        self.layout = None
        self.graph = None
        self.progress_bar = ProgressBar()
        self.popup = Popup(
            title='Download',
            content=self.progress_bar,
            size_hint=(.8, .8),
            background_color=(0, 0, 0, .5),
        )
        # self.popup.bind(on_open = self.puopen)
        # self.add_widget(Button(text ='Download', on_release = self.pop))

        # self.conn = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        self.conn = sqlite3.connect("qanalytics.db")
        self.cursor = self.conn.cursor()

        create_user = '''CREATE TABLE IF NOT EXISTS `users` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `userid` int(10),
            `username` varchar(255),
            `email` varchar(255),
            `password` varchar(255),
            `reg_status` char(10)
            )'''

        create_data = '''CREATE TABLE IF NOT EXISTS `data_frame` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `file_id` int(11),
            `userid` int(11),
            `filename` varchar(255),
            `filepath` varchar(255),
            `filetype` char(10),
            `created` timestamp
            )'''

        self.cursor.execute(create_user)
        self.cursor.execute(create_data)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"
        self.title = 'QAnalytics'
        self.icon = 'images/logo.png'
        self.kv = Builder.load_file('fe/auth.kv')
        return self.kv

    # def on_start(self):
    #     super().on_start()
    #     get_user = shelve.open('get_user')
    #     email = get_user['user'][3]
    #     print("EMAIL: %s" % email)
    #     print("MAIN APP IDS: ", MainApp.get_running_app().root.get_screen('dashboard').ids)
    #     MainApp.get_running_app().root.get_screen('dashboard').ids.user_name_label.text = email
        

    def signup(self):
        signup_screen = MainApp.get_running_app().root.get_screen('signup')
        self.email = signup_screen.ids.signup_field.text.strip()
        self.password = signup_screen.ids.signuppwd_field.text.strip()
        self.confirm = signup_screen.ids.signup_conf_field.text.strip()
        self.userid = random.randint(START, END)
        isvalid = True
        verror = ""

        if not self.email or "@" not in self.email:
            isvalid = False
            verror += "Invalid email address!\n"

        if not self.password or len(self.password) < 8:
            isvalid = False
            verror += "Invalid password!\n"

        if self.password != self.confirm:
            isvalid = False
            verror += "Password mismatch!\n"
        try:
            if isvalid == True:
                password = self.password.encode('utf-8')
                password = bcrypt.hashpw(password, bcrypt.gensalt())
                password = bytes.decode(password)

                if self.checkuser(self.email):
                    u_exist = "User already exists."
                    self.alert(u_exist)
                else:
                    sql = "INSERT INTO users (userid, email, password, reg_status) VALUES ('%i', '%s', '%s', '%s')" % (self.userid, self.email, password, 'active')
                    if self.cursor.execute(sql):
                        to = self.email
                        subject = 'Account Creation for QAnalytics'
                        emailMsg = '''<div style="background: #eee;padding: 10px;">
                            <div style="max-width: 500px;margin: 0px auto;font-family: sans-serif;text-align: center;background: #fff;border-radius: 5px;overflow: hidden;">
                                <div style="width: 100%;background: #fc9700;">
                                    <h1 style="color: #fff;text-decoration: none;margin: 0px;padding: 10px 0px;">QAnalytics</h1>
                                </div>
                                <div style="color: #000;padding: 10px;margin-top: 10px;">
                                    Hello, <br/>Thank you for registering with us at QAnalytics. Please login to your dashbaord with your email and password
                                    <div style="padding: 10px;margin: 10px 0px;color: #000;background: #eee;border-radius: 5px;">
                                    Account Confirmation:
                                        <div style="font-size: 35px; color: #000;font-weight: 700;">
                                            Confirmed
                                        </div>
                                    </div>
                                </div>
                                <div style="color: #000; padding-bottom: 10px;">
                                    However, if this registration process was not initiated by you, kindly ignore this mail.
                                    <br />
                                    If you have encounter any problem while creating your account, feel free to <a href="' . $webhost . '/contact" style="text-decoration: none; color: #bf5794;">contact us</a>
                                </div>
                            </div>
                        </div>'''
                        alt = '''Hello user, Thank you for registering with us at QAnalytics Predictive Model. Please login to your dashboard with your email and dashboard. <br />  However, if this registration process was not initiated by you, kindly ignore this mail.'''
                        sendmail.SendMail(to, subject, emailMsg, alt)
                    signupok = "SignUp Successful"
                    self.alert(signupok)
            else:
                self.errormsg(verror)
        finally:
            self.conn.commit()

    def signin_thread(self):
        self.waitmsg = MDLabel(text="Please wait while we load your dashboard...", font_size = "20sp", pos_hint={"x": .31, "y": .4})
        MainApp.get_running_app().root.get_screen('signin').ids['waitlabel'] = weakref.ref(self.waitmsg)
        signinscr = MainApp.get_running_app().root.get_screen('signin').ids.outer_box
        signinscr.add_widget(self.waitmsg)
        Clock.schedule_once(lambda x: self.signin(), 0)            
        

    def signin(self):
        signin_screen = MainApp.get_running_app().root.get_screen('signin')
        self.email = signin_screen.ids.signin_field.text.strip()
        self.password = signin_screen.ids.pwd_field.text.strip()
        # print("MAIN APP IDS: ", MainApp.get_running_app().root.get_screen('dashboard').ids)
        # print("USER NAME: ", MainApp.get_running_app().root.get_screen('dashboard').ids.user_name_label)        

        self.password = self.password.encode('utf-8')

        sql = f"SELECT * FROM users WHERE email = '{self.email}'"
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        try:
            if res:
                hash_pwd = res[0][4]
                hash_pwd_encoded = str.encode(hash_pwd)
                if bcrypt.checkpw(self.password, hash_pwd_encoded):
                    get_user = shelve.open('get_user', flag='n')
                    get_user['user'] = res[0]
                    msg = "Signin Successful"
                    self.alert(msg)
                else:
                    msg = "Wrong email or password!"
                    self.errormsg(msg)
            else:
                msg = "User does not exist!"
                self.errormsg(msg)
        finally:
            self.conn.commit()
            get_user = shelve.open('get_user')
            email = get_user['user'][3]
            MainApp.get_running_app().root.get_screen('dashboard').ids.user_name_label.text = email
            self.recent_plot = MainApp.get_running_app().root.get_screen('dashboard').ids.dashboard_home_screen
            plt.cla()
            self.recent_plot.clear_widgets()
            self.doanalysis()
            self.recent_plot.add_widget(FigureCanvasKivyAgg(plt.gcf()))
            

    def checkuser(self, email):
        sql = f"SELECT * FROM users WHERE email = '{email}'"
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if not res:
            return False
        else:
            return True

    def logout(self):
        self.dialog = False
        if not self.dialog:
            self.dialog = MDDialog(
                title="Logout Dialog Box",
                text="Do you want to log out now?",
                buttons=[
                    MDFlatButton(text="CANCEL", text_color=self.theme_cls.primary_color, on_release=self.cancel),
                    MDRectangleFlatButton(text="YES", text_color=self.theme_cls.primary_color, on_release=self.logoutuser),
                ],
            )
        self.dialog.open()

    def cancel(self, obj):
        self.dialog.dismiss()

    def cancelerror(self, obj):
        if MainApp.get_running_app().root.get_screen('signin'):
            signin_screen = MainApp.get_running_app().root.get_screen('signin')
            signin_screen.ids.signin_field.text = ''
            signin_screen.ids.pwd_field.text = ''
            self.dialog1.dismiss()
        if MainApp.get_running_app().root.get_screen('signup'):
            signup_screen = MainApp.get_running_app().root.get_screen('signup')
            signup_screen.ids.signup_field.text = ''
            signup_screen.ids.signuppwd_field.text = ''
            self.dialog1.dismiss()

    def logoutuser(self, obj):
        shelve.open("get_user", flag="n")
        dashbaord_screen = MainApp.get_running_app().root.get_screen('dashboard')
        dashbaord_screen.manager.current = "home"
        self.dialog.dismiss()

    def closealert(self, obj):
        if MainApp.get_running_app().root.get_screen('signup'):
            signup_screen = MainApp.get_running_app().root.get_screen('signup')
            signup_screen.ids.signup_field.text = ''
            signup_screen.ids.signuppwd_field.text = ''
            signup_screen.ids.signup_conf_field.text = ''
            if self.dialog1.dismiss():
                self.dialog1 = False
        if MainApp.get_running_app().root.get_screen('signin'):
            signin_screen = MainApp.get_running_app().root.get_screen('signin')
            signin_screen.ids.waitlabel.text = ''
            signin_screen.ids.signin_field.text = ''
            signin_screen.ids.pwd_field.text = ''
            if self.dialog1.dismiss():
                self.dialog1 = False
            signin_screen.manager.current = "dashboard"

        self.dialog1.dismiss()

    def alert(self, message):
        self.dialog1 = False
        if not self.dialog1:
            self.dialog1 = MDDialog(
                title="Confirm",
                text=message,
                buttons=[
                    MDRectangleFlatButton(text="OK", text_color=self.theme_cls.primary_color, on_release=self.closealert),
                ],
            )
        self.dialog1.open()

    def errormsg(self, message):
        self.dialog1 = False
        print(message)
        if not self.dialog1:
            self.dialog1 = MDDialog(
                title="Error",
                text=message,
                buttons=[
                    MDRectangleFlatButton(text="OK", text_color=self.theme_cls.primary_color, on_release=self.cancelerror),
                ],
            )
        self.dialog1.open()

    def back(self):
        if MainApp.get_running_app().root.get_screen('signup'):
            signup_screen = MainApp.get_running_app().root.get_screen('signup')
            signup_screen.manager.current = "home"
            signup_screen.manager.transition.direction = "right"
        elif MainApp.get_running_app().root.get_screen('signin'):
            signin_screen = MainApp.get_running_app().root.get_screen('signin')
            signin_screen.manager.current = "home"
            signin_screen.manager.transition.direction = "right"

    def selected(self, filename):
        print(filename[0])
        filename = filename[0]
        return filename

    def closetable(self, obj):
        if self.layout != None:
            self.df_screen.remove_widget(self.layout)
            self.layout = None

    def showdataframe_thread(self, filename):
        dashbd = MainApp.get_running_app().root.get_screen('dashboard')
        if dashbd.ids.filechooser_lyt:
            dashbd.ids.filechooser_lyt.clear_widgets()
        self.filechoosermsg = MDLabel(text="Please wait while loading the file...", font_size="12sp", pos_hint={"x":.3, "y":.4})
        dashbd.ids['filechooser_msg'] = weakref.ref(self.filechoosermsg)
        dashbd.ids.filechooser_lyt.add_widget(self.filechoosermsg)
        Clock.schedule_once(lambda x: self.showdataframe(filename), 0)            


    def showdataframe(self, filename):
        if 'table_button_layout' in MainApp.get_running_app().root.get_screen('dashboard').ids:
            MainApp.get_running_app().root.get_screen('dashboard').ids.table_button_layout.text = ''
        if self.layout == None and Path(filename[0]).is_file():
            filename = filename[0].replace('\\', '/')
            # Read and store content of an excel file
            cur_date = datetime.datetime.now()
            cur_date_y = cur_date.strftime("%Y-%m-%d")
            cur_date_h = cur_date.strftime("%H-%M-%S")
            cur_date_ft = f'{cur_date_y}-{cur_date_h}'
            csv_path = fr'{os.path.dirname(os.path.dirname(__file__))}/excelfiles/csvfile-{cur_date_ft}.csv'.replace('\\', '/')
            print("CSV FILE PATH", csv_path)
            try:
                read_file = pd.read_excel(fr'{filename}', engine='openpyxl')
                # Write the dataframe object into csv file
                read_file.to_csv(fr'{csv_path}', index=None, header=True)

                # read csv file and convert into a dataframe object
                df = pd.DataFrame(pd.read_csv(fr'{csv_path}', header=1))
                # get column header names
                new_headers = ['Stnno', 'Year', 'Month', 'Day', 'Hour (MST)', 'Pressure MSL (Hpa)', 'Dry Bulb Temp. (⁰ C)', 'Dew Point (⁰ C)', 'Relative Humidity (%)', 'Mean Surface Direction (⁰)', 'Wind Speed (m/s)', 'Rainfall Duration (m/s)', 'Rainfall Amount (mm)', 'Amount ( mm )', 'Rain Intensity (mm/hr)']

                # show the dataframe
                df.columns = new_headers
                col = list(df.columns)
                row = df.to_records(index=False)
                print("Rows in dataframe: ", row)
                self.df_screen = MainApp.get_running_app().root.get_screen('dashboard').ids.screen_manager.get_screen('upload_from_csv')

                col = [(x, dp(60)) for x in col]
                self.layout = BoxLayout(orientation='vertical')
                innerbox = BoxLayout(orientation='horizontal', spacing='5', padding=(5, 5, 5, 5), size_hint=(1, .1))
                MainApp.get_running_app().root.get_screen('dashboard').ids['table_button_layout'] = weakref.ref(innerbox)

                closebtn = MDFlatButton(
                    text='        Close        ',
                    pos_hint={"center_x": .5},
                    halign="left",
                    valign="bottom",
                    size_hint=(None, None),
                    size=(100, 40),
                    md_bg_color=(36 / 255, 40 / 255, 43 / 255, 1),
                    on_release=self.closetable,
                )
                table = MDDataTable(
                    pos_hint={"center_x": .5, "center_y": .5},
                    size_hint=(1, .9),
                    # height = '490dp',
                    column_data=col,
                    row_data=row,
                    use_pagination=True,
                    rows_num=10,
                    pagination_menu_height='240dp',
                )

                button = MDFlatButton(
                    text='        Perform Analysis        ',
                    pos_hint={"center_x": .5},
                    size_hint=(None, None),
                    size=(200, 40),
                    md_bg_color=(36 / 255, 40 / 255, 43 / 255, 1),
                    on_release=self.analyze_thread,
                )
                self.layout.add_widget(table)
                innerbox.add_widget(closebtn)
                innerbox.add_widget(button)
                self.layout.add_widget(innerbox)
                self.df_screen.add_widget(self.layout)

                self.file_id = random.randint(START, END)
                self.filename = 'csvfile-' + cur_date_ft + '.csv'
                self.filepath = fr'{csv_path}'
                self.created = datetime.datetime.now()
                get_user = shelve.open('get_user')
                user = get_user['user']
                self.userid = user[1]
                # save the csv file path
                sql = "INSERT INTO data_frame (file_id, userid, filename, filepath, filetype, created) VALUES ('%i', '%i', '%s', '%s', '%s', '%s')" % (self.file_id, self.userid, self.filename, self.filepath, 'csv', self.created)

                self.cursor.execute(sql)
                self.conn.commit()
            except Exception as e:
                csverr = f"Please upload a valid csv file. {e}"
                print(csverr)
                self.alert(csverr)

    def doanalysis(self):
        # get user
        get_user = shelve.open('get_user')
        user = get_user['user']
        userid = user[1]
        # get the currently uploaded csv file
        sql = f"SELECT filepath FROM data_frame WHERE userid = '{userid}' ORDER BY created DESC LIMIT 1"
        self.cursor.execute(sql)
        csv_path = self.cursor.fetchall()[0][0]
        print("CSV FILE PATH IN ANALYSE", csv_path)
        # check if result exist then create dataframe
        if csv_path and Path(csv_path).is_file():
            # read csv file and convert into a dataframe object
            df = pd.read_csv(fr'{csv_path}', header=1)
            print(df.head())  # 7 columns, including the Date.
            new_headers = ['Stnno', 'Year', 'Month', 'Day', 'Hour (MST)', 'Pressure MSL (Hpa)', 'Dry Bulb Temp. (⁰ C)', 'Dew Point (⁰ C)', 'Relative Humidity (%)', 'Mean Surface Direction (⁰)', 'Wind Speed (m/s)', 'Rainfall Duration (m/s)', 'Rainfall Amount (mm)', 'Amount ( mm )', 'Rain Intensity (mm/hr)']

            # show the dataframe
            df.columns = new_headers
            # Separate dates for future plotting
            date_rows = ['Year', 'Month', 'Day']
            # train_dates = pd.to_datetime(df['Year'], format="%Y-%m-%d")
            df["Date"] = df[date_rows].apply(lambda x: "-".join(x.values.astype(str)), axis="columns")
            df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
            df = df[['Date', 'Pressure MSL (Hpa)', 'Dry Bulb Temp. (⁰ C)', 'Dew Point (⁰ C)', 'Relative Humidity (%)', 'Mean Surface Direction (⁰)', 'Wind Speed (m/s)', 'Rainfall Duration (m/s)', 'Rainfall Amount (mm)']]          

            original = df[['Date', 'Rainfall Amount (mm)']]
            # original['Date'] = pd.to_datetime(original['Date'], format="%Y-%m-%d")
            original = original.loc[original['Date'] >= '2014-05-01']
            plt.title('Recent Analysis', fontdict={'fontsize': 20}, loc='center')
            plt.ylabel('Rainfall Amount (mm)')
            plt.xlabel('Year(yr)')
            plt.plot(original['Date'], original['Rainfall Amount (mm)'])
            # plt.plot(df_forecast['Date'], df_forecast['Rainfall Amount (mm)'])
            

    def analyze_thread(self, obj):
        dashbrd = MainApp.get_running_app().root.get_screen('dashboard')
        if dashbrd.ids.table_button_layout:
            dashbrd.ids.table_button_layout.clear_widgets()
        self.dataframemsg = MDLabel(text="                                        Analysing... Please wait", font_size="12sp")
        dashbrd.ids.table_button_layout.add_widget(self.dataframemsg)
        Clock.schedule_once(lambda x: self.analyze(obj), 0)

    def analyze(self, obj):
        # get user
        Window.size = (1000, 600)
        get_user = shelve.open('get_user')
        user = get_user['user']
        userid = user[1]
        # get the currently uploaded csv file
        sql = f"SELECT filepath FROM data_frame WHERE userid = '{userid}' ORDER BY created DESC LIMIT 1"
        self.cursor.execute(sql)
        csv_path = self.cursor.fetchall()[0][0]
        print("CSV FILE PATH IN ANALYSE", csv_path)
        # check if result exist then create dataframe
        if csv_path and Path(csv_path).is_file():
            # read csv file and convert into a dataframe object
            df = pd.read_csv(fr'{csv_path}', header=1)
            print(df.head())  # 7 columns, including the Date.
            new_headers = ['Stnno', 'Year', 'Month', 'Day', 'Hour (MST)', 'Pressure MSL (Hpa)', 'Dry Bulb Temp. (⁰ C)', 'Dew Point (⁰ C)', 'Relative Humidity (%)', 'Mean Surface Direction (⁰)', 'Wind Speed (m/s)', 'Rainfall Duration (m/s)', 'Rainfall Amount (mm)', 'Amount ( mm )', 'Rain Intensity (mm/hr)']

            # show the dataframe
            df.columns = new_headers
            #Separate dates for future plotting
            date_rows = ['Year', 'Month', 'Day']
            # train_dates = pd.to_datetime(df['Year'], format="%Y-%m-%d")
            df["Date"] = df[date_rows].apply(lambda x:"-".join(x.values.astype(str)), axis="columns")
            df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
            df = df[['Date', 'Dry Bulb Temp. (⁰ C)', 'Dew Point (⁰ C)', 'Relative Humidity (%)', 'Mean Surface Direction (⁰)', 'Wind Speed (m/s)', 'Rainfall Amount (mm)']]
            train_dates = df["Date"]
            print(train_dates.head())
            print(train_dates.tail(15)) #Check last few dates. 
            print("NEW DATAFRAME HEADERS: ", df.head())


            #Variables for training
            cols = list(df)[1:6]
            #Date and volume columns are not used in training. 
            print(cols) #['Duration', 'High', 'Low', 'Close', 'Adj Close']

            #New dataframe with only training data - 5 columns
            df_for_training = df[cols].astype(float)

            # df_for_plot=df_for_training.tail(5000)
            # df_for_plot.plot.line()

            #LSTM uses sigmoid and tanh that are sensitive to magnitude so values need to be normalized
            # normalize the dataset
            scaler = StandardScaler()
            scaler = scaler.fit(df_for_training)
            df_for_training_scaled = scaler.transform(df_for_training)


            #As required for LSTM networks, we require to reshape an input data into n_samples x timesteps x n_features. 
            #In this example, the n_features is 5. We will make timesteps = 14 (past days data used for training). 

            #Empty lists to be populated using formatted training data
            trainX = []
            trainY = []

            n_future = 1   # Number of days we want to look into the future based on the past days.
            n_past = 14  # Number of past days we want to use to predict the future.

            #Reformat input data into a shape: (n_samples x timesteps x n_features)
            #In my example, my df_for_training_scaled has a shape (12823, 5)
            #12823 refers to the number of data points and 5 refers to the columns (multi-variables).
            for i in range(n_past, len(df_for_training_scaled) - n_future +1):
                trainX.append(df_for_training_scaled[i - n_past:i, 0:df_for_training.shape[1]])
                trainY.append(df_for_training_scaled[i + n_future - 1:i + n_future, 0])

            trainX, trainY = np.array(trainX), np.array(trainY)

            print('trainX shape == {}.'.format(trainX.shape))
            print('trainY shape == {}.'.format(trainY.shape))

            #In my case, trainX has a shape (12809, 14, 5). 
            #12809 because we are looking back 14 days (12823 - 14 = 12809). 
            #Remember that we cannot look back 14 days until we get to the 15th day. 
            #Also, trainY has a shape (12809, 1). Our model only predicts a single value, but 
            #it needs multiple variables (5 in my example) to make this prediction. 
            #This is why we can only predict a single day after our training, the day after where our data ends.
            #To predict more days in future, we need all the 5 variables which we do not have. 
            #We need to predict all variables if we want to do that. 

            # define the Autoencoder model

            model = Sequential()
            model.add(LSTM(64, activation='relu', input_shape=(trainX.shape[1], trainX.shape[2]), return_sequences=True))
            model.add(LSTM(32, activation='relu', return_sequences=False))
            model.add(Dropout(0.2))
            model.add(Dense(trainY.shape[1]))

            model.compile(optimizer='adam', loss='mse')
            model.summary()


            # fit the model
            history = model.fit(trainX, trainY, epochs=5, batch_size=16, validation_split=0.1, verbose=1)
            # self.train_screen = MainApp.get_running_app().root.get_screen('dashboard').ids.trained_dataframe_screen

            # self.train_screen.clear_widgets()
            # plt.xlabel('Training loss')
            # plt.ylabel('Validation loss')
            # plt.plot(history.history['loss'], label='Training loss')
            # plt.plot(history.history['val_loss'], label='Validation loss')
            # plt.legend()
            
            # self.train_screen.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        

            # Predicting...
            # Libraries that will help us extract only business days in the US.
            # Otherwise our dates would be wrong when we look back (or forward).
            # from pandas.tseries.holiday import USFederalHolidayCalendar
            # from pandas.tseries.offsets import CustomBusinessDay
            # us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())
            # Remember that we can only predict one day in future as our model needs 5 variables
            # as inputs for prediction. We only have all 5 variables until the last day in our dataset.
            n_past = 91
            n_days_for_prediction = 90  # let us predict past 15 days

            # predict_period_dates = pd.date_range(list(train_dates)[-n_past], periods=n_days_for_prediction, freq='1d').tolist()
            predict_period_dates = pd.date_range(list(train_dates)[-1], periods=n_days_for_prediction, freq='1d').tolist()
            print(predict_period_dates)

            # Make prediction
            prediction = model.predict(trainX[-n_days_for_prediction:])  # shape = (n, 1) where n is the n_days_for_prediction

            print("PREDICTION: ", prediction)

            # Perform inverse transformation to rescale back to original range
            # Since we used 5 variables for transform, the inverse expects same dimensions
            # Therefore, let us copy our values 5 times and discard them after inverse transform
            print("DF FOR TRAINING: ", df_for_training.shape[1])
            prediction_copies = np.repeat(prediction, df_for_training.shape[1], axis=-1)
            y_pred_future = scaler.inverse_transform(prediction_copies)[:, 0]

            print("PREDICTION VALUES: ", y_pred_future)

            # Convert timestamp to date
            forecast_dates = []
            for time_i in predict_period_dates:
                forecast_dates.append(time_i.date())

            print("FORCAST DATE: %s" % forecast_dates)

            df_forecast = pd.DataFrame({'Date': np.array(forecast_dates), 'Rainfall Amount (mm)': y_pred_future})
            df_forecast['Date'] = pd.to_datetime(df_forecast['Date'], format="%Y-%m-%d")

            res_forecast = df_forecast.copy()
            res_forecast.columns = ['Date', 'Forecasted Rainfall Amount (mm)']
            res_forecast['Date'] = pd.to_datetime(res_forecast['Date'], format="%Y-%m-%d")
            col = list(res_forecast.columns)
            print("Columns: %s" % col)
            row = res_forecast.to_records(index=False)
            print(res_forecast.head())

            # for i in row:
                # i[0] = datetime.datetime.strptime(i[0], format='%Y-%m-%d').strftime('%Y-%m-%d')
                # print("Date values: ", i[0])
            # print("Rows of records: %s" % row)
            col = [(x, dp(60)) for x in col]
            table = MDDataTable(
                pos_hint={"center_x": .5, "center_y": .5},
                size_hint=(1, .9),
                # height = '490dp',
                column_data=col,
                row_data=row,
                use_pagination=True,
                rows_num=10,
                pagination_menu_height='240dp',
            )

            print("\n================================")
            print("FORECAST FINAL RESULT: ", df_forecast)
            self.train_screen = MainApp.get_running_app().root.get_screen('dashboard').ids.prediction_result_screen  
            self.train_screen.add_widget(table)
            
            original = df[['Date', 'Rainfall Amount (mm)']]
            original['Date'] = pd.to_datetime(original['Date'], format="%Y-%m-%d")
            original = original.loc[original['Date'] >= '2014-05-01']
            # original = original.loc[original['Date']]

            self.plot_screen = MainApp.get_running_app().root.get_screen('dashboard').ids.original_dataframe_screen
            plt.cla()
            self.plot_screen.clear_widgets()
            
            plt1, = plt.plot(original['Date'], original['Rainfall Amount (mm)'], label='Original Rainfall Amount (mm)')
            plt2, = plt.plot(df_forecast['Date'], df_forecast['Rainfall Amount (mm)'], label='Predicted Rainfall Amount (mm)')
            plt.ylabel('Rainfall Amount (mm)')
            plt.xlabel('Year(yr)')
            plt.legend(loc='upper right', handles=[plt1, plt2])
            
            self.plot_screen.add_widget(FigureCanvasKivyAgg(plt.gcf()), index=1)



            MainApp.get_running_app().root.get_screen('dashboard').ids.screen_manager.get_screen('upload_from_csv').manager.current = "display_graph"
        Window.size = (1000, 600)

    def pop(self, filename):
        self.progress_bar.value = 1
        self.popup.bind(on_open=self.puopen(filename))
        self.popup.open()

    # To continuously increasing the value of pb.
    def next(self, filename):
        if self.progress_bar.value >= 100:
            self.showdataframe(filename)
        self.progress_bar.value += 1

    def puopen(self, filename):
        Clock.schedule_interval(self.next(filename), 100)


if __name__ == "__main__":
    MainApp().run()
