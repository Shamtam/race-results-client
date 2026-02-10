from pathlib import Path

from PySide6.QtCore import QSettings

from .defaults import default_cfg_fname

_default_location = (Path.home() / default_cfg_fname).resolve()


class SettingsStore(QSettings):

    def __init__(self, location: Path = _default_location):
        super().__init__(str(location), QSettings.Format.IniFormat)

    def get_str_value(self, key: str) -> str:
        return str(self.value(key, defaultValue=""))

    def get_bool_value(self, key: str) -> bool:
        return bool(self.value(key, defaultValue="False", type=bool))

    @property
    def Host(self) -> str:
        return self.get_str_value("Host")

    @property
    def AuthEndpoint(self) -> str:
        return self.get_str_value("AuthEndpoint")

    @property
    def ApiKey(self) -> str:
        return self.get_str_value("ApiKey")

    @property
    def ResultsPath(self) -> str:
        return self.get_str_value("ResultsPath")

    @property
    def AutoStart(self) -> bool:
        return self.get_bool_value("AutoStart")

    @property
    def TrayStart(self) -> bool:
        return self.get_bool_value("TrayStart")
