# -*- coding: utf-8 -*-

import yaml
import pandas as pd
from lib import manage_mysql
from lib import load_yaml
from lib import config
from lib import var2gl
from lib import query

var2gl._bet()


def racetime():

    con, cur = manage_mysql._connect()

    table = 'raceresult'
    distanceList = load_yaml._load_yaml(config.path_setting + 'distance_category.yml')

    timeDict = {}
    for distance in distanceList:
        for roadbed in range(0, 2):
            for roadcondition in range(0, 4):

                columnList = [
                    'avg(time)',
                    'std(time)',
                    'avg(last)',
                    'std(last)'
                    ]
                conditionDict = {
                    'distance': '"' + str(distance) + '"',
                    'roadbed': '"' + str(roadbed) + '"',
                    'roadCondition': '"' + str(roadcondition) + '"'
                }

                sql = query._select(table, conditionDict, columnList)
                cur.execute(sql)
                total_ave, total_std, last_ave, last_std = cur.fetchone()
                if total_ave is not None:
                    condition = str(distance) + '_' + str(roadbed) + '_' + str(roadcondition)
                    timeDict[condition] = {
                        'total_ave': round(total_ave, 2),
                        'total_std': round(total_std, 2),
                        'last_ave': round(last_ave, 2),
                        'last_std': round(last_std, 2)
                    }

    timeYaml = yaml.dump(timeDict)
    file = 'time.yml'
    data = open(config.path_statistics + file, mode='w', encoding='utf-8')
    data.write(str(timeYaml))

    manage_mysql._end(con)


def winrate_all(statisticsList):

    con, cur = manage_mysql._connect()

    sqlDict = {
        'count_all': '',
        'count_1': ' where ranking=1',
        'count_2': ' where ranking=1 or ranking=2',
        'count_3': ' where ranking=1 or ranking=2 or ranking=3'
    }

    countDict = {}
    table = 'raceresult'
    sql = query._count(table)

    for key in sqlDict:
        cur.execute(sql + sqlDict[key])
        count = cur.fetchone()
        countDict[key] = count[0]

    countYaml = yaml.dump(countDict)
    file = 'average.yml'
    data = open(config.path_statistics + file, mode='w', encoding='utf-8')
    data.write(str(countYaml))

    manage_mysql._end(con)


def winrate_target(statisticsList):

    con, cur = manage_mysql._connect()

    whereDict = {
        'roadbed_turf': 'roadbed_0',
        'roadbed_dirt': 'roadbed_1',
        'distance_sprint': 'distancecategory_sprint',
        'distance_mile': 'distancecategory_mile',
        'distance_intermediate': 'distancecategory_intermediate',
        'distance_long': 'distancecategory_long',
        'distance_extended': 'distancecategory_extended',
        'course_01': 'course_01',
        'course_02': 'course_02',
        'course_03': 'course_03',
        'course_04': 'course_04',
        'course_05': 'course_05',
        'course_06': 'course_06',
        'course_07': 'course_07',
        'course_08': 'course_08',
        'course_09': 'course_09',
        'course_10': 'course_10',
        'winclass_debut': 'winclass_9',
        'winclass_0': 'winclass_0',
        'winclass_1': 'winclass_1',
        'winclass_2': 'winclass_2',
        'winclass_3': 'winclass_3',
        'winclass_open': 'winclass_4',
        'sex_male': 'sex_牡',
        'sex_female': 'sex_牝',
        'sex_gelding': 'sex_セ'
    }

    sqlDict = {
        'count_all': '',
        'count_1': ' and ranking=1',
        'count_2': ' and (ranking=1 or ranking=2)',
        'count_3': ' and (ranking=1 or ranking=2 or ranking=3)'
    }

    table = 'raceresult'

    for target in statisticsList:
        print(target)

        group = ' group by ' + target + '_code'

        countDict = {}
        for where in whereDict:
            whereList = whereDict[where].split('_')
            name = str(whereList[0])
            value = str(whereList[1])
            conditionDict = {name: '"' + value + '"'}
            selectList = {target + '_code', 'count(*)'}

            sql = query._select(table, conditionDict, selectList)

            for key in sqlDict:
                count_pd = pd.read_sql(sql + sqlDict[key] + group, con)

                for i in range(len(count_pd)):
                    code = str(count_pd[target + '_code'][i])
                    number = str(count_pd['count(*)'][i])
                    if key == 'count_all':
                        countDict[code + '_' + where] = ({key: number})
                    else:
                        countDict[code + '_' + where].update({key: number})

            countYaml = yaml.dump(countDict)
            file = target + '.yml'
            data = open(config.path_statistics + file, mode='w', encoding='utf-8')
            data.write(str(countYaml))

    manage_mysql._end(con)


if __name__ == '__main__':

    file = config.path_setting + 'statistics.yml'
    statisticsList = load_yaml._load_yaml(file)

    racetime()
    winrate_all(statisticsList)
    winrate_target(statisticsList)
