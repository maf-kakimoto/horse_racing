# -*- coding: utf-8 -*-

import glob
from lib import manage_mysql
from lib import load_yaml
from lib import config
from lib import var2gl
from lib import query
from module import file2db

var2gl._bet()


def syllabarytable(syllabaryDoct, resultcolumnList):

    con, cur = manage_mysql._connect()

    for syllabary in syllabaryDoct:
        table = '_raceResult_' + syllabaryDoct[syllabary]
        type = 'varchar(64)'
        query._drop(table)
        query._create(table, resultcolumnList, type)

    manage_mysql._end(con)


def backward(syllabaryDoct):

    yaml = config.path_setting + 'holdings_all.yml'
    holdingsDic = load_yaml._load_yaml(yaml)

    result = {}
    for course in holdingsDic:
        yearDic = holdingsDic[course]['year']
        for year in yearDic:
            timeDic = yearDic[year]
            if type(timeDic) is dict:
                for times in timeDic:
                    days = timeDic[times]
                    for day in range(days):
                        holding = str('{0:02d}'.format(times))
                        holding += str('{0:02d}'.format(day+1))
                        path_races = config.path_bet + 'races/'
                        path_races += course + '/'
                        path_races += str(year) + '/'
                        path_races += holding + '/'
                        files = glob.glob(path_races + '*.csv')
                        for file in files:
                            file2db._file2db(file, result, syllabaryDoct, 'backward')


def mergedresulttable(syllabaryDoct, raceresultcolumnList, horseinfocolumnList):

    con, cur = manage_mysql._connect()

    for syllabary in syllabaryDoct:
        table = '_raceResult_' + syllabaryDoct[syllabary]
        view = '_view' + table
        sql = 'DROP VIEW if exists ' + view
        cur.execute(sql)

        sql = 'CREATE VIEW ' + view
        sql += ' AS select'
        for raceresultcolumn in raceresultcolumnList:
            sql += ' R.' + raceresultcolumn + ' AS ' + raceresultcolumn + ','
        for horseinfocolumn in horseinfocolumnList:
            sql += ' I.' + horseinfocolumn + ' AS ' + horseinfocolumn + ','
        sql = sql[:-1]
        sql += ' from (' + table + ' R join horseInfo I on R.horse_code = I.horse_code)'
        cur.execute(sql)

    manage_mysql._end(con)


def allresulttable(syllabaryDoct, raceresultcolumnList, horseinfocolumnList):

    con, cur = manage_mysql._connect()

    table = 'raceresult'
    columnList = raceresultcolumnList + horseinfocolumnList
    type = 'varchar(64)'
    query._drop(table)
    query._create(table, columnList, type)

    for syllabary in syllabaryDoct:
        table = '_view_raceresult_' + syllabaryDoct[syllabary]
        conditionDic = {}
        sql = query._select(table, conditionDic)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            table = 'raceresult'
            sql = query._insert_from_List(table, row)
            cur.execute(sql)

    manage_mysql._end(con)


if __name__ == '__main__':

    yaml = config.path_setting + 'syllabary.yml'
    syllabaryDoct = load_yaml._load_yaml(yaml)
    yaml = config.path_setting + 'resultdb.yml'
    raceresultcolumnList = load_yaml._load_yaml(yaml)
    yaml = config.path_setting + 'horseinfodb.yml'
    horseinfocolumnList = load_yaml._load_yaml(yaml)

    syllabarytable(syllabaryDoct, raceresultcolumnList)

    backward(syllabaryDoct)
    mergedresulttable(syllabaryDoct, raceresultcolumnList, horseinfocolumnList)
    allresulttable(syllabaryDoct, raceresultcolumnList, horseinfocolumnList)
