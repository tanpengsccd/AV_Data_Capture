#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
import re
from ADC_function import *
from core import *
from ConfigApp import *
import json
import shutil
import argparse
from pathlib import Path
from operator import itemgetter
from itertools import groupby
import pandas as pd




config = ConfigApp()

patern_of_file_name_sufixes = r'.(mp4|avi|rmvb|wmv|mov|mkv|flv|ts|m2ts)$'


def UpdateCheck(version):
    if UpdateCheckSwitch() == '1':
        html2 = get_html('https://raw.githubusercontent.com/yoshiko2/AV_Data_Capture/master/update_check.json')
        html = json.loads(str(html2))

        if not version == html['version']:
            print('[*]                  * New update ' + html['version'] + ' *')
            print('[*]                     ↓ Download ↓')
            print('[*] ' + html['download'])
            print('[*]======================================================')
    else:
        print('[+]Update Check disabled!')


def argparse_get_file():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", default='', nargs='?', help="Write the file path on here")
    args = parser.parse_args()
    if args.file == '':
        return ''
    else:
        return args.file


def movie_lists(escape_folders):
    escape_folders = re.split('[,，]', escape_folders)
    total = []

    for root, dirs, files in os.walk(config.search_folder):
        if root in escape_folders:
            continue
        for file in files:
            if re.search(patern_of_file_name_sufixes, file, re.IGNORECASE):
                path = os.path.join(root, file)
                total.append(path)
    return total


def CreatFailedFolder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            os._exit(0)


# def CEF(path):
#     try:
#         files = os.listdir(path)  # 获取路径下的子文件(夹)列表
#         for file in files:
#             os.removedirs(path + '/' + file)  # 删除这个空文件夹
#             print('[+]Deleting empty folder', path + '/' + file)
#     except:
#         a = ''
#

# 获取番号，集数
def getNumber(filepath, absolute_path=False):
    name = filepath
    if absolute_path:
        name = name.replace('\\', '/')
    # 移除文件类型后缀
    name = re.sub(patern_of_file_name_sufixes, '', name, 0, re.IGNORECASE)

    # 处理包含减号-和_的番号
    name = name.replace("_", "-")
    name = re.sub(r'(Carib)(bean)?', '', name, 0, re.IGNORECASE)
    # 移除干扰字段
    name = name.replace('22-sht.me', '')
    # 移除 清晰度相关度 字符,去除文件名中时间
    # 字母开头的
    pattern_of_resolution_alphas = r'(?<![a-zA-Z])(SD|((F|U)|(Full|Ultra)[-_*. ~]?)?HD|BD|(blu[-_*. ~]?ray)|h264|h265|HEVC)'
    # 数字开头的
    pattern_of_resolution_numbers = r'(?<!\d)(4K|(1080[ip])|(720p)|(480p))'
    pattern_of_date = r"\d{4}[-.]\d{1,2}[-.]\d{1,2}\ - "
    name = re.sub(pattern_of_resolution_alphas, "", name, 0, re.IGNORECASE)
    name = re.sub(pattern_of_resolution_numbers, "", name, 0, re.IGNORECASE)
    name = re.sub(pattern_of_date, "", name)

    if 'FC2' or 'fc2' in name:
        name = name.replace('-PPV', '').replace('PPV-', '').replace('FC2PPV-', 'FC2-').replace('FC2PPV_', 'FC2-')

    #移除连续重复无意义符号 . ~ - *
    # p = re.compile(r"([-_*. ~])(\1+)")
    name = re.sub(r"([-_*. ~])(\1+)", r"\1", name)
    # 移除尾部无意义符号 方便识别剧集数
    name = re.sub(r'[-_*. ~]$', "", name)
    # 提取可能的集数号(只识别一位) part1 ，ipz.A  ， CD1 ， NOP019B.HD.wmv
    episodes = 0
    try:
        # 零宽断言获取尾部数字 剧集数 123,abc ,#
        patern_episodes_number = r'(?<!\d)\d$'
        episodes = re.findall(patern_episodes_number, name)[-1]
        name = re.sub(patern_episodes_number, "", name)
    except:
        try:
            # 零宽断言获取尾部数字 剧集数 123,abc
            patern_episodes_alpha = r'(?<![a-zA-Z])[a-zA-Z]$'
            episodes = re.findall(patern_episodes_alpha, name)[-1]
            name = re.sub(patern_episodes_alpha, "", name)
        except:
            pass
        pass
    # 可能视屏文件名无番号，但是文件夹名含有番号
    # 正则取含-的番号 【字母-[字母]数字】,数字必定大于2位 番号的数组的最后的一个元素
    try:
        number = re.findall(r'[a-zA-Z|\d]+-[a-zA-Z|\d]*\d{2,}', name)[-1]
        if number:
            return number, episodes
    except:
        pass  # 不抛出错误，继续向下运行
    # 提取不含减号-的番号，FANZA CID

    # 非贪婪匹配非特殊字符，零宽断言后，数字至少2位连续,ipz221.part2 ， mide072hhb
    try:
        number = re.findall(r'[a-zA-Z|\d]+[a-zA-Z|\d]*\d{2,}', name)[-1]
        return number, episodes
    except:
        return '', episodes


