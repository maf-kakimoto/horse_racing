# -*- coding: utf-8 -*-

import re
import yaml
import time
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from lib import webdriver


def _loadnumber(driver, path, racekey, typekey):

    typeDict = {
        'tanfuku': 'b1',
        'wakuren': 'b3',
        'umaren': 'b4',
        'wide': 'b5',
        'umatan': 'b6',
        'sanfuku': 'b7',
        'santan': 'b8',
    }

    url = 'https://race.netkeiba.com/odds/index.html'
    url += '?type=' + typeDict[typekey]
    url += '&race_id=' + racekey
    url += '&rf=shutuba_submenu'
    driver.get(url)
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    racedata02 = soup.select_one('.RaceData02')
    racedata02_span = racedata02.select('span')
    number = re.sub(r'頭', '', racedata02_span[7].text)
    number = int(number)

    return soup, number


def _tanfuku(driver, path, racekey):

    soup, number = _loadnumber(driver, path, racekey, 'tanfuku')

    tanshoDict = {}
    fukushoDict = {}
    for i in range(1, number+1):
        gate = str('{0:02d}'.format(i))
        tansho_odds = soup.select_one('#odds-1_' + gate)
        fukusho_odds = soup.select_one('#odds-2_' + gate)
        if tansho_odds is not None and tansho_odds != '除外':
            tanshoDict['tan_' + gate] = tansho_odds.text
            fukushoDict['fuku_' + gate] = fukusho_odds.text

    tanshoDict.update(fukushoDict)
    tanfukuDict = tanshoDict.copy()

    return tanfukuDict


def _wakuren(driver, path, racekey):

    soup, number = _loadnumber(driver, path, racekey, 'wakuren')

    wakurenDict = {}
    for i in range(1, 9):
        waku1 = str('{0:02d}'.format(i))
        for j in range(i, 9):
            waku2 = str('{0:02d}'.format(j))
            odds = soup.select_one('#odds-3-' + waku1 + waku2)
            if odds is not None and odds != '除外':
                wakurenDict['wakuren_' + waku1 + '-' + waku2] = odds.text

    return wakurenDict


def _umaren(driver, path, racekey):

    soup, number = _loadnumber(driver, path, racekey, 'umaren')

    umarenDict = {}
    for i in range(1, number):
        gate1 = str('{0:02d}'.format(i))
        for j in range(i+1, number+1):
            gate2 = str('{0:02d}'.format(j))
            odds = soup.select_one('#odds-4-' + gate1 + gate2)
            if odds is not None and odds != '除外':
                umarenDict['umaren_' + gate1 + '-' + gate2] = odds.text

    return umarenDict


def _wide(driver, path, racekey):

    soup, number = _loadnumber(driver, path, racekey, 'wide')

    wideDict = {}
    for i in range(1, number):
        gate1 = str('{0:02d}'.format(i))
        for j in range(i+1, number+1):
            gate2 = str('{0:02d}'.format(j))
            odds_max = soup.select_one('#odds-5-' + gate1 + gate2)
            odds_min = soup.select_one('#oddsmin-5-' + gate1 + gate2)
            if odds_max is not None and odds_max != '除外':
                wideDict['wide_' + gate1 + '-' + gate2] = odds_max.text + ' - ' + odds_min.text

    return wideDict


def _umatan(driver, path, racekey):

    soup, number = _loadnumber(driver, path, racekey, 'umatan')

    umatanDict = {}
    for i in range(1, number+1):
        gate1 = str('{0:02d}'.format(i))
        for j in range(1, number+1):
            if i != j:
                gate2 = str('{0:02d}'.format(j))
                odds = soup.select_one('#odds-6-' + gate1 + gate2)
                if odds is not None and odds != '除外':
                    umatanDict['umatan_' + gate1 + '-' + gate2] = odds.text

    return umatanDict


def _sanfuku(driver, path, racekey):

    soup, number = _loadnumber(driver, path, racekey, 'sanfuku')

    sanfukuDict = {}
    for i in range(1, number-1):
        xpath = '/html/body/div[1]/div[3]/div[2]/div[1]/div[3]/div[1]/div/div/div/select'
        select_box = driver.find_element(By.XPATH, xpath)
        select = Select(select_box)
        select.select_by_index(i)
        time.sleep(2)

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        gate1 = str('{0:02d}'.format(i))
        for j in range(i+1, number):
            gate2 = str('{0:02d}'.format(j))
            for k in range(j+1, number+1):
                gate3 = str('{0:02d}'.format(k))
                odds = soup.select_one('#odds-7-' + gate1 + gate2 + gate3)
                if odds is not None and odds != '除外':
                    sanfukuDict['sanfuku_' + gate1 + '-' + gate2 + '-' + gate3] = odds.text

    return sanfukuDict


def _santan(driver, path, racekey):

    soup, number = _loadnumber(driver, path, racekey, 'santan')

    santanDict = {}
    for i in range(1, number+1):
        # xpath = '/html/body/div[1]/div[4]/div[2]/div[1]/div[3]/div[1]/div/div/div/select'
        xpath = '/html/body/div[1]/div[3]/div[2]/div[1]/div[3]/div[1]/div/div/div/select'
        select_box = driver.find_element(By.XPATH, xpath)
        select = Select(select_box)
        select.select_by_index(i)
        time.sleep(2)

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        gate1 = str('{0:02d}'.format(i))
        for j in range(1, number+1):
            gate2 = str('{0:02d}'.format(j))
            for k in range(1, number+1):
                if i != j and i != k and j != k:
                    gate3 = str('{0:02d}'.format(k))
                    odds = soup.select_one('#odds-8-' + gate1 + gate2 + gate3)
                    if odds is not None and odds != '除外':
                        santanDict['santan_' + gate1 + '-' + gate2 + '-' + gate3] = odds.text

    return santanDict


def _odds(raceid):

    path = raceid['courseNum'] + '/'
    path += raceid['year'] + '/'
    path += raceid['date'] + '/'
    racekey = raceid['year']
    racekey += raceid['courseNum']
    racekey += raceid['date']
    racekey += raceid['No']

    headless = True
    # headless = False
    driver = webdriver._webdriver(headless)

    oddsDict = {}
    oddsDict.update(_tanfuku(driver, path, racekey))
    oddsDict.update(_wakuren(driver, path, racekey))
    oddsDict.update(_umaren(driver, path, racekey))
    oddsDict.update(_wide(driver, path, racekey))
    oddsDict.update(_umatan(driver, path, racekey))
    oddsDict.update(_sanfuku(driver, path, racekey))
    oddsDict.update(_santan(driver, path, racekey))

    with open('./races/' + path + racekey + '_odds.yml', 'w') as f:
        yaml.dump(oddsDict, f)

    driver.quit()
