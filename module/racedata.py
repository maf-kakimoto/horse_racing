# -*- coding: utf-8 -*-

import yaml
import re
from bs4 import BeautifulSoup
from lib import load_yaml


def _horselist(soup, raceinfo, out):

    columnList = load_yaml._load_yaml('./setting/resultfile.yml')
    header = ','.join(columnList)
    header += '\n'
    out.write(header)

    payout = soup.select_one('.pay_table_01')
    payout = payout.select('.txt_r')
    tansho = payout[0].text
    tansho = re.sub(r',', '', tansho)
    fukushoStr = str(payout[2])
    fukushoStr = re.sub(r',', '', fukushoStr)
    fukushoList = []
    fukushoList = fukushoStr.split('<br/>')
    for i in range(len(fukushoList)):
        fukushoList[i] = re.sub(r'\D', '', fukushoList[i])

    horseinfoList = soup.select_one('.race_table_01')
    horseinfoList = re.sub(r',', '', str(horseinfoList))
    horseinfoList = re.sub(r'</tr>', ',', str(horseinfoList))
    horseinfoList = horseinfoList.split(',')

    i = 0
    winner_time = 0
    for horseinfo in horseinfoList:

        horseinfoDict = {}
        if i != 0 and i <= int(raceinfo['number']):
            horseinfo = BeautifulSoup(horseinfo, 'lxml')
            txt_r = horseinfo.select('.txt_r')
            txt_r_list = []
            for txt_r_item in txt_r:
                txt_r_list.append(txt_r_item.text)
            horseinfoDict['rank'] = txt_r_list[0]
            horseinfoDict['gate'] = txt_r_list[1]
            if txt_r_list[2] != '':
                time = txt_r_list[2].split(':')
                horseinfoDict['time'] = str(float(time[0]) * 60 + float(time[1]))
                if i == 1:
                    winner_time = float(horseinfoDict['time'])
                horseinfoDict['diff'] = str(round(float(horseinfoDict['time']) - winner_time, 1))
            else:
                horseinfoDict['time'] = '-'
                horseinfoDict['diff'] = '-'
            horseinfoDict['odds'] = txt_r_list[3]
            horseinfoDict['prize'] = txt_r_list[4]
            if horseinfoDict['prize'] == '':
                horseinfoDict['prize'] = '0'

            horse = horseinfo.select_one('a[href^="/horse/"]')
            horseinfoDict['horseName'] = horse.text
            horse_code = horse.attrs['href']
            horseinfoDict['horse_code'] = horse_code.split('/')[2]

            txt_c = horseinfo.select('.txt_c')
            txt_c_list = []
            for txt_c_item in txt_c:
                txt_c_list.append(txt_c_item.text)
            sex = txt_c_list[0][0]
            horseinfoDict['sex'] = sex
            horseinfoDict['age'] = txt_c_list[0][1:]
            horseinfoDict['loaf'] = txt_c_list[1]

            jockey = horseinfo.select_one('a[href^="/jockey/"]')
            horseinfoDict['jockey'] = jockey.text
            jockey_code = jockey.attrs['href']
            jockeycodeList = jockey_code.split('/')
            if len(jockeycodeList) == 4:
                pointer = 2
            elif len(jockeycodeList) == 6:
                pointer = 4
            horseinfoDict['jockey_code'] = jockeycodeList[pointer]

            r1ml = horseinfo.select('.r1ml')
            r2ml = horseinfo.select('.r2ml')
            r3ml = horseinfo.select('.r3ml')
            bml = horseinfo.select('.bml')
            if len(r1ml) > 0:
                for ml_item in r1ml:
                    if len(ml_item.text) == 4:
                        horseinfoDict['last'] = ml_item.text
                        horseinfoDict['last_rank'] = '1'
                    elif len(ml_item.text) < 3:
                        horseinfoDict['popularity'] = ml_item.text
            if len(r2ml) > 0:
                for ml_item in r2ml:
                    if len(ml_item.text) == 4:
                        horseinfoDict['last'] = ml_item.text
                        horseinfoDict['last_rank'] = '2'
                    elif len(ml_item.text) < 3:
                        horseinfoDict['popularity'] = ml_item.text
            if len(r3ml) > 0:
                for ml_item in r3ml:
                    if len(ml_item.text) == 4:
                        horseinfoDict['last'] = ml_item.text
                        horseinfoDict['last_rank'] = '3'
                    elif len(ml_item.text) < 3:
                        horseinfoDict['popularity'] = ml_item.text
            if len(bml) > 0:
                for ml_item in bml:
                    if len(ml_item.text) == 4:
                        horseinfoDict['last'] = ml_item.text
                        horseinfoDict['last_rank'] = '-'
                    elif len(ml_item.text) < 3 and ml_item.text != '\n':
                        horseinfoDict['popularity'] = ml_item.text
            if 'last' not in horseinfoDict or 'last_rank' not in horseinfoDict:
                horseinfoDict['last'] = '-'
                horseinfoDict['last_rank'] = '-'

            td = horseinfo.select('td')
            if td[10].text == '':
                horseinfoDict['corner'] = '-'
            else:
                horseinfoDict['corner'] = td[10].text
            weight = td[14].text.translate(str.maketrans({'(': ',', ')': ''}))
            weightList = []
            weightList = weight.split(',')
            if len(weightList) == 2:
                horseinfoDict['weight'] = weightList[0]
                horseinfoDict['weightDiff'] = weightList[1]
            else:
                horseinfoDict['weight'] = '-'
                horseinfoDict['weightDiff'] = '-'

            trainer = horseinfo.select_one('a[href^="/trainer/"]')
            horseinfoDict['trainer'] = trainer.text
            trainer_code = trainer.attrs['href']
            trainercodeList = trainer_code.split('/')
            if len(trainercodeList) == 4:
                pointer = 2
            elif len(trainercodeList) == 6:
                pointer = 4
            horseinfoDict['trainer_code'] = trainercodeList[pointer]

            txt_l = horseinfo.select('.txt_l')
            if '[東]' in txt_l[2].text:
                belongs = '東'
            elif '[西]' in txt_l[2].text:
                belongs = '西'
            else:
                belongs = '他'
            horseinfoDict['belongs'] = belongs

            owner = horseinfo.select_one('a[href^="/owner/"]')
            horseinfoDict['owner'] = owner.text
            owner_code = owner.attrs['href']
            ownercodeList = owner_code.split('/')
            if len(ownercodeList) == 4:
                pointer = 2
            elif len(ownercodeList) == 6:
                pointer = 4
            horseinfoDict['owner_code'] = ownercodeList[pointer]

            if horseinfoDict['rank'] == '1':
                horseinfoDict['tansho'] = tansho
            else:
                horseinfoDict['tansho'] = '0'

            if horseinfoDict['rank'] == '1':
                horseinfoDict['fukusho'] = fukushoList[0]
            elif horseinfoDict['rank'] == '2' and len(fukushoList) > 1:
                horseinfoDict['fukusho'] = fukushoList[1]
            elif horseinfoDict['rank'] == '3' and len(fukushoList) > 2:
                horseinfoDict['fukusho'] = fukushoList[2]
            else:
                horseinfoDict['fukusho'] = '0'

            resultList = []
            for key in columnList:
                resultList.append(horseinfoDict[key])

            result = ','.join(resultList)
            result += '\n'
            out.write(result)

        i += 1


