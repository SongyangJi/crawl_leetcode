# -*- coding: utf-8 -*-
# @Time : 2021/5/4
# @Author : Song yang Ji
# @File : down_image.py
# @Software: PyCharm

from PIL import Image
from io import BytesIO
import re
import requests
import logging

"""
正则匹配模式
"""
pattern = re.compile(r'(https|http)://.*\.(jpg|gif|jpeg|png)')


def download_image(img_url, img_name=""):
    """
    :param img_url: 传入的url, 形如 https://xxxxxx.jpg 等
    :param img_name: 下载的图片
    :return: 是否下载成功
    """
    if pattern.search(img_url) is None:
        return False
    else:
        img_url = pattern.search(img_url).group()

    if len(img_name) == 0:
        filename = img_url.split(r"//", 1)[1]
        filename = filename.replace("/", "_")
    else:
        filename = img_name
    # 请求数据
    res = requests.get(img_url, stream=True)
    # 二进制输出流
    try:
        with open(filename, "wb") as f:
            f.write(res.content)
    except IOError:
        print('down image error')
        return False
    return True


def change_webp_to_jpg(webp_content):
    """
    将webp图片格式转换为jpg格式
    :param webp_content: webp图片字节流
    :return: jpg图片字节流
    """
    jpg_content = ""
    try:
        if webp_content.upper().startswith(b"RIF"):
            im = Image.open(BytesIO(webp_content))
            if im.mode == "RGBA":
                im.load()
                background = Image.new("RGB", im.size, (255, 255, 255))
                background.paste(im, mask=im.split()[3])
                im = background
            img_byte = BytesIO()
            im.save(img_byte, format='JPEG')
            jpg_content = img_byte.getvalue()
    except Exception as err:
        logging.error(err)
    return jpg_content if jpg_content else webp_content


if __name__ == '__main__':
    s = "https://assets.leetcode-cn.com/aliyun-lc-upload/users/mian-bi-zhe-5/avatar_1567341249.png?x-oss-process=image%2Fresize%2Ch_160%2Cw_160"
    print(download_image(s))
