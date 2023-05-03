# -*- coding: utf-8 -*-

import pandas as pd
from lib import load_yaml
from lib import config
from lib import query
from lib import manage_mysql


def _table(table, columnList):

    query._drop(table)
    con, cur = manage_mysql._connect()

    sql = 'CREATE table ' + table
    sql += ' ('
    for column in columnList:
        if column == 'horse_code':
            type = 'varchar(16)'
        else:
            type = 'varchar(8)'
        sql += column + ' ' + type + ','
    sql = sql[:-1]
    sql += ')'
    cur.execute(sql)

    manage_mysql._end(con)


def _load_dict():

    idDict = {}
    idDict['syllabary'] = load_yaml._load_yaml(config.path_setting + 'syllabary.yml')
    idDict['time'] = load_yaml._load_yaml(config.path_statistics + 'time.yml')
    idDict['average'] = load_yaml._load_yaml(config.path_statistics + 'average.yml')
    idDict['jockey'] = load_yaml._load_yaml(config.path_statistics + 'jockey.yml')
    idDict['trainer'] = load_yaml._load_yaml(config.path_statistics + 'trainer.yml')
    idDict['owner'] = load_yaml._load_yaml(config.path_statistics + 'owner.yml')
    idDict['producer'] = load_yaml._load_yaml(config.path_statistics + 'producer.yml')
    idDict['sire'] = load_yaml._load_yaml(config.path_statistics + 'sire.yml')

    return idDict


def _rate(target, key, targetDict, allrateDict):

    countDict = targetDict.get(key)
    rateDict = {}
    threshold = 100

    if countDict is not None:
        count_all = countDict.get('count_all')
        count_1 = countDict.get('count_1')
        count_2 = countDict.get('count_2')
        count_3 = countDict.get('count_3')

        if count_all is not None:
            count_all = int(count_all)
        else:
            count_all = 0

        if count_all > threshold and count_1 is not None:
            count_1 = int(count_1)
            rateDict['win'] = round(float(100 * count_1 / count_all), 2)
        else:
            rateDict['win'] = allrateDict['win']

        if count_all > threshold and count_2 is not None:
            count_2 = int(count_2)
            rateDict['double'] = round(float(100 * count_2 / count_all), 2)
        else:
            rateDict['double'] = allrateDict['double']

        if count_all > threshold and count_3 is not None:
            count_3 = int(count_3)
            rateDict['triple'] = round(float(100 * count_3 / count_all), 2)
        else:
            rateDict['triple'] = allrateDict['triple']

    else:
        rateDict = allrateDict

    return rateDict


