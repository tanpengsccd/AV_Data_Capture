#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
import re
from ADC_function import *
from core import *
from ConfigApp import ConfigApp
import json
import shutil
import argparse
from pathlib import Path
from operator import itemgetter
from itertools import groupby
import pandas as pd

config = ConfigApp()

patern_of_file_name_sufixes = r'.(mov|mp4|avi|rmvb|wmv|mov|mkv|flv|ts|m2ts)$'


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
    name = filepath.upper()  # 转大写
    if absolute_path:
        name = name.replace('\\', '/')
    # 移除文件类型后缀
    name = re.sub(patern_of_file_name_sufixes, '', name, 0, re.IGNORECASE)

    # 处理包含减号-和_的番号'/-070409_621'
    name = re.sub(r'[-_.~*# ]', "-", name, 0)

    name = re.sub(r'(Carib)(bean)?', '-', name, 0, re.IGNORECASE)
    name = re.sub(r'(1pondo)', '-', name, 0, re.IGNORECASE)
    name = re.sub(r'(tokyo)[-. ]?(hot)', '-', name, 0, re.IGNORECASE)
    name = re.sub(r'Uncensored', '-', name, 0, re.IGNORECASE)
    name = re.sub(r'JAV', '-', name, 0, re.IGNORECASE)
    # 移除干扰字段
    name = name.replace('22-sht.me', '-')
    # 移除 清晰度相关度 字符,去除文件名中时间
    # 字母开头的
    pattern_of_resolution_alphas = r'(?<![a-zA-Z])(SD|((F|U)|(Full|Ultra)[-_*. ~]?)?HD|BD|(blu[-_*. ~]?ray)|[hx]264|[hx]265|HEVC)'
    # 数字开头的
    pattern_of_resolution_numbers = r'(?<!\d)(4K|(1080[ip])|(720p)|(480p))'
    pattern_of_date = r"\d{4}[-.]\d{1,2}[-.]\d{1,2}\ - "
    name = re.sub(pattern_of_resolution_alphas, "-", name, 0, re.IGNORECASE)
    name = re.sub(pattern_of_resolution_numbers, "-", name, 0, re.IGNORECASE)
    name = re.sub(pattern_of_date, "", name)

    if 'FC2' or 'fc2' in name:
        name = name.replace('-PPV', '').replace('PPV-', '').replace('FC2PPV-', 'FC2-').replace('FC2PPV_', 'FC2-')

    # 移除连续重复无意义符号-
    # p = re.compile(r"([-_*. ~])(\1+)")
    name = re.sub(r"([-])(\1+)", r"\1", name)
    # 移除尾部无意义符号 方便识别剧集数
    name = re.sub(r'[-_*. ~]$', "", name)
    # 提取集数号 123ABC(只识别一位) part1 ，ipz.A  ， CD1 ， NOP019B.HD.wmv
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
    # 纯数字番号：062212-055
    # 字母+数字番号：N1180,mide072hhb,SIVR-00008
    name = re.findall(r'(?:\d{2,}-\d{2,})|(?:[A-Z]+-?[A-Z]*\d{2,})', name)[-1]
    if not ('-' in name):
        # 无减号-的番号，FANZA CID 尝试分段加上-
        # 非贪婪匹配非特殊字符，零宽断言后，数字至少2位连续,ipz221.part2 ， mide072hhb ,n1180
        try:
            name = re.findall(r'[a-zA-Z]+\d{2,}', name)[-1]
            # 比如MCDV-47 mcdv-047 是2个不一样的片子，但是 SIVR-00008 和 SIVR-008是同同一部
            name = re.sub(r'([a-zA-Z]{2,})(?:0*?)(\d{2,})', r'\1-\2', name)
            # return name, episodes
        except:
            pass
        # 正则取含-的番号 【字母-[字母]数字】,数字必定大于2位 番号的数组的最后的一个元素
    try:
        # MKBD_S03-MaRieS
        name = re.findall(r'[a-zA-Z|\d]+-[a-zA-Z|\d]*\d{2,}', name)[-1]
        # 107NTTR-037 -> NTTR-037 , SIVR-00008 -> SIVR-008
        searched = re.search(r'([a-zA-Z]{2,})-(?:0*)(\d{3,})', name)
        if searched:
            name = '-'.join(searched.groups())
        # 如果 name 存在 则 返回
        if name:
            return name, episodes
    except:
        return name, episodes


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

