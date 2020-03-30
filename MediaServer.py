from enum import Enum, auto


class MediaServer(Enum):
    EMBY = auto()
    PLEX = auto()
    KODI = auto()

    # media = EMBY
    #
    def __init__(self, arg):
        self = [e for e in MediaServer if arg.upper() == self.name]

    def poster_name(self, name):
        if self == MediaServer.EMBY:  # 保存[name].png
            return name + '.png'
        elif self == MediaServer.KODI:  # 保存[name]-poster.jpg
            return name + '-poster.jpg'
        elif self == MediaServer.PLEX:  # 保存 poster.jpg
            return 'poster.jpg'

    def image_name(self, name):
        if self == MediaServer.EMBY:  # name.jpg
            return name + '.jpg'
        elif self == MediaServer.KODI:  # [name]-fanart.jpg
            return name + '-fanart.jpg'
        elif self == MediaServer.PLEX:  # fanart.jpg
            return 'fanart.jpg'
