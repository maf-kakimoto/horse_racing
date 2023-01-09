# -*- coding: utf-8 -*-

import codecs
import time
import os
from lib import bs
from lib import load_yaml
from module import basicinfo
from module import racedata
from module import odds


def makeFiles(raceid):

    path = './races/'
    path += raceid['courseNum'] + '/'
    path += raceid['year'] + '/'
    path += raceid['date'] + '/'

    if not os.path.exists(path):
        os.makedirs(path)

    racekey = raceid['year']
    racekey += raceid['courseNum']
    racekey += raceid['date']
    racekey += raceid['No']

    url = 'https://db.netkeiba.com/race/' + racekey + '/'
    soup_download = bs._soup(url)
    out = codecs.open(path + racekey + '_soup.html', 'w', 'utf-8')
    out.write(str(soup_download))
    out.close()
    time.sleep(2)

    soup = bs.BeautifulSoup(open(path + racekey + '_soup.html'), 'html.parser')

    title = soup.select_one('title')

    if title is not None:

        raceinfo = basicinfo._basicinfo(soup, raceid)

        if raceinfo['jump_flg'] == '0':

            fileName = racekey + '_'
            fileName += raceinfo['road'] + '_'
            fileName += raceinfo['distance'] + '_'
            fileName += raceinfo['outFlg'] + '_'
            fileName += raceinfo['condition'] + '_'
            fileName += raceinfo['age'] + '_'
            fileName += raceinfo['class'] + '_'
            fileName += raceinfo['sex'] + '_'
            fileName += raceinfo['loaf'] + '_'
            fileName += raceinfo['number'] + '_'
            fileName += raceinfo['weather'] + '_'
            fileName += raceinfo['date']

            print(path, raceid['No'])

            out_horselist = codecs.open(path + fileName + '.csv', 'w', 'utf-8')
            racedata._horselist(soup, raceinfo, out_horselist)
            out_horselist.close()

            out_refund = codecs.open(path + racekey + '_refund.yml', 'w', 'utf-8')
            racedata._refund(soup, out_refund)
            out_refund.close()


if __name__ == '__main__':

    holdingsDict = load_yaml._load_yaml('./setting/holdings_sampling.yml')

    for course in holdingsDict:
        yearDic = holdingsDict[course]['year']
        for year in yearDic:
            timeDic = yearDic[year]
            if type(timeDic) is dict:
                for times in timeDic:
                    days = timeDic[times]
                    if ',' in str(days):
                        dayList = days.split(',')
                        day_from = int(dayList[0]) - 1
                        day_to = int(dayList[1])
                    else:
                        day_from = 0
                        day_to = days
                    for day in range(day_from, day_to):
                        racedate = str('{0:02d}'.format(times)) + str('{0:02d}'.format(day+1))
                        for race in range(12):
                            raceno = str('{0:02d}'.format(race+1))
                            raceid = {
                                'courseNum': course,
                                'year': str(year),
                                'date': racedate,
                                'No': raceno
                                }
                            print(raceid)
                            makeFiles(raceid)
                            odds._odds(raceid)
