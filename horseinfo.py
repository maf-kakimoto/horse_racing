# -*- coding: utf-8 -*-

import re
import time
import sys
from lib import manage_mysql
from lib import bs
from lib import urlquery
from lib import query


def main(page, settingDict):

    base = 'xxx'
    paramsDic = {
        'search_string': '',
        'category': 'horse',
        'detail': '1',
        'age_from': str(settingDict['ageFrom']),
        'age_to': str(settingDict['ageTo']),
        'sort_list': '1',
        'horse': '0',
        'page': str(page)
    }
    url = urlquery._multiparams(base, paramsDic)
    soup = bs._soup(url)
    horses = soup.find_all('a', href=re.compile('/horse/'))

    if len(horses) == 0:
        print('!!! end of search !!!')
        sys.exit()

    horseNameList = []
    horseCodeList = []
    for item in horses:
        horseNameList.append(item.text)
        horse_code = item.attrs['href']
        horseCodeList.append(horse_code.split('/')[3])
    sexAge = soup.select('.age')
    sexList = []
    ageList = []
    for item in sexAge:
        if item.text != '性齢':
            sexList.append(item.text[0])
            ageList.append(item.text[1:])

    father = soup.select('td[class="father"]')
    fatherList = []
    fatherCodeList = []
    for item in father:
        fatherList.append(item.text.replace('\n', ''))
        if item.a is not None:
            fatherCode = item.a.attrs['href']
            fatherCode = fatherCode.split('/')
            fatherCodeList.append(fatherCode[3])
        else:
            fatherCodeList.append('')
    fatherLine = soup.select('.fline')
    fatherLineList = []
    for item in fatherLine:
        if item.text != '父系':
            fatherLineList.append(item.text)

    mother = soup.select('.mother')
    motherList = []
    for item in mother:
        item = item.text.replace('\n', '')
        if item != '母':
            motherList.append(item)

    bmsLine = soup.select('.mondad')
    bmsList = []
    bmsLineList = []
    i = 0
    for item in bmsLine:
        item = item.text.replace('\n', '')
        if i % 2 == 0:
            bmsList.append(item)
        else:
            bmsLineList.append(item)
        i += 1
    bms = soup.select('td[class="mondad"]')
    bmsCodeList = []
    for item in bms:
        if item.a is not None:
            bmsCode = item.a.attrs['href']
            bmsCode = bmsCode.split('/')
            bmsCodeList.append(bmsCode[3])
        else:
            bmsCodeList.append('')

    trainer = soup.select('.trainer')
    trainerList = []
    trainerCodeList = []
    for item in trainer:
        trainerList.append(item.text.replace('\n', ''))
        trainerCode = item.a.attrs['href']
        trainerCode = trainerCode.split('/')
        trainerCodeList.append(trainerCode[3])

    owner = soup.select('.owner')
    ownerList = []
    ownerCodeList = []
    for item in owner:
        if item.text != '馬主':
            ownerList.append(item.text.replace('\n', ''))
            ownerCode = item.a.attrs['href']
            ownerCode = ownerCode.split('/')
            ownerCodeList.append(ownerCode[3])

    producer = soup.select('.producer')
    producerList = []
    producerCodeList = []
    for item in producer:
        if item.text != '生産者':
            producerList.append(item.text.replace('\n', ''))
            producerCode = item.a.attrs['href']
            producerCode = producerCode.split('/')
            producerCodeList.append(producerCode[3])

    for i in range(len(horseNameList)):

        con, cur = manage_mysql._connect()
        table = 'horseInfo'
        conditionDic = {'horse_code': horseCodeList[i]}
        slct_all = query._select(table, conditionDic)
        cur.execute(slct_all)
        result = cur.fetchall()
        if len(result) == 0:
            print(horseNameList[i])
            valueDic = {
                'name': horseNameList[i],
                'horse_code': horseCodeList[i],
                'sex': sexList[i],
                'birth': str(settingDict['year'] - int(ageList[i])),
                'sire': fatherList[i],
                'sire_code': fatherCodeList[i],
                'sireLine': fatherLineList[i],
                'mother': motherList[i],
                'bms': bmsList[i],
                'bms_code': bmsCodeList[i],
                'bmsLine': bmsLineList[i],
                'trainer': trainerList[i],
                'trainer_code': trainerCodeList[i],
                'owner': ownerList[i],
                'owner_code': ownerCodeList[i],
                'producer': producerList[i],
                'producer_code': producerCodeList[i]
            }
            insert_all = query._insert_from_Dict(table, valueDic)
            cur.execute(insert_all)
        manage_mysql._end(con)


if __name__ == '__main__':

    settingDict = {
        'year': int(sys.argv[1]),
        'ageFrom': int(sys.argv[2]),
        'ageTo': int(sys.argv[3]),
    }

    for i in range(1000):
        print(i + 1)
        main(i + 1, settingDict)
        time.sleep(2)
