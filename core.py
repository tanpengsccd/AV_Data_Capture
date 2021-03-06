# -*- coding: utf-8 -*-

import os.path
import shutil
from PIL import Image
import json
from ADC_function import *
from MediaServer import *
from AV_Data_Capture import config
import lazyxml
# =========website========
from SiteSource import avsox, javdb, fc2fans_club, javbus, fanza, mgstage
import requests
from enum import Enum, auto


# =====================本地文件处理===========================

def escapePath(path, escapeLiterals):  # Remove escape literals
    # escapeLiterals = Config['escape']['literals']
    backslash = '\\'
    for literal in escapeLiterals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath, failed_folder):
    if failed_folder.strip() == '':
        print('[+]Failed output folder is Empty')
    else:
        print('[-]Move to Failed output folder')
        shutil.move(filepath, failed_folder)
    return


def CreatFailedFolder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            return

        # 根据番号获取字典数据


class SiteSource(Enum):
    AVSOX = auto()
    FC2 = auto()
    FANZA = auto()
    JAVDB = auto()
    JAVBUS = auto()
    MGSTAGE = auto()


def getDataFromJSON(file_number):  # 从JSON返回元数据
    """
    iterate through all services and fetch the data
    """

    func_mapping = {
        "avsox": avsox.main,
        "fc2": fc2fans_club.main,
        "fanza": fanza.main,
        "javdb": javdb.main,
        "javbus": javbus.main,
        "mgstage": mgstage.main,
    }

    # default fetch order list, from the begining to the end
    sources = ["javbus", "javdb", "fanza", "mgstage", "fc2", "avsox"]

    # if the input file name matches centain rules,
    # move some web service to the begining of the list
    if re.match(r"^\d{5,}", file_number) or re.match(r'heyzo', file_number, re.IGNORECASE):
        sources.insert(0, sources.pop(sources.index("avsox")))
    elif re.match(r"\d+\D+", file_number) or re.match(r'siro', file_number, re.IGNORECASE):
        sources.insert(0, sources.pop(sources.index("mgstage")))
        sources.insert(0, sources.pop(sources.index("fanza")))
    elif re.match(r'fc2', file_number, re.IGNORECASE):
        sources.insert(0, sources.pop(sources.index("fc2")))

    for source in sources:
        json_data = json.loads(func_mapping[source](file_number))
        # if any service return a valid return, break
        if getDataState(json_data) != 0:
            break

    # ================================================网站规则添加结束================================================

    title = json_data['title']
    actor_list = str(json_data['actor']).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    release = json_data['release']
    number = json_data['number']
    studio = json_data['studio']
    source = json_data['source']
    runtime = json_data['runtime']
    outline = json_data['runtime']
    label = json_data['label']
    year = json_data['year']
    try:
        cover_small = json_data['cover_small']
    except:
        cover_small = ''

    imagecut = json_data['imagecut']
    tag = str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    if title == '' or number == '':
        raise Exception('[-]Movie Data not found!')

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
    title = re.sub(r'[#\\/:*?"<>|\]]', '', title, 0, re.IGNORECASE)
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')
    # ====================处理异常字符 END================== #\/:*?"<>|

    naming_rule = eval(config.naming_rule)
    location_rule = eval(config.location_rule)

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['naming_rule'] = naming_rule
    json_data['location_rule'] = location_rule
    json_data['year'] = year
    return json_data


def get_info(json_data):  # 返回json里的数据
    title = json_data['title']
    studio = json_data['studio']
    year = json_data['year']
    outline = json_data['outline']
    runtime = json_data['runtime']
    director = json_data['director']
    actor_photo = json_data['actor_photo']
    release = json_data['release']
    number = json_data['number']
    cover = json_data['cover']
    website = json_data['website']
    return title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website


def download_cover_file(url, name, folder_path):
    """
    download small cover
    :param url: url
    :param name:  name same as movie's name without ext
    :param folder_path:  dir to save
    :return:
    """
    filename = config.media_server.poster_name(name)
    DownloadFileWithFilename(url, filename, folder_path)


