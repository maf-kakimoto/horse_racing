# -*- coding: utf-8 -*-

import time
import pandas as pd
from lib import load_yaml
from lib import manage_mysql
from lib import var2gl
from lib import config
from lib import query
from module import features

var2gl._bet()


def merge(tablename, featuresList, idDict):

    con, cur = manage_mysql._connect()

    horseinfotable = 'horseInfo'
    conditionDic = {}
    sql = query._select(horseinfotable, conditionDic)
    horseinfo_pd = pd.read_sql(sql, con)

    features._table(tablename, featuresList)
    sqlkey = {}

    for i in range(len(horseinfo_pd)):
        print(horseinfo_pd['name'][i], horseinfo_pd['horse_code'][i])

        initial_ja = horseinfo_pd['name'][i][0]
        sqlkey['initial_en'] = idDict['syllabary'][initial_ja]
        sqlkey['horse_code'] = horseinfo_pd['horse_code'][i]
        sqlkey['epoch'] = str(time.time())

        features._features(sqlkey, idDict, tablename, featuresList, {}, con, cur)
        con.commit()

    con.close()


if __name__ == '__main__':

    tablename = 'features'
    featuresList = load_yaml._load_yaml(config.path_setting + 'features.yml')
    idDict = features._load_dict()

    merge(tablename, featuresList, idDict)
