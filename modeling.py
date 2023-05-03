# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.metrics import Precision
from tensorflow.keras.regularizers import l2

from lib import config
from lib import var2gl
from lib import manage_mysql
from lib import query

# from sqlalchemy import create_engine

var2gl._bet()


def main():

    # winclassList = ['debut', 'experienced']
    winclassList = ['debut']
    train_ratio = 0.8
    debutdropList = [
        'totaltime_dev_ave',
        'totaltime_dev_max',
        'lasttime_dev_ave',
        'lasttime_dev_max',
        'corner_1st',
        'corner_2nd',
        'corner_3rd',
        'corner_4th',
    ]

    con, cur = manage_mysql._connect()
    table = 'features'
    conditionDic = {}
    sql = query._select(table, conditionDic)
    original_df = pd.read_sql(sql, con)
    manage_mysql._end(con)

    # engine = create_engine('xxx')
    # alchemy_df = pd.read_sql_query(sql, engine)

    for winclass in winclassList:

        if winclass == 'debut':
            data_df = original_df.query('epoch_rotation == "0.0"')
            for debutdrop in debutdropList:
                data_df = data_df.drop(debutdrop, axis=1)
        else:
            data_df = original_df.query('epoch_rotation != "0.0"')

        data_df = data_df.astype(float)
        data_nd = data_df.to_numpy()

        train_size = int(train_ratio * data_nd.shape[0])

        np.random.seed(0)
        np.random.shuffle(data_nd)

        for rank in range(1, 4):
            print(winclass, rank + 1)

            # 0: horse code
            # 1: odds
            # 2: rank_1
            # 3: rank_2
            # 4: rank_3
            # 5-: features
            # horsecode = data_nd[:train_size, 0]
            train_x = data_nd[:train_size, 5:]
            train_y = data_nd[:train_size, rank + 1]
            # test_odds = data_nd[train_size:, 1]
            test_x = data_nd[train_size:, 5:]
            test_y = data_nd[train_size:, rank + 1]

            # モデルアーキテクチャの定義
            # 中間層
            #   ニューロンの数は`512`(元の変数の数`221`を考慮して設定)
            #   活性化関数は`Relu`
            # 出力層
            #   ニューロンの数は`1`
            #   活性化関数に`シグモイド関数`を設定し、その出力を「ターゲット変数の確率」と解釈する
            # 各層にドロップアウトを設定, L2ノルムを設定
            model = Sequential([
                Dense(
                    512,
                    kernel_regularizer=l2(0.01),
                    activation='relu',
                    input_dim=test_x.shape[1]
                    ),
                Dropout(0.2),
                Dense(
                    512,
                    kernel_regularizer=l2(0.01),
                    activation='relu'
                    ),
                Dropout(0.2),
                Dense(
                    512,
                    kernel_regularizer=l2(0.01),
                    activation='relu'
                    ),
                Dropout(0.2),
                Dense(
                    1,
                    activation='sigmoid'
                    ),
            ])

            # 学習のためのモデルの定義
            # 損失関数は`交差エントロピー誤差`
            # 最適化手法は`RMSprop`
            # 評価関数は`適合率`(予測がPositiveと判断した時の、判断の精度を高めたいため)
            model.compile(
                loss='binary_crossentropy',
                optimizer='rmsprop',
                metrics=[Precision()],
                )

            epoch = 10
            fit = model.fit(
                train_x,
                train_y,
                validation_data=(test_x, test_y),
                epochs=epoch,
                batch_size=32,
                )
            model.save(config.path_model + 'rank_' + str(rank) + '_' + winclass)

            # drawing
            plt.plot(fit.history['loss'])
            plt.plot(fit.history['val_loss'])
            plt.ylabel('Binary Crossentropy')
            plt.xlabel('Epoch')
            plt.legend(['Train', 'Test'], loc='upper right')
            plt.show()


if __name__ == '__main__':

    main()
