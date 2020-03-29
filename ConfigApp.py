from configparser import ConfigParser

from MediaServer import MediaServer


class ConfigApp:
    def __init__(self):
        config_file = 'config.ini'
        config = ConfigParser()
        config.read(config_file, encoding='UTF-8')
        self.success_folder = config['common']['success_output_folder']
        self.failed_folder = config['common']['failed_output_folder']  # 失败输出目录
        self.escape_folder = config['escape']['folders']  # 多级目录刮削需要排除的目录
        self.search_folder = config['common']['search_folder']  # 搜索路径
        self.temp_folder = config['common']['temp_folder']  # 临时资源路径
        self.soft_link = (config['common']['soft_link'] == 1)
        self.escape_literals = (config['escape']['literals'] == 1)
        self.naming_rule = config['Name_Rule']['naming_rule']
        self.location_rule = config['Name_Rule']['location_rule']

        self.proxy = config['proxy']['proxy']
        self.timeout = config['proxy']['timeout']
        self.retry = config['proxy']['retry']
        self.media_server = MediaServer(config['media']['media_warehouse'])


