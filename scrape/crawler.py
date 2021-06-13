# -*- coding: utf-8 -*-
# @Time : 2021/5/4
# @Author : Song yang Ji
# @File : crawler.py
# @Software: PyCharm

import store.storeInMongoDB as mongo

import time

from selenium.webdriver.support.select import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import requests

import threading
from multiprocessing import Process, Queue

leetcode_url = 'https://leetcode-cn.com'
problem_url = 'https://leetcode-cn.com/problems'


# 打开页面、加载数据
def open_page():
    """
    使用 selenium 自动化打开网页
    打开力扣的官网，然后加载出所有的题目索引行
    :return: 题目 uri 列表
    """
    url = 'https://leetcode-cn.com/problemset/all/'

    driver = webdriver.Chrome()
    driver.get(url)

    try:
        select_limit_page = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select.form-control'))
        )
    except Exception as e:
        print('加载超时 ', e)
        driver.quit()
        return

    # 点击全部，用来打开
    Select(select_limit_page).select_by_visible_text('全部')

    # 等所有的题目都加载完毕
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            '#question-app > div > div:nth-child(2) > div.question-list-base > div.table-responsive.question-list-table > table > tbody.reactable-data > tr:nth-child(2000)'))
        )
        tag = driver.find_element_by_css_selector('tbody.reactable-data')
    except Exception as e:
        print('加载超时 ', e)
        driver.quit()
        return

    uri_list = []

    problem_tag_list = tag.find_elements_by_tag_name('tr')

    # cnt = 0
    for tag in problem_tag_list:
        dct = parse_problem_row(tag)
        # 存储至 MongoDB
        if dct:
            mongo.insert_problem_brief_info(dct)
        uri_list.append(dct['uri'])
        # cnt = cnt + 1
        # print('解析第', cnt, '行数据')
        # 测试用
        # if True:
        #     break
    return uri_list


# 解析题目行
def parse_problem_row(tag):
    """
    根据tag对象提取其中的信息：题号、题名、题解数量、通过率、难度
    :param tag: Beautiful中的Tag对象
    :return: 字典  形如: {'id': '1720', 'name': '解码异或后的数组', 'uri': 'decode-xored-array', 'solutions': '376', 'passing_rate': '87.4%', 'difficult_level': '简单'}
    """

    res = {}

    # 解析题号
    id = tag.find_element_by_css_selector('td:nth-child(2)').text
    res['id'] = id

    # 解析题名、以及 problem-tag-name
    node = tag.find_element_by_css_selector('td:nth-child(3)').find_element_by_tag_name('a')
    name = node.text
    uri = node.get_attribute('href').split('/')[-1]
    res['name'] = name
    res['uri'] = uri

    # 解析题解数量
    solutions = tag.find_element_by_css_selector('td:nth-child(4)').text
    res['solutions'] = solutions

    # 解析通过率
    passing_rate = tag.find_element_by_css_selector('td:nth-child(5)').text
    res['passing_rate'] = passing_rate

    difficult_level = tag.find_element_by_css_selector('td:nth-child(6)').text
    res['difficult_level'] = difficult_level

    return res


# ajax请求数据
def crawling_problem_by_name(problem_name):
    """
    根据题目的名称爬取题目信息
    :param problem_name: 题目名称 (保证唯一)
    :return 是否请求成功
    """
    url = 'https://leetcode-cn.com/graphql/'

    graphql_str = '''
        {
          "operationName": "questionData",
          "variables": {
            "titleSlug": ""
          },
          "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    categoryTitle\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    envInfo\n    book {\n      id\n      bookName\n      pressName\n      source\n      shortDescription\n      fullDescription\n      bookImgUrl\n      pressImgUrl\n      productUrl\n      __typename\n    }\n    isSubscribed\n    isDailyQuestion\n    dailyRecordStatus\n    editorType\n    ugcQuestionId\n    style\n    exampleTestcases\n    __typename\n  }\n}\n"
        }
    '''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_3_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'Origin': leetcode_url,
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json'
    }

    data = json.loads(graphql_str, strict=False)
    data['variables']['titleSlug'] = problem_name
    # 这里不可以用键值对的方法传参，必须是json串
    data = json.dumps(data)

    try:
        response = requests.post(url, data=data, headers=headers, timeout=20)
    except Exception as e:
        print('request error: ', e)
        return False

    if response.status_code != 200:
        print('request failure')
        return False

    # 存储到MongoDB
    try:
        data_dict = json.loads(response.text, strict=False)
    except Exception as e:
        print('Json parse error :', e)
        return False

    mongo.insert_problem_raw_data(data_dict)
    return True


def main():
    begin = time.time()

    problem_names = open_page()

    print('需要爬取的题目数量:', len(problem_names))

    for problem_name in problem_names:
        crawling_problem_by_name(problem_name)

    end = time.time()
    print('爬虫结束,耗费时间为', (end - begin), '秒\n')


if __name__ == '__main__':
    main()