def create_folder(paths):
    for path_to_make in paths:
        if path_to_make:
            try:
                os.makedirs(path_to_make)
            except FileExistsError as e:
                # name = f'{folder=}'.split('=')[0].split('.')[-1]
                print(path_to_make + " 已经存在")
                pass
            except Exception as exception:
                print('! 创建文件夹失败，请确认权限')
                raise exception
        else:
            raise Exception('！创建的文件夹路径为空，请确认')


if __name__ == '__main__':
    version = '2.8.2'

    print('[*]================== AV Data Capture ===================')
    print('[*]                    Version ' + version)
    print('[*]======================================================')

    # UpdateCheck(version)

    CreatFailedFolder(config.failed_folder)
    os.chdir(os.getcwd())

    # 创建文件夹
    create_folder([config.failed_folder, config.search_folder, config.temp_folder])

    # temp 文件夹中infos放 番号json信息，pics中放图片信息
    path_infos = config.temp_folder + '/infos'
    path_pics = config.temp_folder + '/pics'

    create_folder([path_infos, path_pics])


    # 遍历搜索目录下所有视频的路径
    # movie_list = movie_lists(config.escape_folder)

    # 以下是测试的数据
    # f = open('TestPathSpecial.txt', 'r')
    f = open('TestPathNFO.txt', 'r')

    movie_list = [line[:-1] for line in f.readlines()]
    f.close()
    # 获取 番号,集数,路径  的字典->list
    code_ep_paths = [[codeEposode[0], codeEposode[1], path] for path, codeEposode in get_numbers(movie_list).items()]
    [print(i) for i in code_ep_paths]
    #  按番号分组片子列表（重点），用于寻找相同番号的片子
    # TODO 按 番号和集数分组，每组元素数量大于1会产生覆盖，需要使用策略1.自动 1.1 取体积大的 1.2 取体积小的 1.3 选择特定后缀的  2. 手动
    # # 这里利用pandas分组 "https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html"
    # # 显示所有列
    # pd.set_option('display.max_columns', None)
    # # 显示所有行
    # pd.set_option('display.max_rows', None)
    # # 设置value的显示长度为100，默认为50
    # pd.set_option('max_colwidth', 30)

    # 创建框架
    df = pd.DataFrame(code_ep_paths, columns=('code', 'ep', 'path'))
    # 以番号分组
    groupedCode_code_ep_paths = df.groupby(['code'])
    # print(df.groupby(['code']).describe().unstack())

    print('---------------------------------')
    print("Movies:" + str(len(movie_list)))
    print("Codes:" + str(len(groupedCode_code_ep_paths)) + "  (all recognized movies as 'unknown' code)")

    print('Warning:!!!! Same Code Movies')
    print('---------------------------------')
    for code, code_ep_paths in groupedCode_code_ep_paths:
        # itemPaths = list(path_numberEepisode)
        if len(code_ep_paths) > 1:
            print((code if code else 'unknown') + ":")
            [print('----ep:' + str(code_ep_path[1]) + '  path:' + str(code_ep_path[2])) for code_ep_path in
             code_ep_paths.values]
    isContinue = input('继续? N 退出 \n')
    if isContinue.strip(' ') == "N":
        exit(1)

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
    count_all_grouped = str(len(groupedCode_code_ep_paths))
    print('[+] Find ', count_all, ' movies,', count_all_grouped, ' numbers')

    # 创建 key为番号，value 为 番号信息的字典（貌似没用）
    code_info_dict = {}
    # if config.soft_link:
    #     print('[!] --- Soft link mode is ENABLE! ----')

    # 遍历按番号分组的集合，刮取番号信息并缓存
    for code, code_ep_paths in groupedCode_code_ep_paths:
        count = count + 1
        percentage = str(count / int(count_all_grouped) * 100)[:4] + '%'
        print('[!] - ' + percentage + ' [' + str(count) + '/' + count_all_grouped + '] -')
        try:
            print("[!]Fetching Data for   [" + code + "]")

            if code:
                # 创建番号的文件夹
                file_path = path_infos + '/' + code + '.json'
                nfo = {}
                # 读取缓存信息，如果没有则联网搜刮

                path = Path(file_path)
                if path.exists() and path.is_file() and path.stat().st_size > 0:
                    print('找到缓存信息：' + code)
                    with open(file_path) as fp:
                        nfo = json.load(fp)
                else:

                    # 核心功能 - 联网抓取信息字典
                    print('联网搜刮：' + code)
                    nfo = core_main(code)
                    # 把缓存信息写入缓存文件夹中
                    with open(file_path, 'w') as fp:
                        json.dump(nfo, fp)
                # 将番号信息放入字典
                code_info_dict[code] = nfo
                print("[*]======================================================")

        except Exception as e:  # 番号的信息获取失败
            print('[-]' + code + " Can't find info:" + code + ',Reason:' + e)
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

    print('----------------------------------')
    # 遍历番号信息，下载番号电影的海报，图片
    for code, nfo in code_info_dict.items():
        if len(nfo.keys()) == 0:
            print(code + '：信息为空 忽略')
            continue


        code_pics_folder_to_save = path_pics + '/' + code
        # 1 创建 番号文件夹
        os.makedirs(code_pics_folder_to_save, exist_ok=True)
        #  下载缩略图
        if nfo['imagecut'] == 3:  # 3 是缩略图
            path = Path(code_pics_folder_to_save + '/' + 'thumb.png')
            if path.exists() and path.is_file() and path.stat().st_size > 0:
                print(code + '：缩略图已有缓存')
            else:
                print(code + '：缩略图下载中...')
                download_file(nfo['cover_small'], code_pics_folder_to_save, 'thumb.png')
                print(code + '：缩略图下载完成')
        #  下载海报
        path = Path(code_pics_folder_to_save + '/' + 'poster.png')
        if path.exists() and path.is_file() and path.stat().st_size > 0:
            print(code + '：海报已有缓存')
        else:
            print(code + '：海报下载中...')
            download_file(nfo['cover'], code_pics_folder_to_save, 'poster.png')
            print(code + '：海报下载完成')

        # # 2 创建缩略图海报
        # if nfo['imagecut'] == 3:  # 3 是缩略图
        #     download_cover_file(nfo['cover_small'], code, code_pics_folder_to_save)
        # # 3 创建图
        # download_image(nfo['cover'], code, code_pics_folder_to_save)
        # # 4 剪裁
        # crop_image(nfo['imagecut'], code, code_pics_folder_to_save)
        # # 5 背景图
        # copy_images_to_background_image(code, code_pics_folder_to_save)
        # 6 创建 mame.nfo(不需要，需要时从infos中josn文件转为nfo文件)
        # make_nfo_file(nfo, code, temp_path_to_save)

    # 开始操作
    # TODO 方式1 刮削：添加nfo，封面，内容截图等
    # TODO 方式2 整理+刮削：按规则移动影片，字幕 到 演员，发行商，有无🐎 等



    # if config.program_mode == '1':
    #     if multi_part == 1:
    #         number += part  # 这时number会被附加上CD1后缀
    #     smallCoverCheck(path, number, imagecut, json_data['cover_small'], c_word, option, filepath, config.failed_folder)  # 检查小封面
    #     imageDownload(option, json_data['cover'], number, c_word, path, multi_part, filepath, config.failed_folder)  # creatFoder会返回番号路径
    #     cutImage(option, imagecut, path, number, c_word)  # 裁剪图
    #     copyRenameJpgToBackdrop(option, path, number, c_word)
    #     PrintFiles(option, path, c_word, json_data['naming_rule'], part, cn_sub, json_data, filepath, config.failed_folder, tag)  # 打印文件 .nfo
    #     pasteFileToFolder(filepath, path, number, c_word)  # 移动文件
    #     # =======================================================================整理模式
    # elif config.program_mode == '2':
    #     pasteFileToFolder_mode2(filepath, path, multi_part, number, part, c_word)  # 移动文件

    # CEF(config.success_folder)
    # CEF(config.failed_folder)
    print("[+]All finished!!!")
    input("[+][+]Press enter key exit, you can check the error message before you exit.")
