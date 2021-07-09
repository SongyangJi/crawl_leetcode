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


def getData():
    ls = []
    for p in c1.find():
        ls.append(p)
    return ls


def getDataFrameFromProblems_brief_information():
    data_model = c1.find_one()
    df = pd.DataFrame(columns=list(data_model))
    df = df.append(getData(), ignore_index=True)
    return df


def analyzeLevel_Num(df):
    df = df.groupby('difficult_level')['_id'].count()
    df = pd.DataFrame(df.values, columns=['数量'], index=df.index)
    df.plot(kind='bar')
    plt.show()
    pass


def analyzeSolutions_Rate():
    data = getData()
    df = pd.DataFrame({'通过率': [float(it['passing_rate'][:-1]) / 100 for it in data]},
                      index=[it['solutions'] for it in data])
    print(df)
    df.sort_index().plot()
    plt.show()
    pass


def analyzeLevel_Rate(df):
    df['passing_rate'] = df['passing_rate'].map(lambda x: float(x[:-1]) / 100)
    df = df.groupby('difficult_level')['passing_rate'].mean()
    df = pd.DataFrame(df.values, columns=['平均通过率'], index=df.index)
    df.sort_values(by='平均通过率',inplace=True,ascending=False)
    df.plot(kind='bar')
    plt.show()
    pass


if __name__ == '__main__':
    df = getDataFrameFromProblems_brief_information()
    # analyzeLevel_Num(df)
    # analyzeSolutions_Rate()
    analyzeLevel_Rate(df)