def get_numbers(paths):
    #  提取对应路径的番号+集数

    maps = {}
    for path in paths:
        try:
            number, episode = getNumber(path)
            maps[path] = (number, episode)
        except:
            maps[path] = ("unknown", '0')
            pass

    return maps


if __name__ == '__main__':
    version = '2.8.2'

    print('[*]================== AV Data Capture ===================')
    print('[*]                    Version ' + version)
    print('[*]======================================================')

    # UpdateCheck(version)

    CreatFailedFolder(config.failed_folder)
    os.chdir(os.getcwd())

    # 遍历搜索目录下所有视频的路径
    # movie_list = movie_lists(config.escape_folder)
    # for i in movie_list:
    #     print(i)

    # 以下是测试的数据
    f = open('TestPaths.txt', 'r')
    movie_list = [line[:-1] for line in f.readlines()]
    f.close()
    # 获取 番号,集数,路径  的字典->list
    code_ep_paths = [[codeEposode[0], codeEposode[1], path] for path, codeEposode in get_numbers(movie_list).items()]
    [print(i) for i in code_ep_paths]
    # 排序
    # sorted_path_number_episodes = sorted(path_number_episodes, key=lambda kv: (str(kv[1][0]), str(kv[1][1])))
    # 按 番号和集数分组，每组元素数量大于1会产生覆盖，需要使用策略1.自动 1.1 取体积大的 1.2 取体积小的 1.3 选择特定后缀的  2. 手动
    # "https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html"
    # 显示所有列
    pd.set_option('display.max_columns', None)
    # 显示所有行
    pd.set_option('display.max_rows', None)
    # 设置value的显示长度为100，默认为50
    pd.set_option('max_colwidth', 30)

    df = pd.DataFrame(code_ep_paths, columns=('code', 'ep', 'path'))
    groupedCode_code_ep_paths = df.groupby(['code'])
    # print(df.groupby(['code']).describe().unstack())

    # print(len(list(groupbycodeNumber_path_number_episodes)))
    print('相同番号的电影：--------------')
    for code, code_ep_paths in groupedCode_code_ep_paths:
        # itemPaths = list(path_numberEepisode)
        if len(code_ep_paths) > 1:
            print(code + ":")
            [print('----ep:' + str(code_ep_path[1]) + ' path:' + str(code_ep_path[2])) for code_ep_path in code_ep_paths.values ]



    # isContinue = input('继续？Y or N')
    # if isContinue != "Y":
    #     exit(1)

    # ========== 野鸡番号拖动 ==========
    # number_argparse = argparse_get_file()
    # if not number_argparse == '':
    #     print("[!]Making Data for   [" + number_argparse + "], the number is [" + getNumber(number_argparse,
    #                                                                                         absolute_path=True) + "]")
    #     nfo = core_main(number_argparse, getNumber(number_argparse, absolute_path=True))
    #     print("[*]======================================================")
    #     CEF(config.success_folder)
    #     CEF(config.failed_folder)
    #     print("[+]All finished!!!")
    #     input("[+][+]Press enter key exit, you can check the error messge before you exit.")
    #     os._exit(0)
    # ========== 野鸡番号拖动 ==========


    count = 0
    count_all = str(len(movie_list))
    print('[+] Find', count_all, 'movies')

    codeNumberEpisode_nfo_paths = {}
    if config.soft_link:
        print('[!] --- Soft link mode is ENABLE! ----')
    for code, code_ep_paths in groupedCode_code_ep_paths:  # 遍历电影列表 交给core处理
        count = count + 1
        percentage = str(count / int(count_all) * 100)[:4] + '%'
        print('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
        try:
            print("[!]Fetching Data for   [" + code + "]")

            if code:
                # core 联网抓取信息
                nfo = core_main(code)
                codeNumberEpisode_nfo_paths[code] = nfo
                print("[*]======================================================")


        except Exception as e:  # 联网抓取信息失败
            print(
                '[-]' + code + " Can't find info from Internet:" + code + ',Reason:' + e)
            # if config.soft_link:
            #     print('[-]Link', file_path_name, 'to failed folder')
            #     os.symlink(file_path_name, config.failed_folder + '/')
            # else:
            #     try:
            #         print('[-]Move ' + file_path_name + ' to failed folder:' + config.failed_folder)
            #         shutil.move(file_path_name, config.failed_folder + '/')
            #     except FileExistsError:
            #         print('[!]File exists in failed!')
            #     except:
            #         print('[+]skip')
            continue

    for code_number, nfo in codeNumberEpisode_nfo_paths:
        print(code_number + ":")
        print("-----" + nfo)
    # CEF(config.success_folder)
    # CEF(config.failed_folder)
    print("[+]All finished!!!")
    input("[+][+]Press enter key exit, you can check the error messge before you exit.")
