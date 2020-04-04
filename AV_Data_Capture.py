#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
import fuckit
from tenacity import retry, stop_after_delay, wait_fixed
import json
import shutil
import argparse
from pathlib import Path
import pandas as pd

from core import *
from ConfigApp import ConfigApp
from PathNameProcessor import PathNameProcessor

config = ConfigApp()


def safe_list_get(list_in, idx, default):
    try:
        return list_in[idx]
    except IndexError:
        return default


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
            if re.search(PathNameProcessor.pattern_of_file_name_suffixes, file, re.IGNORECASE):
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

    name = PathNameProcessor.remove_distractions(name)
    suffix_episode, name = PathNameProcessor.extract_suffix_episode(name)

    episode_behind_code, code_number = PathNameProcessor.extract_code(name)
    code_number = code_number if code_number else ''
    episode = suffix_episode if suffix_episode else episode_behind_code if episode_behind_code else ''

    return code_number, episode


def get_numbers(paths):
    #  提取对应路径的番号+集数

    maps = {}
    for path in paths:
        # try:
        number, episode = getNumber(path)
        maps[path] = (number, episode)
    # except:
    #     maps[path] = ("unknown", '0')
    #     pass

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

    # 以下是从文本中提取测试的数据
    f = open('TestPathSpecial.txt', 'r')
    # f = open('TestPathNFO.txt', 'r')
    movie_list = [line[:-1] for line in f.readlines()]
    f.close()

    # 获取 番号,集数,路径  的字典->list
    code_ep_paths = [[codeEposode[0], codeEposode[1], path] for path, codeEposode in get_numbers(movie_list).items()]
    [print(i) for i in code_ep_paths]
    #  按番号分组片子列表（重点），用于寻找相同番号的片子
    # # 这里利用pandas分组 "https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html"
    # # 设置打印时显示所有列
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
    print("找到影片数量:" + str(len(movie_list)))
    print("合计番号数量:" + str(len(groupedCode_code_ep_paths)) + "  (多个相同番号的影片只统计一个，不能识别的番号 都统一为'unknown')")
    print('Warning:!!!! 以下为相同番号的电影明细')
    print('◤--------------------------------')
    for code, code_ep_paths in groupedCode_code_ep_paths:
        # itemPaths = list(path_numberEepisode)
        if len(code_ep_paths) > 1:
            print("|" + (code if code else 'unknown') + ":")
            [print('|           集数:' + str(code_ep_path[1]) + '  路径: ' + str(code_ep_path[2])) for code_ep_path in
             code_ep_paths.values]
    print('◣---------------------------------')
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

                    @retry(stop=stop_after_delay(3), wait=wait_fixed(2))
                    def read_file():
                        with open(file_path, 'w') as fp:
                            json.dump(nfo, fp)


                    read_file()

                # 将番号信息放入字典
                code_info_dict[code] = nfo
                print("[*]======================================================")

        except Exception as e:  # 番号的信息获取失败
            print('[-]' + code + " Can't find info:" + code + ',Reason:' + str(e))
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
    # 相同番号处理：按集数添加-CD[X]；视频格式 and 大小 分；
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
