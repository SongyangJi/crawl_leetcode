# -*- coding: utf-8 -*-
# @Time : 2021/5/7
# @Author : Song yang Ji
# @File : storeInMongoDB.py
# @Software: PyCharm

from pymongo import MongoClient

client = MongoClient()
db = client.leetcode

c1 = db.problems_brief_information

c2 = db.problems_raw


def insert_problem_brief_info(doc):
    c1.insert_one(doc)


def insert_problem_raw_data(doc):
    c2.insert_one(doc)
