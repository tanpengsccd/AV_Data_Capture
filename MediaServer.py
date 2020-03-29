from enum import Enum, auto


class MediaServer(Enum):
    EMBY = auto()
    JELLYFIN = EMBY
    PLEX = auto()
    KODI = auto()

    # media = EMBY
    #
    def __init__(self, arg):
        self = [e for e in MediaServer if arg.upper() == self.name]