def smallCoverCheck(path, number, imagecut, cover_small, c_word, option, filepath, failed_folder):
    if imagecut == 3:
        if option == 'emby':
            DownloadFileWithFilename(cover_small, '1.jpg', path, filepath, failed_folder)
            try:
                img = Image.open(path + '/1.jpg')
            except Exception:
                img = Image.open('1.jpg')
            w = img.width
            h = img.height
            img.save(path + '/' + number + c_word + '.png')
            time.sleep(1)
            os.remove(path + '/1.jpg')
        if option == 'kodi':
            DownloadFileWithFilename(cover_small, '1.jpg', path, filepath, failed_folder)
            try:
                img = Image.open(path + '/1.jpg')
            except Exception:
                img = Image.open('1.jpg')
            w = img.width
            h = img.height
            img.save(path + '/' + number + c_word + '-poster.jpg')
            time.sleep(1)
            os.remove(path + '/1.jpg')
        if option == 'plex':
            DownloadFileWithFilename(cover_small, '1.jpg', path, filepath, failed_folder)
            try:
                img = Image.open(path + '/1.jpg')
            except Exception:
                img = Image.open('1.jpg')
            w = img.width
            h = img.height
            img.save(path + '/poster.jpg')
            os.remove(path + '/1.jpg')


def creatFolder(success_folder, location_rule, json_data, escapeLiterals):  # 创建文件夹
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website = get_info(json_data)
    if len(location_rule) > 240:  # 新建成功输出文件夹
        path = success_folder + '/' + location_rule.replace("'actor'", "'manypeople'", 3).replace("actor",
                                                                                                  "'manypeople'",
                                                                                                  3)  # path为影片+元数据所在目录
    else:
        path = success_folder + '/' + location_rule
        # print(path)
    if not os.path.exists(path):
        path = escapePath(path, escapeLiterals)
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ']-' + title, "/number")
            path = escapePath(path, escapeLiterals)
            os.makedirs(path)
    return path


# =====================资源下载部分===========================
def download_file(url, folder, name_with_ext):
    """
    download file
    :param url: source url
    :param name_with_ext:  full name like 'mike.jpg'
    :param folder: folder path
    :return: full path if downloaded file like '/Users/proj/AV_Data_Capture/mike.jpg'
    """
    proxy_dict = {"http": str(config.proxy), "https": str(config.proxy)} if config.proxy else None
    i = 0
    while i < config.retry:
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            r = requests.get(url, headers=headers, timeout=config.timeout, proxies=proxy_dict)
            if r == '':
                print('[-]Movie Data not found!')
                return
            with open(str(folder) + "/" + name_with_ext, "wb") as code:
                code.write(r.content)
            return str(folder) + "/" + name_with_ext
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(config.retry))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(config.retry))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(config.retry))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(config.retry))


def DownloadFileWithFilename(url, filename, path):  # path = examle:photo , video.in the Project Folder!
    proxy, timeout, retry_count = get_network_settings()
    i = 0
    proxy_dict = {"http": str(config.proxy), "https": str(config.proxy)} if proxy else None
    while i < retry_count:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            r = requests.get(url, headers=headers, timeout=timeout,
                             proxies=proxy_dict)
            if r == '':
                print('[-]Movie Data not found!')
                return
            with open(str(path) + "/" + filename, "wb")  as code:
                code.write(r.content)
            return
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    # moveFailedFolder(filepath, failed_folder)
    return


def download_image(url, name, folder):
    """
    download img
    :param url:  source
    :param name:  name
    :param folder: folder to save
    :return:
    """
    name_with_ext = config.media_server.image_name(name)
    download_file(url, folder, name_with_ext)


