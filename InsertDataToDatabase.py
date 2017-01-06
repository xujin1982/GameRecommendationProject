import pandas as pd
import numpy as np
import mysql.connector
from sqlalchemy import create_engine
from datetime import datetime
import requests, json, os, time, sys, random, re

path_steam_app_info = 'E:/GitHub/output/steam_app_info.csv'

app_detail_file = '../output/2016-12-27_app_detail_test.txt'
with open(app_detail_file, 'rb') as f:
    dic_app_detail = {'name':{}, 'type':{}, 'initial_price':{}, 'release_date':{}, 'score':{}, 
                      'recommendations':{}, 'windows':{}, 'mac':{}, 'linux':{}, 'header_image':{}}
    lst_raw_string = f.readlines()
    total_count = len(lst_raw_string)
    count = 0
    for line in lst_raw_string:
        temp = json.loads(line)
        tempid = temp.keys()[0]        
        if temp[tempid]['success']:            
            temp = temp[tempid].get('data')
            steam_appid = int(temp.get('steam_appid'))
            name = temp.get('name')
            apptype = temp.get('type')

            if temp.get('is_free'):
                initial_price = 0
            else:
                initial_price = temp.get('price_overview',{}).get('initial')
            if temp.get('release_date').get('coming_soon') == False:
                temp_date = temp.get('release_date').get('date')
                if not temp_date == '':
                    if re.search(',',temp_date) == None:
                        release_date = datetime.strptime(temp_date, '%b %Y')
                    else:
                        try:
                            release_date = datetime.strptime(temp_date, '%b %d, %Y')
                        except:
                            pass
                        try:
                            release_date = datetime.strptime(temp_date, '%d %b, %Y')
                        except:
                            pass
            score = temp.get('metacritic',{}).get('score')
            recommendations = temp.get('recommendations',{}).get('total')
            header_image = temp.get('header_image')
            required_age = int(temp.get('required_age'))
            if not temp.get('developers') == None:
                developers = temp.get('developers')[0]
            windows = 1 if temp.get('platforms').get('windows') else 0
            mac = 1 if temp.get('platforms').get('mac') else 0
            linux = 1 if temp.get('platforms').get('linux') else 0
            count += 1            
            dic_app_detail['name'].update({steam_appid:name})
            dic_app_detail['type'].update({steam_appid:apptype})
            dic_app_detail['initial_price'].update({steam_appid:initial_price})
            dic_app_detail['release_date'].update({steam_appid:release_date})
            dic_app_detail['score'].update({steam_appid:score})
            dic_app_detail['recommendations'].update({steam_appid:recommendations})
            dic_app_detail['windows'].update({steam_appid:windows})
            dic_app_detail['mac'].update({steam_appid:mac})
            dic_app_detail['linux'].update({steam_appid:linux})
            dic_app_detail['header_image'].update({steam_appid:header_image})

            
df_app_detail = pd.DataFrame(dic_app_detail)
df_app_detail.initial_price = df_app_detail.initial_price.map(lambda x: x/100.0)
df_app_detail.index.name = 'steam_appid'
df_app_detail = df_app_detail[['name', 'type', 'initial_price', 'release_date', 'score', 
                               'recommendations', 'windows', 'mac', 'linux', 'header_image']]
df_app_detail.reset_index(inplace=True)
df_app_detail.to_csv(path_steam_app_info,encoding='utf8',index=False)

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
        header_image VARCHAR(100)
    );
    ''')

engine.execute('''
    LOAD DATA INFILE '%s' INTO TABLE `tbl_steam_app` 
    FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (@steam_appid, @name, @type, @initial_price, @release_date, @score, @recommendations, 
    @windows, @mac, @linux, @header_image)
    SET
    steam_appid = nullif(@steam_appid, ''),
    name = nullif(@name, ''),
    type = nullif(@type, ''),
    initial_price = nullif(@initial_price,''),
    release_date = nullif(@release_date,''),
    score = nullif(@score,''), 
    recommendations = nullif(@recommendations, ''),
    windows = nullif(@windows, ''),
    mac = nullif(@mac, ''),
    linux = nullif(@linux, ''),
    header_image = nullif(@header_image, '');
    ''' % path_steam_app_info)