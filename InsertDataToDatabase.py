import pandas as pd
import numpy as np
import mysql.connector
from sqlalchemy import create_engine
import requests, json, os, time, sys, random

engine = create_engine('mysql+mysqlconnector://root:1234@127.0.0.1/game_recommendation?charset=utf8mb4')

engine.execute('''
    CREATE TABLE IF NOT EXISTS tbl_steam_app
    (
        steam_appid INT,
        name VARCHAR(500) CHARACTER SET utf8mb4,
        type VARCHAR(15),
        initial_price FLOAT,
        release_date VARCHAR(20),
        score INT,
        recommendations INT,
        windows BOOLEAN,
        mac BOOLEAN,
        linux BOOLEAN,
        header_image VARCHAR(100),
        required_age INT,
        developers VARCHAR(500) CHARACTER SET utf8mb4
    );
    ''')

columns = ['steam_appid', 'name', 'type', 'initial_price', 'release_date', 'score', 
        'recommendations', 'windows', 'mac', 'linux', 'header_image','required_age','developers']
app_detail_data = pd.DataFrame(pd.DataFrame(np.array([np.nan] * len(columns))).T, columns = columns)

app_detail_file = '../output/2016-12-27_app_detail_test.txt'
with open(app_detail_file, 'rb') as f:
    for line in f.readlines():
        temp = json.loads(line)
        tempid = temp.keys()[0]
        if temp[tempid]['success']:
            temp = temp[tempid]['data']
            app_detail_data.steam_appid = int(temp['steam_appid'])
            app_detail_data.name = temp['name']
            app_detail_data.apptype = temp['type']
            if temp['is_free']:
                app_detail_data.initial_price = 0
            else:
                try:
                    app_detail_data.initial_price = temp['price_overview']['initial']
                except:
                    pass
            app_detail_data.release_date = temp['release_date']['date']
            try:
                app_detail_data.score = int(temp['metacritic']['score'])
            except:
                pass
            try:
                app_detail_data.recommendations = int(temp['recommendations']['total'])
            except:
                pass
            app_detail_data.windows = temp['platforms']['windows']
            app_detail_data.mac = temp['platforms']['mac']
            app_detail_data.linux = temp['platforms']['linux']
            app_detail_data.header_image = temp['header_image']
            app_detail_data.required_age = int(temp['required_age'])
            try:
                app_detail_data.developers = temp['developers'][0]
            except:
                pass
            app_detail_data.to_sql('tbl_steam_app',engine,if_exists='append',index = False)