def imageDownload(option, cover, number, c_word, path, multi_part, filepath, failed_folder):  # 封面是否下载成功，否则移动到failed
    if option == 'emby':  # name.jpg
        if DownloadFileWithFilename(cover, number + c_word + '.jpg', path, filepath, failed_folder) == 'failed':
            moveFailedFolder(filepath, failed_folder)
            return
        DownloadFileWithFilename(cover, number + c_word + '.jpg', path, filepath, failed_folder)
        if not os.path.getsize(path + '/' + number + c_word + '.jpg') == 0:
            print('[+]Image Downloaded!', path + '/' + number + c_word + '.jpg')
            return
        i = 1
        while i <= int(config.retry):
            if os.path.getsize(path + '/' + number + c_word + '.jpg') == 0:
                print('[!]Image Download Failed! Trying again. [' + config.retry + '/3]')
                DownloadFileWithFilename(cover, number + c_word + '.jpg', path, filepath, failed_folder)
                i = i + 1
                continue
            else:
                break
        if multi_part == 1:
            old_name = os.path.join(path, number + c_word + '.jpg')
            new_name = os.path.join(path, number + c_word + '.jpg')
            os.rename(old_name, new_name)
            print('[+]Image Downloaded!', path + '/' + number + c_word + '.jpg')
        else:
            print('[+]Image Downloaded!', path + '/' + number + c_word + '.jpg')
    elif option == 'plex':  # fanart.jpg
        if DownloadFileWithFilename(cover, 'fanart.jpg', path, filepath, failed_folder) == 'failed':
            moveFailedFolder(filepath, failed_folder)
            return
        DownloadFileWithFilename(cover, 'fanart.jpg', path, filepath, failed_folder)
        if not os.path.getsize(path + '/fanart.jpg') == 0:
            print('[+]Image Downloaded!', path + '/fanart.jpg')
            return
        i = 1
        while i <= int(config.retry):
            if os.path.getsize(path + '/fanart.jpg') == 0:
                print('[!]Image Download Failed! Trying again. [' + config.retry + '/3]')
                DownloadFileWithFilename(cover, 'fanart.jpg', path, filepath, failed_folder)
                i = i + 1
                continue
            else:
                break
        if not os.path.getsize(path + '/' + number + c_word + '.jpg') == 0:
            print('[!]Image Download Failed! Trying again.')
            DownloadFileWithFilename(cover, number + c_word + '.jpg', path, filepath, failed_folder)
        print('[+]Image Downloaded!', path + '/fanart.jpg')
    elif option == 'kodi':  # [name]-fanart.jpg
        if DownloadFileWithFilename(cover, number + c_word + '-fanart.jpg', path, filepath, failed_folder) == 'failed':
            moveFailedFolder(filepath, failed_folder)
            return
        DownloadFileWithFilename(cover, number + c_word + '-fanart.jpg', path, filepath, failed_folder)
        if not os.path.getsize(path + '/' + number + c_word + '-fanart.jpg') == 0:
            print('[+]Image Downloaded!', path + '/' + number + c_word + '-fanart.jpg')
            return
        i = 1
        while i <= int(config.retry):
            if os.path.getsize(path + '/' + number + c_word + '-fanart.jpg') == 0:
                print('[!]Image Download Failed! Trying again. [' + config.retry + '/3]')
                DownloadFileWithFilename(cover, number + c_word + '-fanart.jpg', path, filepath, failed_folder)
                i = i + 1
                continue
            else:
                break
        print('[+]Image Downloaded!', path + '/' + number + c_word + '-fanart.jpg')


