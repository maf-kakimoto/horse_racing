# -*- coding: utf-8 -*-

def _corner(corner, number):

    corner_list = corner.split('-')
    cornerDic = {}

    max = 100

    if len(corner_list) > 0 and corner_list[0] != '':
        corner = max * int(corner_list[0]) / int(number)
        cornerDic['1st_corner'] = str(round(corner, 2))
    else:
        cornerDic['1st_corner'] = '50'

    if len(corner_list) > 1 and corner_list[1] != '':
        corner = max * int(corner_list[1]) / int(number)
        cornerDic['2nd_corner'] = str(round(corner, 2))
    else:
        cornerDic['2nd_corner'] = cornerDic['1st_corner']

    if len(corner_list) > 2 and corner_list[2] != '':
        corner = max * int(corner_list[2]) / int(number)
        cornerDic['3rd_corner'] = str(round(corner, 2))
    else:
        cornerDic['3rd_corner'] = cornerDic['2nd_corner']

    if len(corner_list) > 3 and corner_list[3] != '':
        corner = max * int(corner_list[3]) / int(number)
        cornerDic['4th_corner'] = str(round(corner, 2))
    else:
        cornerDic['4th_corner'] = cornerDic['3rd_corner']

    return cornerDic