def _refund(soup, out):

    refund = soup.select_one('.pay_block')
    refund_tr_list = refund.select('tr')

    refundDict = {
        'tan': 0,
        'fuku': 0,
        'waku': 0,
        'uren': 0,
        'wide': 0,
        'utan': 0,
        'sanfuku': 0,
        'santan': 0
    }

    refundallList = []
    for refund_tr in refund_tr_list:
        refund_th = refund_tr.select_one('th')
        refund_class = refund_th['class'][0]
        refund_td_list = refund_tr.select('td')
        for refund_td in refund_td_list:
            refundStr = str(refund_td)
            refundStr = re.sub(r',', '', refundStr)
            refundList = []
            refundList = refundStr.split('<br/>')
            refundDict[refund_class] = len(refundList)
            for i in range(len(refundList)):
                refundList[i] = re.sub('[a-z<>"=_/ ]', '', refundList[i])
                refundList[i] = re.sub('→', '=', refundList[i])
                refundallList.append(refundList[i])

    pointer_start = 0
    pointer_end = 0
    refunddataDict = {}
    for key in refundDict:
        refunddetailDict = {}
        # refunddetailList = []
        pointer_end += refundDict[key] * 3
        targetList = refundallList[pointer_start:pointer_end]

        if refundDict[key] == 3:
            refunddetailDict['number'] = ','.join(targetList[0:3])
            refunddetailDict['pay'] = ','.join(targetList[3:6])
            refunddetailDict['popularity'] = ','.join(targetList[6:9])
        elif refundDict[key] == 2:
            refunddetailDict['number'] = ','.join(targetList[0:2])
            refunddetailDict['pay'] = ','.join(targetList[2:4])
            refunddetailDict['popularity'] = ','.join(targetList[4:6])
        elif refundDict[key] == 1:
            refunddetailDict['number'] = targetList[0]
            refunddetailDict['pay'] = targetList[1]
            refunddetailDict['popularity'] = targetList[2]

        if 'number' in refunddetailDict:
            number = refunddetailDict['number']
            combiList = number.split(',')

            number_tmp = ''
            for combi in combiList:
                if '-' in combi:
                    gateList = combi.split('-')
                    gate_tmp = ''
                    for gateitem in gateList:
                        gate = str('{0:02d}'.format(int(gateitem)))
                        gate_tmp += gate + '-'
                    gate_tmp = gate_tmp[:-1]
                elif '=' in combi:
                    gateList = combi.split('=')
                    gate_tmp = ''
                    for gateitem in gateList:
                        gate = str('{0:02d}'.format(int(gateitem)))
                        gate_tmp += gate + '='
                    gate_tmp = gate_tmp[:-1]
                elif ',' in combi:
                    gateList = combi.split(',')
                    gate_tmp = ''
                    for gateitem in gateList:
                        gate = str('{0:02d}'.format(int(gateitem)))
                        gate_tmp += gate + ','
                    gate_tmp = gate_tmp[:-1]
                else:
                    gate_tmp = str('{0:02d}'.format(int(combi)))

                number_tmp += gate_tmp + ','

            refunddetailDict['number'] = number_tmp[:-1]

        refunddataDict[key] = refunddetailDict
        pointer_start = pointer_end

    refundYaml = yaml.dump(refunddataDict)
    out.write(str(refundYaml))
