from pathlib import Path

from PySide6.QtCore import QSettings

from .defaults import default_cfg_fpath


class SettingsStore(QSettings):

    def __init__(self, location: Path = default_cfg_fpath):
        super().__init__(str(location), QSettings.Format.IniFormat)

    def get_str_value(self, key: str) -> str:
        return str(self.value(key, defaultValue=""))

    def get_bool_value(self, key: str) -> bool:
        return bool(self.value(key, defaultValue="False", type=bool))

    @property
    def ApiKey(self) -> str:
        return self.get_str_value("ApiKey")

    @property
    def AuthEndpoint(self) -> str:
        return self.get_str_value("AuthEndpoint")

    @property
    def AutoStart(self) -> bool:
        return self.get_bool_value("AutoStart")

    @property
    def HeatsPath(self) -> str:
        return self.get_str_value("HeatsPath")

    @property
    def Host(self) -> str:
        return self.get_str_value("Host")

    @property
    def LogToFile(self) -> bool:
        return self.get_bool_value("LogToFile")

    @property
    def ResultsPath(self) -> str:
        return self.get_str_value("ResultsPath")

    @property
    def StartMinimized(self) -> bool:
        return self.get_bool_value("StartMinimized")
