#This project is to retrieve data from ISS and store it in an excel and SQL Database

import csv

import pandas as pd
import requests
from _datetime import datetime
import pandas
import matplotlib.pyplot as plt
import numpy as np

#Data from ISS Station
response_iss = requests.get(url="http://api.open-notify.org/iss-now.json")
response_iss.raise_for_status()

data_iss = response_iss.json()

longitude = round(float(data_iss["iss_position"]["longitude"]),1)
latitude = round(float(data_iss["iss_position"]["latitude"]),1)
print(type(latitude))
position = (latitude,longitude)


#Data from Time
import pytz
from datetime import datetime

# Set the timezone to US/Eastern
tz = pytz.timezone('Europe/Madrid')

# Get the current time in the specified timezone
time_now = datetime.now(tz)

# Print the current time
print(time_now)
LAT_MADRID = 40.24
LNG_MADRID = 3.43
parameters = {
    "lat": LAT_MADRID,
    "lng": LNG_MADRID,
    "formatted": 0,
}
response_time = requests.get(url="https://api.sunrise-sunset.org/json", params=parameters)
response_time.raise_for_status()
data_time = response_time.json()
sunrise = data_time["results"]["sunrise"]
sunset = data_time["results"]["sunset"]
day_length = data_time["results"]["day_length"]

month = sunrise.split("T")[0].split("-")[1]
day = sunrise.split("T")[0].split("-")[2]
hour = time_now.hour
minute = time_now.minute

data_dict = {
    "day": day,
    "hour": hour,
    "minute": minute,

    "latitude": latitude,
    "longitude": longitude,
}
print(data_dict)

#Data processing

data_frame_dirty = pandas.DataFrame((data_dict), index=[0])
print(data_frame_dirty)
data_frame_dirty.to_csv("row_data.csv", mode="a")
data_not_cleaned = pandas.read_csv("row_data.csv")
data_frame_cleaned = data_not_cleaned[data_not_cleaned.day != "day"]
data_frame_cleaned = data_frame_cleaned.drop(columns=["Unnamed: 0"])
print(data_frame_cleaned)
data_frame_cleaned.to_csv("clean_data.csv", mode="w")

from flask import Flask,render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
with app.app_context():
    #Create database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ISS_database.db'
    db = SQLAlchemy(app)

    #Create table
    class ISS(db.Model):
         id = db.Column(db.Integer,primary_key=True)
         day = db.Column(db.Integer, nullable=False)
         hour = db.Column(db.Integer, nullable=False)
         minute = db.Column(db.Integer, nullable=False)
         latitude = db.Column(db.Float, nullable=False)
         longitude = db.Column(db.Float, nullable=False)

    db.create_all()
    #Create record
    new_data = ISS(
        day = data_dict["day"],
        hour = data_dict["hour"],
        minute = data_dict["minute"],
        latitude = data_dict["latitude"],
        longitude = data_dict["longitude"],
    )
    print('record created')
    db.session.add(new_data)
    db.session.commit()


    #Create record
    new_data = ISS(
        day = data_dict["day"],
        hour = data_dict["hour"],
        minute = data_dict["minute"],
        latitude = data_dict["latitude"],
        longitude = data_dict["longitude"],
    )
    db.session.add(new_data)
    db.session.commit()

#Visualization of data with Matplotlib

#Data from csv file
# data_csv = pandas.read_csv('clean_data.csv')
# x = data_csv["longitude"]
# y = data_csv["latitude"]

#Data from database
import sqlite3
conn = sqlite3.connect('instance/ISS_database.db')

query = "SELECT longitude,latitude FROM iss"
data_db = pd.read_sql(query,conn)

x = data_db['longitude']
y = data_db['latitude']

plt.plot(x, y)

plt.xlim(-180, 180)
plt.ylim(-90, 90)
plt.title('ISS Position',fontsize=20)
plt.xlabel('Longitude', fontsize=10)
plt.ylabel('Latitude', fontsize=10)

plt.xticks(np.arange(-180,180,30),fontsize=10)
plt.yticks(np.arange(-90,90,30),fontsize=10)
plt.show()


