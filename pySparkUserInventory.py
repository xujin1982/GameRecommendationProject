# Build Recommender system based on pySpark


import json
from pyspark.mllib.recommendation import ALS
from pyspark import SparkContext
from sqlalchemy import create_engine
import pandas as pd

import codecs
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

# sc = SparkContext()

path_user_inventory = '../output/wen_user_inventory_5000.txt'

def parse_raw_sting(raw_sting):
    user_inventory = json.loads(raw_sting)
    return user_inventory.items()[0]

user_inventory_rdd = sc.textFile(path_user_inventory).map(parse_raw_sting).zipWithIndex()

def id_index(x):
    ((user_id, lst_inventory),index) = x
    return (index,user_id)

dic_id_index = user_inventory_rdd.map(id_index).collectAsMap()

def create_tuple(x):
    ((user_id, lst_inventory),index) = x
    if lst_inventory != None:
        return (index,[(i.get('appid'),i.get('playtime_forever')) \
                       for i in lst_inventory if i.get('playtime_forever') > 0])
    else:
        return (index,[])
    
training_rdd = user_inventory_rdd.map(create_tuple).flatMapValues(lambda x: x)\
    .map(lambda (index,(appid,time)):(index,appid,time))

model = ALS.train(training_rdd,5)

dic_recommended = {'g0':{},'g1':{},'g2':{},'g3':{},'g4':{},'g5':{},
                   'g6':{},'g7':{},'g8':{},'g9':{}}
for index in dic_id_index.keys():
    try:
        lst_recommended = [i.product for i in model.recommendProducts(index,10)]
        user_id = dic_id_index.get(index)
        rank = 0
        for app_id in lst_recommended:
            dic_recommended['g%s'%rank].update({user_id:app_id})
            rank += 1
    except:
        pass
df = pd.DataFrame(dic_recommended)
df.index.name = 'user_id'
df = df.reset_index()


engine = create_engine('mysql+mysqlconnector://root:1234@127.0.0.1/game_recommendation?charset=utf8mb4')

df.to_sql('tbl_recommend_games',engine, if_exists = 'replace')