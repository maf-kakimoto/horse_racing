# -*- coding: utf-8 -*-

import re
from lib import load_yaml


def _basicinfo(soup, raceID):

    raceinfo = {
        'year': raceID['year'],
        'holding': raceID['date'],
        'courseNum': raceID['courseNum'],
        'No': raceID['No']
        }

    title = soup.select_one('title')
    title = title.text
    title = title.translate(str.maketrans({'｜': ',', '|': ',', ' ': None}))
    title = title.split(',')
    name = title[0]
    raceinfo['raceName'] = name

    if '障害' in raceinfo['raceName'] or 'ジャンプ' in raceinfo['raceName']:
        raceinfo['jump_flg'] = '1'

    else:
        raceinfo['jump_flg'] = '0'

        date_tmp = title[1].translate(str.maketrans({'年': '-', '月': '-', '日': None}))
        dateList = date_tmp.split('-')
        date = dateList[0]
        date += '-' + str('{0:02d}'.format(int(dateList[1])))
        date += '-' + str('{0:02d}'.format(int(dateList[2])))
        raceinfo['date'] = date

        basic_data = soup.select_one('.racedata')
        basic_data = basic_data.span.text
        basic_data = basic_data.translate(str.maketrans({'\xa0': '', ' ': ''}))
        basic_data = basic_data.split('/')
        road = basic_data[0][0]
        roadDic = load_yaml._load_yaml('./setting/roadbed_ja.yml')
        raceinfo['road'] = roadDic[road]

        distance = basic_data[0]
        distance = re.sub('内2周', '', distance)
        raceinfo['distance'] = re.sub('\\D', '', distance)

        if '外' in basic_data[0]:
            raceinfo['outFlg'] = '1'
        else:
            raceinfo['outFlg'] = '0'

        condition = basic_data[2].split(':')[1]
        conditionDic = load_yaml._load_yaml('./setting/condition_ja.yml')
        raceinfo['condition'] = conditionDic[condition]

        weather = basic_data[1].split(':')[1]
        weatherDic = load_yaml._load_yaml('./setting/weather.yml')
        raceinfo['weather'] = weatherDic[weather]

        detail_data = soup.select_one('.smalltxt')
        detail_data = detail_data.text

        ageDic = load_yaml._load_yaml('./setting/ageclass_ja.yml')
        for key in ageDic:
            if key in detail_data:
                raceinfo['age'] = ageDic[key]
                break

        classDic = load_yaml._load_yaml('./setting/winclass.yml')
        for key in classDic:
            if key in detail_data:
                raceinfo['class'] = classDic[key]
                break

        loafDic = load_yaml._load_yaml('./setting/loafclass.yml')
        for key in loafDic:
            if key in detail_data:
                raceinfo['loaf'] = loafDic[key]
                break

        sexDic = load_yaml._load_yaml('./setting/sexclass_ja.yml')
        raceinfo['sex'] = '9'
        for key in sexDic:
            if key in detail_data:
                raceinfo['sex'] = sexDic[key]
                break

        rank = soup.select('a[href^="/horse/"]')
        raceinfo['number'] = str(len(rank))

    return raceinfo
