# -*- coding: utf-8 -*-
# @Time : 2021/7/9
# @Author : Song yang Ji
# @File : analyze.py
# @Software: PyCharm

from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

client = MongoClient()
db = client.leetcode

c1 = db.problems_brief_information
c2 = db.problems_raw


def getDataFrameFromProblems_brief_information():
    data_model = c1.find_one()
    df = pd.DataFrame(columns=list(data_model))
    ls = []
    for p in c1.find():
        ls.append(p)
    df = df.append(ls, ignore_index=True)
    return df


def analyzeDataFrame(df):
    df = df.groupby('difficult_level')['_id'].count()
    df = pd.DataFrame(df.values, columns=['数量'], index=df.index)
    print(df)
    df.plot(kind='bar')
    plt.show()
    pass


if __name__ == '__main__':
    df = getDataFrameFromProblems_brief_information()
    analyzeDataFrame(df)
