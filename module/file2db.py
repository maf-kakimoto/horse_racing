# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from lib import load_yaml
from lib import config
from lib import manage_mysql
from lib import query
from module import corner


def _file2db(file, result, syllabaryDoct, b_or_f):

    data = open(file, 'r')
    fileitem = file.split('_')
    print(fileitem[0])
    racekey = fileitem[0].split('/')
    reader = csv.DictReader(data)
    result['year'] = racekey[-1][:4]
    result['course'] = racekey[-1][4:6]
    result['holding'] = racekey[-1][6:10]
    result['raceNo'] = racekey[-1][10:12]
    result['roadbed'] = fileitem[1]
    result['distance'] = fileitem[2]
    if result['course'] == '04' or result['course'] == '08' or result['course'] == '09':
        result['outFlg'] = fileitem[3]
    else:
        result['outFlg'] = '0'
    result['roadCondition'] = fileitem[4]
    result['ageclass'] = fileitem[5]
    result['winclass'] = fileitem[6]
    result['sexclass'] = fileitem[7]
    result['loafCondition'] = fileitem[8]
    result['number'] = fileitem[9]
    result['weather'] = fileitem[10]
    result['racedate'] = fileitem[11].split('.')[0]
    date = result['racedate'].split('-')
    epoch = datetime(
        int(date[0]),
        int(date[1]),
        int(date[2].split('.')[0]), 0, 0).strftime('%s')
    result['racedate_epoch'] = epoch

    for row in reader:
        if str.isdecimal(row['rank']) or row['rank'] == '':
            yaml = config.path_setting + 'distance_category.yml'
            distance_category = load_yaml._load_yaml(yaml)
            if result['distance'] in distance_category:
                result['distancecategory'] = distance_category[result['distance']]
            else:
                result['distancecategory'] = 'others'

            result['ranking'] = row['rank']
            result['gate'] = row['gate']
            result['horseName'] = row['horseName']
            result['horse_code'] = row['horse_code']
            result['sex'] = row['sex']
            if result['year'] == '' or row['age'] == '' or row['age'] == '-':
                result['birth'] = ''
            else:
                result['birth'] = str(int(result['year']) - int(row['age']))
            result['age'] = row['age']
            result['loaf'] = row['loaf']
            result['jockey'] = row['jockey']
            result['jockey_code'] = row['jockey_code']
            result['time'] = row['time']
            result['diff'] = row['diff']
            if row['popularity'] == '':
                result['popularity'] = result['number']
            else:
                result['popularity'] = row['popularity']
            result['odds'] = row['odds']
            if row['last'] == '-' or row['last_rank'] == '-':
                result['last'] = '100.0'
                result['last_rank'] = result['number']
            else:
                result['last'] = row['last']
                result['last_rank'] = row['last_rank']

            result['corner'] = row['corner']
            cornerDict = corner._corner(result['corner'], result['number'])
            for key in cornerDict:
                result[key] = cornerDict[key]

            result['trainer'] = row['trainer']
            result['trainer_code'] = row['trainer_code']
            result['trainer_belongs'] = row['belongs']
            result['owner'] = row['owner']
            result['owner_code'] = row['owner_code']
            if row['weight'] == '-' or row['weightDiff'] == '-':
                result['weight'] = '470'
                result['weightDiff'] = '0'
            else:
                result['weight'] = row['weight']
                result['weightDiff'] = row['weightDiff']
            result['prize'] = row['prize']
            result['tansho'] = row['tansho']
            result['fukusho'] = row['fukusho']

            if b_or_f == 'backward':
                initial = result['horseName'][0]
                table = '_raceResult_' + syllabaryDoct[initial]
            elif b_or_f == 'forward':
                table = 'target'

            if result['distancecategory'] != 'others':
                con, cur = manage_mysql._connect()
                sql = query._insert_from_Dict(table, result)
                cur.execute(sql)
                manage_mysql._end(con)

    data.close()