def make_nfo_file(nfo, nfo_name, folder_path):
    """
    make xxx.nfo in folder
    :param nfo_name: name
    :param nfo: nfo dict
    :param folder_path: where to create file, default temp_folder
    :return:
    """
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website = get_info(nfo)
    naming_rule = nfo['naming_rule']
    tag = nfo['tag']

    path = folder_path
    c_word = ''
    cn_sub = ''
    part = ''
    # path_file = path + "/" + number + c_word + ".nfo", "wt"
    path_file = path + "/" + nfo_name + c_word + ".nfo"
    lazyxml.dump
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        if config.media_server == MediaServer.PLEX:
            with open(path_file, "wt", encoding='UTF-8') as code:
                print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
                print("<movie>", file=code)
                print(" <title>" + naming_rule + part + "</title>", file=code)
                print("  <set>", file=code)
                print("  </set>", file=code)
                print("  <studio>" + studio + "+</studio>", file=code)
                print("  <year>" + year + "</year>", file=code)
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
                print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
                print("  <director>" + director + "</director>", file=code)
                print("  <poster>poster.jpg</poster>", file=code)
                print("  <thumb>thumb.png</thumb>", file=code)
                print("  <fanart>fanart.jpg</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not value == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except:
                    aaaa = ''
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in str(tag).strip("[ ]").replace("'", '').replace(" ", '').split(','):
                        print("  <tag>" + i + "</tag>", file=code)
                except:
                    aaaaa = ''
                try:
                    for i in str(tag).strip("[ ]").replace("'", '').replace(" ", '').split(','):
                        print("  <genre>" + i + "</genre>", file=code)
                except:
                    aaaaaaaa = ''
                if cn_sub == '1':
                    print("  <genre>中文字幕</genre>", file=code)
                print("  <num>" + number + "</num>", file=code)
                print("  <release>" + release + "</release>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + website + "</website>", file=code)
                print("</movie>", file=code)
                print("[+]Writeed!          " + path + "/" + number + ".nfo")
        elif config.media_server == MediaServer.EMBY:
            with open(path_file, "wt", encoding='UTF-8') as code:
                print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
                print("<movie>", file=code)
                print(" <title>" + naming_rule + part + "</title>", file=code)
                print("  <set>", file=code)
                print("  </set>", file=code)
                print("  <studio>" + studio + "+</studio>", file=code)
                print("  <year>" + year + "</year>", file=code)
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
                print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
                print("  <director>" + director + "</director>", file=code)
                print("  <poster>" + number + c_word + ".png</poster>", file=code)
                print("  <thumb>" + number + c_word + ".png</thumb>", file=code)
                print("  <fanart>" + number + c_word + '.jpg' + "</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not value == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except:
                    aaaa = ''
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in tag:
                        print("  <tag>" + i + "</tag>", file=code)
                except:
                    aaaaa = ''
                try:
                    for i in tag:
                        print("  <genre>" + i + "</genre>", file=code)
                except:
                    aaaaaaaa = ''
                if cn_sub == '1':
                    print("  <genre>中文字幕</genre>", file=code)
                print("  <num>" + number + "</num>", file=code)
                print("  <premiered>" + release + "</premiered>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + website + "</website>", file=code)
                print("</movie>", file=code)
                print("[+]Writeed!          " + path + "/" + number + c_word + ".nfo")
        elif config.media_server == MediaServer.KODI:
            with open(path_file, "wt", encoding='UTF-8') as code:
                print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
                print("<movie>", file=code)
                print(" <title>" + naming_rule + part + "</title>", file=code)
                print("  <set>", file=code)
                print("  </set>", file=code)
                print("  <studio>" + studio + "+</studio>", file=code)
                print("  <year>" + year + "</year>", file=code)
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
                print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
                print("  <director>" + director + "</director>", file=code)
                print("  <poster>" + number + c_word + "-poster.jpg</poster>", file=code)
                print("  <fanart>" + number + c_word + '-fanart.jpg' + "</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not value == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except:
                    aaaa = ''
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in tag:
                        print("  <tag>" + i + "</tag>", file=code)
                except:
                    aaaaa = ''
                try:
                    for i in tag:
                        print("  <genre>" + i + "</genre>", file=code)
                except:
                    aaaaaaaa = ''
                if cn_sub == '1':
                    print("  <genre>中文字幕</genre>", file=code)
                print("  <num>" + number + "</num>", file=code)
                print("  <release>" + release + "</release>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + website + "</website>", file=code)
                print("</movie>", file=code)
                print("[+]Writeed!          " + path + "/" + number + c_word + ".nfo")
    except IOError as e:
        print("[-]Write Failed! :" + e)
        # print(e)
        # moveFailedFolder(filepath, failed_folder)
        return
    except Exception as e:
        print("[-]Write Failed! :" + e)
        # moveFailedFolder(filepath, failed_folder)
        return


def PrintFiles(option, path, c_word, naming_rule, part, cn_sub, json_data, filepath, failed_folder, tag):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website = get_info(json_data)
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        if option == 'plex':
            with open(path + "/" + number + c_word + ".nfo", "wt", encoding='UTF-8') as code:
                print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
                print("<movie>", file=code)
                print(" <title>" + naming_rule + part + "</title>", file=code)
                print("  <set>", file=code)
                print("  </set>", file=code)
                print("  <studio>" + studio + "+</studio>", file=code)
                print("  <year>" + year + "</year>", file=code)
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
                print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
                print("  <director>" + director + "</director>", file=code)
                print("  <poster>poster.jpg</poster>", file=code)
                print("  <thumb>thumb.png</thumb>", file=code)
                print("  <fanart>fanart.jpg</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not value == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except:
                    aaaa = ''
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(','):
                        print("  <tag>" + i + "</tag>", file=code)
                except:
                    aaaaa = ''
                try:
                    for i in str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(','):
                        print("  <genre>" + i + "</genre>", file=code)
                except:
                    aaaaaaaa = ''
                if cn_sub == '1':
                    print("  <genre>中文字幕</genre>", file=code)
                print("  <num>" + number + "</num>", file=code)
                print("  <release>" + release + "</release>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + website + "</website>", file=code)
                print("</movie>", file=code)
                print("[+]Writeed!          " + path + "/" + number + ".nfo")
        elif option == 'emby':
            with open(path + "/" + number + c_word + ".nfo", "wt", encoding='UTF-8') as code:
                print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
                print("<movie>", file=code)
                print(" <title>" + naming_rule + part + "</title>", file=code)
                print("  <set>", file=code)
                print("  </set>", file=code)
                print("  <studio>" + studio + "+</studio>", file=code)
                print("  <year>" + year + "</year>", file=code)
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
                print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
                print("  <director>" + director + "</director>", file=code)
                print("  <poster>" + number + c_word + ".png</poster>", file=code)
                print("  <thumb>" + number + c_word + ".png</thumb>", file=code)
                print("  <fanart>" + number + c_word + '.jpg' + "</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not value == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except:
                    aaaa = ''
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in tag:
                        print("  <tag>" + i + "</tag>", file=code)
                except:
                    aaaaa = ''
                try:
                    for i in tag:
                        print("  <genre>" + i + "</genre>", file=code)
                except:
                    aaaaaaaa = ''
                if cn_sub == '1':
                    print("  <genre>中文字幕</genre>", file=code)
                print("  <num>" + number + "</num>", file=code)
                print("  <premiered>" + release + "</premiered>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + website + "</website>", file=code)
                print("</movie>", file=code)
                print("[+]Writeed!          " + path + "/" + number + c_word + ".nfo")
        elif option == 'kodi':
            with open(path + "/" + number + c_word + ".nfo", "wt", encoding='UTF-8') as code:
                print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
                print("<movie>", file=code)
                print(" <title>" + naming_rule + part + "</title>", file=code)
                print("  <set>", file=code)
                print("  </set>", file=code)
                print("  <studio>" + studio + "+</studio>", file=code)
                print("  <year>" + year + "</year>", file=code)
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
                print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
                print("  <director>" + director + "</director>", file=code)
                print("  <poster>" + number + c_word + "-poster.jpg</poster>", file=code)
                print("  <fanart>" + number + c_word + '-fanart.jpg' + "</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not value == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except:
                    aaaa = ''
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in tag:
                        print("  <tag>" + i + "</tag>", file=code)
                except:
                    aaaaa = ''
                try:
                    for i in tag:
                        print("  <genre>" + i + "</genre>", file=code)
                except:
                    aaaaaaaa = ''
                if cn_sub == '1':
                    print("  <genre>中文字幕</genre>", file=code)
                print("  <num>" + number + "</num>", file=code)
                print("  <release>" + release + "</release>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + website + "</website>", file=code)
                print("</movie>", file=code)
                print("[+]Writeed!          " + path + "/" + number + c_word + ".nfo")
    except IOError as e:
        print("[-]Write Failed!")
        print(e)
        moveFailedFolder(filepath, failed_folder)
        return
    except Exception as e1:
        print(e1)
        print("[-]Write Failed!")
        moveFailedFolder(filepath, failed_folder)
        return


def crop_image(crop_style, name, path):
    try:
        origin_image = Image.open(path + '/' + config.media_server.image_name(name))
        if crop_style == 1:
            cropped_image = origin_image.crop((origin_image.width / 1.9, 0, origin_image.width, origin_image.height))
        else:
            cropped_image = origin_image
        cropped_image.save(path + '/' + config.media_server.poster_name(name))

    except Exception as e:
        print('[-]Cover cut failed:' + e)


def cutImage(option, imagecut, path, number, c_word):
    if option == 'plex':
        if imagecut == 1:  # 截取右侧封面 fanart.jpg 截取为poster.jpg
            try:
                img = Image.open(path + '/fanart.jpg')
                imgSize = img.size
                w = img.width
                h = img.height
                img2 = img.crop((w / 1.9, 0, w, h))
                img2.save(path + '/poster.jpg')
            except:
                print('[-]Cover cut failed!')
        elif imagecut == 0:  # 改名 fanart.jpg ->poster.jpg
            img = Image.open(path + '/fanart.jpg')
            w = img.width
            h = img.height
            img.save(path + '/poster.jpg')
    elif option == 'emby':
        if imagecut == 1:  # 截取右侧封面 [name].jpg 截取为 [name].jpg
            try:
                img = Image.open(path + '/' + number + c_word + '.jpg')
                imgSize = img.size
                w = img.width
                h = img.height
                img2 = img.crop((w / 1.9, 0, w, h))
                img2.save(path + '/' + number + c_word + '.png')
            except:
                print('[-]Cover cut failed!')
        elif imagecut == 0:  # [name].jpg -> [name].png
            img = Image.open(path + '/' + number + c_word + '.jpg')
            img.save(path + '/' + number + c_word + '.png')
    elif option == 'kodi':
        if imagecut == 1:  # 截取右侧封面 [name]-fanart.jpg 截取为 [name]-poster.jpg
            try:
                img = Image.open(path + '/' + number + c_word + '-fanart.jpg')
                w = img.width
                h = img.height
                img2 = img.crop((w / 1.9, 0, w, h))
                img2.save(path + '/' + number + c_word + '-poster.jpg')
            except:
                print('[-]Cover cut failed!')
        elif imagecut == 0:  # [name]-fanart.jpg 截取为 [name]-poster.jpg
            img = Image.open(path + '/' + number + c_word + '-fanart.jpg')

            try:
                img = img.convert('RGB')
                img.save(path + '/' + number + c_word + '-poster.jpg')
            except:
                img = img.convert('RGB')
                img.save(path + '/' + number + c_word + '-poster.jpg')


def pasteFileToFolder(filepath, path, number, c_word):  # 文件路径，番号，后缀，要移动至的位置
    houzhui = str(re.search('[.](avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm)$', filepath, re.IGNORECASE).group())
    try:
        if config.soft_link == '1':  # 如果soft_link=1 使用软链接
            os.symlink(filepath, path + '/' + number + c_word + houzhui)
        else:
            os.rename(filepath, path + '/' + number + c_word + houzhui)
        if os.path.exists(config.search_folder + '/' + number + c_word + '.srt'):  # 字幕移动
            os.rename(config.search_folder + '/' + number + c_word + '.srt', path + '/' + number + c_word + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(config.search_folder + '/' + number + c_word + '.ssa'):
            os.rename(os.getcwd() + '/' + number + c_word + '.ssa', path + '/' + number + c_word + '.ssa')
            print('[+]Sub moved!')
        elif os.path.exists(config.search_folder + '/' + number + c_word + '.sub'):
            os.rename(os.getcwd() + '/' + number + c_word + '.sub', path + '/' + number + c_word + '.sub')
            print('[+]Sub moved!')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return


def pasteFileToFolder_mode2(filepath, path, multi_part, number, part, c_word):  # 文件路径，番号，后缀，要移动至的位置
    if multi_part == 1:
        number += part  # 这时number会被附加上CD1后缀
    houzhui = str(re.search('[.](avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm)$', filepath, re.IGNORECASE).group())
    try:
        if config.soft_link== '1':
            os.symlink(filepath, path + '/' + number + part + c_word + houzhui)
        else:
            os.rename(filepath, path + '/' + number + part + c_word + houzhui)
        if os.path.exists(number + '.srt'):  # 字幕移动
            os.rename(number + part + c_word + '.srt', path + '/' + number + part + c_word + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(number + part + c_word + '.ass'):
            os.rename(number + part + c_word + '.ass', path + '/' + number + part + c_word + '.ass')
            print('[+]Sub moved!')
        elif os.path.exists(number + part + c_word + '.sub'):
            os.rename(number + part + c_word + '.sub', path + '/' + number + part + c_word + '.sub')
            print('[+]Sub moved!')
        print('[!]Success')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return


def copy_images_to_background_image(name, path):
    shutil.copy(path + "/" + config.media_server.image_name(name), path + "/Backdrop.jpg")
    if config.media_server == MediaServer.PLEX:
        shutil.copy(path + "/" + config.media_server.poster_name(name), path + '/thumb.png')


def copyRenameJpgToBackdrop(option, path, number, c_word):
    if option == 'plex':
        shutil.copy(path + '/fanart.jpg', path + '/Backdrop.jpg')
        shutil.copy(path + '/poster.jpg', path + '/thumb.png')
    if option == 'emby':
        shutil.copy(path + '/' + number + c_word + '.jpg', path + '/Backdrop.jpg')
    if option == 'kodi':
        shutil.copy(path + '/' + number + c_word + '-fanart.jpg', path + '/Backdrop.jpg')


def get_part(filepath, failed_folder):
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
        if re.search('-cd\d+', filepath):
            return re.findall('-cd\d+', filepath)[0]
    except:
        print("[-]failed!Please rename the filename again!")
        moveFailedFolder(filepath, failed_folder)
        return


def debug_mode(json_data):
    try:
        if config.debug_mode == '1':
            print('[+] ---Debug info---')
            for i, v in json_data.items():
                if i == 'outline':
                    print('[+]  -', i, '    :', len(v), 'characters')
                    continue
                if i == 'actor_photo' or i == 'year':
                    continue
                print('[+]  -', "%-11s" % i, ':', v)
            print('[+] ---Debug info---')
    except:
        aaa = ''


def core_main(number_th):
    # =======================================================================初始化所需变量
    multi_part = 0
    part = ''
    c_word = ''
    option = ''
    cn_sub = ''

    # filepath = file_path  # 影片的路径
    number = number_th

    json_data = getDataFromJSON(number)  # 定义番号

    # if json_data.get('number') != number:
    # fix issue #119
    # the root cause is we normalize the search id
    # PrintFiles() will use the normalized id from website,
    # but pasteFileToFolder() still use the input raw search id
    # so the solution is: use the normalized search id
    # number = json_data["number"]
    # imagecut = json_data['imagecut']
    # tag = json_data['tag']
    # =======================================================================判断-C,-CD后缀
    # if '-CD' in filepath or '-cd' in filepath:
    #     multi_part = 1
    #     part = get_part(filepath, config.failed_folder)

    # if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
    #     cn_sub = '1'
    #     c_word = '-C'  # 中文字幕影片后缀

    # CreatFailedFolder(config.failed_folder)  # 创建输出失败目录
    # debug_mode(json_data)  # 调试模式检测
    return json_data
    # path = creatFolder(config.success_folder, json_data['location_rule'], json_data, config.escape_literals)  # 创建文件夹
    # =======================================================================刮削模式
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