def _features(sqlkey, idDict, tablename, featuresList, target, con, cur):

    raceresulttable = '_view_raceResult_' + sqlkey['initial_en']
    conditionDict = {'horse_code': '"' + sqlkey['horse_code'] + '"'}
    sql = query._select(raceresulttable, conditionDict)
    sql += ' and racedate_epoch<' + sqlkey['epoch']
    sql += ' order by racedate_epoch desc'
    pastresults = pd.read_sql(sql, con)
    print(sql)

    if len(target) > 0:
        raceresults = pd.concat([target, pastresults])
    else:
        raceresults = pastresults

    raceresults = raceresults.reset_index()

    if len(pastresults) == 0:
        iter_times = 0
    else:
        if len(target) > 0:
            iter_times = 2
        else:
            iter_times = len(raceresults) + 1

    for j in range(1, iter_times):

        featuresDict = {}
        for feature in featuresList:
            featuresDict[feature] = 0

        featuresDict['horse_code'] = raceresults['horse_code'][j-1]
        if raceresults['odds'][j-1] == '':
            featuresDict['odds'] = '-999.9'
        else:
            featuresDict['odds'] = raceresults['odds'][j-1]

        if raceresults['ranking'][j-1] == '':
            ranking = ''
        else:
            ranking = int(raceresults['ranking'][j-1])

        if ranking == '':
            featuresDict['rank_1'] = '0'
            featuresDict['rank_2'] = '0'
            featuresDict['rank_3'] = '0'
        else:
            if ranking < 2:
                featuresDict['rank_1'] = '1'
            if ranking < 3:
                featuresDict['rank_2'] = '1'
            if ranking < 4:
                featuresDict['rank_3'] = '1'

        course = raceresults['course'][j-1]
        featuresDict['course_' + course] = '1'

        year = (int(raceresults['year'][j-1]) - 2011)
        featuresDict['year'] = round(year, 1)

        month = raceresults['racedate'][j-1].split('-')[1]
        featuresDict['month_' + month] = '1'

        holding_day = int(raceresults['holding'][j-1][2:4])
        featuresDict['holding_day'] = holding_day

        epoch_thistime = int(raceresults['racedate_epoch'][j-1])
        if j == len(raceresults):
            epoch_lasttime = epoch_thistime
        else:
            epoch_lasttime = int(raceresults['racedate_epoch'][j])
        epoch_rotation = epoch_thistime - epoch_lasttime
        epoch_based_halfyear = 60 * 60 * 24 * 30 * 6
        epoch_rotation = 100 * epoch_rotation / epoch_based_halfyear
        featuresDict['epoch_rotation'] = round(epoch_rotation, 2)

        if raceresults['weather'][j-1] == '0':
            featuresDict['weather_sunny'] = '1'
        elif raceresults['weather'][j-1] == '1':
            featuresDict['weather_cloudy'] = '1'
        elif raceresults['weather'][j-1] == '2':
            featuresDict['weather_rain'] = '1'
        elif raceresults['weather'][j-1] == '3':
            featuresDict['weather_lightrain'] = '1'
        elif raceresults['weather'][j-1] == '4':
            featuresDict['weather_snow'] = '1'
        elif raceresults['weather'][j-1] == '5':
            featuresDict['weather_lightsnow'] = '1'

        featuresDict['raceno'] = int(raceresults['raceNo'][j-1])

        roadbed_thistime = raceresults['roadbed'][j-1]
        featuresDict['roadbed'] = roadbed_thistime
        roadbed_en = ''
        if roadbed_thistime == '0':
            roadbed_en = 'turf'
        else:
            roadbed_en = 'dirt'
        if j == len(raceresults):
            roadbed_lasttime = roadbed_thistime
        else:
            roadbed_lasttime = raceresults['roadbed'][j]
        if roadbed_thistime != roadbed_lasttime:
            featuresDict['roadbed_rotation'] = '1'

        distance_thistime = raceresults['distance'][j-1]
        featuresDict['distance'] = int((int(distance_thistime) - 1000) / 100)
        featuresDict['distance_out'] = raceresults['outFlg'][j-1]

        if distance_thistime in ['1600', '2000', '2400']:
            featuresDict['distance_core'] = '1'
        if j == len(raceresults):
            distance_lasttime = distance_thistime
        else:
            distance_lasttime = raceresults['distance'][j]
        distance_rotation = (int(distance_thistime) - int(distance_lasttime)) / 100
        featuresDict['distance_rotation'] = distance_rotation

        if raceresults['roadCondition'][j-1] == '0':
            featuresDict['road_good'] = '1'
        elif raceresults['roadCondition'][j-1] == '1':
            featuresDict['road_better'] = '1'
        elif raceresults['roadCondition'][j-1] == '2':
            featuresDict['road_worse'] = '1'
        elif raceresults['roadCondition'][j-1] == '3':
            featuresDict['road_worst'] = '1'

        if raceresults['ageclass'][j-1] == '4+':
            featuresDict['ageclass_4plus'] = '1'
        elif raceresults['ageclass'][j-1] == '3+':
            featuresDict['ageclass_3plus'] = '1'
        elif raceresults['ageclass'][j-1] == '3-':
            featuresDict['ageclass_3minus'] = '1'
        elif raceresults['ageclass'][j-1] == '2-':
            featuresDict['ageclass_2minus'] = '1'

        if raceresults['winclass'][j-1] == '9':
            featuresDict['winclass_debut'] = '1'
        elif raceresults['winclass'][j-1] == '0':
            featuresDict['winclass_0'] = '1'
        elif raceresults['winclass'][j-1] == '1':
            featuresDict['winclass_1'] = '1'
        elif raceresults['winclass'][j-1] == '2':
            featuresDict['winclass_2'] = '1'
        elif raceresults['winclass'][j-1] == '3':
            featuresDict['winclass_3'] = '1'
        elif raceresults['winclass'][j-1] == '4':
            featuresDict['winclass_open'] = '1'

        if raceresults['sexclass'][j-1] == '2':
            featuresDict['sexclass_femaleonly'] = '1'

        number = int(raceresults['number'][j-1])
        featuresDict['number'] = number

        featuresDict['gate'] = raceresults['gate'][j-1]
        if featuresDict['gate'] == '-':
            featuresDict['gate_odd'] = ''
        elif int(featuresDict['gate']) % 2 == 1:
            featuresDict['gate_odd'] = '1'
        else:
            featuresDict['gate_even'] = '1'

        sex = raceresults['sex'][j-1]
        sex_en = ''
        if sex == '牡':
            featuresDict['sex_male'] = '1'
            sex_en = 'male'
        elif sex == '牝':
            featuresDict['sex_female'] = '1'
            sex_en = 'female'
        else:
            featuresDict['sex_gelding'] = '1'
            sex_en = 'gelding'

        if raceresults['age'][j-1] == '':
            featuresDict['age'] = ''
        else:
            age = int(raceresults['age'][j-1]) - 2
            featuresDict['age'] = age

        weight = int(raceresults['weight'][j-1]) - 470
        featuresDict['weight'] = weight

        weightDiff = int(raceresults['weightDiff'][j-1])
        featuresDict['weightDiff'] = weightDiff

        loafDict = {
            '2_1st_male': 54,
            '2_2nd_male': 55,
            '2_1st_female': 54,
            '2_2nd_female': 54,
            '3_1st_male': 56,
            '3_2nd_male': 57,
            '3_1st_female': 54,
            '3_2nd_female': 55
        }
        if raceresults['age'][j-1] == '2':
            loafkey = '2_'
        else:
            loafkey = '3_'
        if int(month) < 10:
            loafkey += '1st_'
        else:
            loafkey += '2nd_'
        if sex in ['牡', 'セ']:
            loafkey += 'male'
        else:
            loafkey += 'female'

        if raceresults['loaf'][j-1] == '' or raceresults['loaf'][j-1] == '--':
            featuresDict['loaf'] = ''
        else:
            loaf = float(raceresults['loaf'][j-1])
            loaf_criteria = loafDict[loafkey]
            featuresDict['loaf'] = loaf - loaf_criteria

        iter = 0
        totaltime_dev_sum = 0
        totaltime_dev_max = 0
        lasttime_dev_sum = 0
        lasttime_dev_max = 0
        for k in range(0, len(raceresults) - j):
            totaltime = float(raceresults['time'][j+k])
            lasttime = float(raceresults['last'][j+k])
            distance = raceresults['distance'][j+k]
            roadbed = raceresults['roadbed'][j+k]
            roadcondition = raceresults['roadCondition'][j+k]
            avestdDict = idDict['time'][distance + '_' + roadbed + '_' + roadcondition]
            total_ave = float(avestdDict['total_ave'])
            total_std = float(avestdDict['total_std'])
            last_ave = float(avestdDict['last_ave'])
            last_std = float(avestdDict['last_std'])
            totaltime_devvalue = 50 + 10 * (totaltime - total_ave) / total_std
            lasttime_devvalue = 50 + 10 * (lasttime - last_ave) / last_std
            totaltime_dev_sum += totaltime_devvalue
            lasttime_dev_sum += lasttime_devvalue
            if totaltime_devvalue > totaltime_dev_max:
                totaltime_dev_max = totaltime_devvalue
            if lasttime_devvalue > lasttime_dev_max:
                lasttime_dev_max = lasttime_devvalue
            iter += 1
        if iter > 0:
            featuresDict['totaltime_dev_ave'] = round(totaltime_dev_sum / iter, 2)
            featuresDict['totaltime_dev_max'] = round(totaltime_dev_max, 2)
            featuresDict['lasttime_dev_ave'] = round(lasttime_dev_sum / iter, 2)
            featuresDict['lasttime_dev_max'] = round(lasttime_dev_max, 2)
        else:
            featuresDict['totaltime_dev_ave'] = ''
            featuresDict['totaltime_dev_max'] = ''
            featuresDict['lasttime_dev_ave'] = ''
            featuresDict['lasttime_dev_max'] = ''

        iter = 0
        corner_1st = 0
        corner_2nd = 0
        corner_3rd = 0
        corner_4th = 0
        for k in range(0, len(raceresults) - j):
            corner_1st += float(raceresults['1st_corner'][j+k])
            corner_2nd += float(raceresults['2nd_corner'][j+k])
            corner_3rd += float(raceresults['3rd_corner'][j+k])
            corner_4th += float(raceresults['4th_corner'][j+k])
            iter += 1
        if iter > 0:
            featuresDict['corner_1st'] = round(corner_1st / iter, 2)
            featuresDict['corner_2nd'] = round(corner_2nd / iter, 2)
            featuresDict['corner_3rd'] = round(corner_3rd / iter, 2)
            featuresDict['corner_4th'] = round(corner_4th / iter, 2)
        else:
            featuresDict['corner_1st'] = ''
            featuresDict['corner_2nd'] = ''
            featuresDict['corner_3rd'] = ''
            featuresDict['corner_4th'] = ''

        count_all = int(idDict['average']['count_all'])
        count_1 = int(idDict['average']['count_1'])
        count_2 = int(idDict['average']['count_2'])
        count_3 = int(idDict['average']['count_3'])
        winrate = round(float(100 * count_1 / count_all), 2)
        doublerate = round(float(100 * count_2 / count_all), 2)
        triplerate = round(float(100 * count_3 / count_all), 2)

        allrateDict = {
            'win': winrate,
            'double': doublerate,
            'triple': triplerate
        }

        whereDict = {
            'roadbed': roadbed_en,
            'distance': raceresults['distancecategory'][j-1],
            'course': raceresults['course'][j-1],
            'winclass': raceresults['winclass'][j-1],
            'sex': sex_en
        }

        targetDict = {
            'jockey': idDict['jockey'],
            'trainer': idDict['trainer'],
            'owner': idDict['owner'],
            'producer': idDict['producer'],
            'sire': idDict['sire']
        }

        for target in targetDict:
            code = raceresults[target + '_code'][j-1]

            for where in whereDict:
                key = str(code) + '_' + where + '_' + whereDict[where]
                rateDict = _rate(target, key, targetDict[target], allrateDict)

                for ratekey in rateDict:
                    featuresDict[target + '_' + where + '_' + ratekey] = rateDict[ratekey]

        belongs = raceresults['trainer_belongs'][j-1]
        if belongs == '東':
            featuresDict['trainerbelongs_east'] = '1'
        elif belongs == '西':
            featuresDict['trainerbelongs_west'] = '1'
        else:
            featuresDict['trainerbelongs_other'] = '1'

        sireline = raceresults['sireLine'][j-1]
        if sireline == '':
            featuresDict['sireline_others'] = '1'
        else:
            sireline = str(sireline)
            sireline = sireline.replace(' ', '')
            sireline = sireline.replace('’', '')
            sireline = sireline.replace('.', '')
            featuresDict['sireline_' + sireline] = '1'

        bmsline = raceresults['bmsLine'][j-1]
        if bmsline == '':
            featuresDict['bmsline_others'] = '1'
        else:
            bmsline = str(bmsline)
            bmsline = bmsline.replace(' ', '')
            bmsline = bmsline.replace('’', '')
            bmsline = bmsline.replace('.', '')
            featuresDict['bmsline_' + bmsline] = '1'

        valueDict = {}
        for feature in featuresDict:
            if feature in featuresList:
                valueDict[feature] = str(featuresDict[feature])

        sql = query._insert_from_Dict(tablename, valueDict)
        cur.execute(sql)
