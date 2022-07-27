import datetime
# from pyexpat import model
import warnings
# from time import sleep
# from turtle import onclick, pos, width
# from wsgiref import headers
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
# from matplotlib import axis
import mysql.connector
import os
import sys
from dotenv import load_dotenv
import random
import bcrypt
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.datatables import MDDataTable
from kivy.uix.boxlayout import BoxLayout
import numpy as np
# from numpy import size, spacing
# import openpyxl
import shelve
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
# from pyparsing import one_of
# import keras
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from kivy.metrics import dp
import threading
from pathlib import Path
# from sklearn.model_selection import train_test_split

rcParams['figure.figsize']=20,10

sendmailfile = os.path.join(os.path.split(sys.argv[0])[0][0], 'emailclient').replace('\\', '/')

sys.path.insert(0, sendmailfile)

gardenpath = os.path.join(os.path.split(sys.argv[0])[0][0], 'garden').replace('\\', '/')

sys.path.insert(0, gardenpath)

from garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import sendmail

load_dotenv()

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


conn = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
cursor = conn.cursor()


class MainApp(MDApp):
    warnings.filterwarnings('ignore')
    dialog = False
    dialog1 = False
    loadfiles = False
    layout = None
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"
        self.title = 'QAnalytics'
        self.icon = 'images/logo.png'
        kv = Builder.load_file('fe/auth.kv')
        return kv

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
                    if cursor.execute(sql):
                        to = self.email
                        subject = 'Account Creation for QAnalytics'
                        emailMsg = '''<div style="background: #eee;padding: 10px;">
                            <div style="max-width: 500px;margin: 0px auto;font-family: sans-serif;text-align: center;background: #fff;border-radius: 5px;overflow: hidden;">
                                <div style="width: 100%;background: #fc9700;">
                                    <h1 style="color: #fff;text-decoration: none;margin: 0px;padding: 10px 0px;">QAnalytics</h1>
                                </div>
                                <div style="color: #000;padding: 10px;margin-top: 10px;">
                                    Hello ' . $name . ', Thank you for registering with us at QAnalytics. Please use the 6-digit code below as your confirmation code.
                                    <div style="padding: 10px;margin: 10px 0px;color: #000;background: #eee;border-radius: 5px;">
                                    Account Confirmation code:
                                        <div style="font-size: 35px; color: #000;font-weight: 700;">
                                            ' . $code . '
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
                        alt = '''Hello user, Thank you for registering with us at SolarVillage. Please use the 6-digit code below as your confirmation code. <br /> ' . code . ' <br /> However, if this registration process was not initiated by you, kindly ignore this mail. <br />If you have encounter any problem while creating your account, feel free to contact us by visiting ' . $webhost . '/contact'''
                        sendmail.SendMail(to, subject, emailMsg, alt)
                    signupok = "SignUp Successful"
                    self.alert(signupok)
            else:
                self.errormsg(verror)
        finally:
            conn.commit()

    def signin(self):
        signin_screen = MainApp.get_running_app().root.get_screen('signin')
        self.email = signin_screen.ids.signin_field.text.strip()
        self.password = signin_screen.ids.pwd_field.text.strip()

        self.password = self.password.encode('utf-8')

        sql = f"SELECT * FROM users WHERE email = '{self.email}'"
        cursor.execute(sql)
        res = cursor.fetchall()
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
            conn.commit()
    
    def checkuser(self, email):
        sql = f"SELECT * FROM users WHERE email = '{email}'"
        cursor.execute(sql)
        res = cursor.fetchall()
        if not res:
            return False
        else:
            return True

    def logout(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = "Logout Dialog Box",
                text = "Do you want to log out now?",
                buttons = [
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
            signin_screen.ids.signin_field.text = ''
            signin_screen.ids.pwd_field.text = ''
            if self.dialog1.dismiss():
                self.dialog1 = False
            signin_screen.manager.current = "dashboard"
             
        self.dialog1.dismiss()
            

    def alert(self, message):
        if not self.dialog1:
            self.dialog1 = MDDialog(
                title = "Confirm",
                text = message,
                buttons = [
                    MDRectangleFlatButton(text="OK", text_color=self.theme_cls.primary_color, on_release=self.closealert),
                ],
            )
        self.dialog1.open()

    def errormsg(self, message):
        print(message)
        if not self.dialog1:
            self.dialog1 = MDDialog(
                title = "Error",
                text = message,
                buttons = [
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
        threading.Thread(target=self.showdataframe, args=(filename)).start()
       
    def showdataframe(self, filename):
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
                read_file.to_csv(fr'{csv_path}', index = None, header=True)   
                
                # read csv file and convert into a dataframe object
                df = pd.DataFrame(pd.read_csv(fr'{csv_path}', header=10))
                # get column header names
                new_headers = ['Stnno', 'Year', 'Month', 'Day', 'Hour (MST)', 'Pressure MSL (Hpa)', 'Dry Bulb Temp. (⁰ C)', 'Dew Point (⁰ C)', 'Relative Humidity (%)', 'Mean Surface Direction (⁰)', 'Wind Speed (m/s)', 'Rainfall Duration (m/s)', 'Rainfall Amount (mm)']
                
                # show the dataframe
                df.columns = new_headers
                col = list(df.columns)
                row = df.to_records(index=False)
                self.df_screen = MainApp.get_running_app().root.get_screen('dashboard').ids.screen_manager.get_screen('upload_from_csv')

                col = [(x, dp(60)) for x in col]
                self.layout = BoxLayout(orientation = 'vertical')
                innerbox = BoxLayout(orientation = 'horizontal', spacing = '5', padding = (5, 5, 5, 5), size_hint=(1, .1))

                closebtn = MDFlatButton(
                    text = '        Close        ',
                    pos_hint = {"center_x": .5},
                    halign="left",
                    valign="bottom",
                    size_hint = (None, None),
                    size = (100, 40),
                    md_bg_color =  (36/255, 40/255, 43/255, 1),
                    on_release = self.closetable,
                )
                table = MDDataTable(
                    pos_hint = {"center_x": .5, "center_y": .5},
                    size_hint = (1, .9),
                    # height = '490dp',
                    column_data = col,
                    row_data = row,
                    use_pagination = True,
                    rows_num = 10,
                    pagination_menu_height = '240dp',
                )

                button = MDFlatButton(
                    text = '        Perform Analysis        ',
                    pos_hint = {"center_x": .5},
                    size_hint = (None, None),
                    size = (200, 40),
                    md_bg_color =  (36/255, 40/255, 43/255, 1),
                    on_release=self.analyze,
                )
                self.layout.add_widget(table)
                innerbox.add_widget(closebtn)
                innerbox.add_widget(button)
                self.layout.add_widget(innerbox)
                self.df_screen.add_widget(self.layout)

                self.file_id = random.randint(START, END)
                self.filename = 'csvfile-'+cur_date_ft+'.csv'
                self.filepath = fr'{csv_path}'
                self.created = datetime.datetime.now()
                get_user = shelve.open('get_user')
                user = get_user['user']
                self.userid = user[1]
                # save the csv file path 
                sql = "INSERT INTO data_frame (file_id, userid, filename, filepath, filetype, created) VALUES ('%i', '%i', '%s', '%s', '%s', '%s')" % (self.file_id, self.userid, self.filename, self.filepath, 'csv', self.created)

                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                csverr = f"Please upload a valid csv file. {e}"
                print(csverr)
                self.alert(csverr)

    def analyze(self, obj):
        # get user 
        get_user = shelve.open('get_user')
        user = get_user['user']
        userid = user[1]
        # get the currently uploaded csv file
        sql = f"SELECT filepath FROM data_frame WHERE userid = '{userid}' ORDER BY created DESC LIMIT 1"
        cursor.execute(sql)
        csv_path = cursor.fetchall()[0][0]
        print("CSV FILE PATH IN ANALYSE", csv_path)
        # check if result exist then create dataframe
        if csv_path and Path(csv_path).is_file():
            # read csv file and convert into a dataframe object
            df = pd.read_csv(fr'{csv_path}', header=10)
            df = df.astype({'( mm )': float})
            df['Year'] = pd.to_datetime(df.Year, format='%Y')
            print("INITIAL DATA FROM PANDAS: ", df[['Year', '( mm )']])
            # get column header names
            new_headers = ['Stnno', 'Year', 'Month', 'Day', 'Hour (MST)', 'Pressure MSL (Hpa)', 'Dry Bulb Temp. (⁰ C)', 'Dew Point (⁰ C)', 'Relative Humidity (%)', 'Mean Surface Direction (⁰)', 'Wind Speed (m/s)', 'Rainfall Duration (m/s)', 'Rainfall Amount (mm)']
            
            # # show the dataframe
            # df.columns = new_headers
            # data = pd.DataFrame(index = range(0, len(df)), columns = new_headers)
            df.index = df['Year']
            df = df.sort_index(ascending=True, axis=True)
            
            data_frame = pd.DataFrame(index=range(0, len(df)), columns=['Year', 'Rainfall Amount (mm)'])
            # prepare data
            for i in range(0, len(df)):
                data_frame['Year'][i] = df['Year'][i]
                data_frame['Rainfall Amount (mm)'][i] = df['( mm )'][i]
            print("DATA FRAME", data_frame)

            # min-max scalar
            scaler = MinMaxScaler(feature_range=(0,1))
            data_frame.index  = data_frame.Year
            data_frame.drop('Year', axis=1, inplace=True)
            final_data = data_frame.values
            train_data = final_data[0:200,:]
            valid_data = final_data[200:,:]
            print("FINAL DATA", final_data)
            print("TRAIN DATA", train_data)
            print("VALID DATA", valid_data)
            scaler = MinMaxScaler(feature_range=(0,1))

            scaled_data = scaler.fit_transform(final_data)
            x_train_data, y_train_data = [], []
            for i in range(60, len(train_data)):
                x_train_data.append(scaled_data[i-60:i,0])
                y_train_data.append(scaled_data[i,0])

            x_train_data = np.array(x_train_data)
            y_train_data = np.array(y_train_data)
            print("X TRAIN DATA: ", x_train_data)
            print("Y TRAIN DATA: ", y_train_data)
            # Long Short-term memory model
            lstm_model = Sequential()
            lstm_model.add(LSTM(units=50, return_sequences=True, input_shape=(np.shape(x_train_data)[1], 1)))
            lstm_model.add(LSTM(units=50))
            lstm_model.add(Dense(1))
            print("DATAFRAME LENGTH: ", len(data_frame))
            print("VALID DATA: ", len(valid_data))
            # print("DATA FRAME MINUS VALID DATA: ", data_frame[140:])
            # print("DATA FRAME MINUS VALID DATA VALUES: ", data_frame[140:].values)
            model_data = data_frame[len(data_frame)-len(valid_data)-60:].values
            
            print("MODEL DATA: ", model_data)

            model_data = model_data.reshape(-1, 1)
            model_data = scaler.transform(model_data)

            # test and train data
            lstm_model.compile(loss='mean_squared_error', optimizer='adam')
            lstm_model.fit(x_train_data, y_train_data, epochs=1, batch_size=1, verbose=2)
            
            x_test = []

            for i in range(60, model_data.shape[0]):
                x_test.append(model_data[i-60:i,0])
            x_test = np.array(x_test)
            print("X TEST NP DATA BEFORE: ", x_test)
            print("X TEST SHAPE: ", x_test.shape)
            # print("X TEST SHAPE 1: ", x_test.shape[1])
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
            print("X TEST NP DATA AFTER: ", x_test)



            # prediction function and result
            predicted_rainfall_amt = lstm_model.predict(x_test)
            predicted_rainfall_amt = scaler.inverse_transform(predicted_rainfall_amt)

            train_data = data_frame[:200]
            valid_data = data_frame[200:]
            print("VALID DATA: ", valid_data)
            valid_data['predictions'] = predicted_rainfall_amt
            plt.plot(train_data['Rainfall Amount (mm)'])
            plt.plot(valid_data[['Rainfall Amount (mm)', 'predictions']])
            plt.ylabel('Rainfall Amount (mm)')
            plt.xlabel('Year')

            self.plot_screen = MainApp.get_running_app().root.get_screen('dashboard').ids.screen_manager.get_screen('display_graph')
            self.plot_screen.add_widget(FigureCanvasKivyAgg(plt.gcf()))

            MainApp.get_running_app().root.get_screen('dashboard').ids.screen_manager.get_screen('upload_from_csv').manager.current = "display_graph"



if __name__ == "__main__":
    MainApp().run()