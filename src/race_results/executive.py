import json
import logging

from datetime import datetime, timezone
from http.client import HTTPSConnection
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Slot, QSettings, Signal
from traceback import format_exc
from typing import Any

from .axware.parser import parse_axware_live_results

_logger = logging.getLogger(__name__)

# TODO: clean this up and/or add to settings?
_host = "race-results-beta.vercel.app"
_endpoint = "/api/ingest/{}/live/results"


class ResultsFileWatcher(QThread):
    status_update = Signal(str)

    def __init__(self, parent: QObject, settings: QSettings):
        super().__init__(parent)
        self.settings = settings
        self.force_update = False

    def sanitize_data(self, input_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        base_entry = {
            "msrId": "",
            "email": "",
            "class": "",
            "carNumber": "",
            "driverName": "",
            "carModel": "",
            "carColor": "",
            "sponsor": "",
            "runs": [],
        }

        _axware_to_submit_map = {
            "Class": "class",
            "#": "carNumber",
            "Driver": "driverName",
            "Car Model": "carModel",
            "Car Color": "carColor",
            "Sponsor": "sponsor",
        }

        out_data = [
            dict(
                base_entry,
                **{_axware_to_submit_map.get(k, k): v for k, v in entry.items()},
            )
            for entry in input_data
        ]

        return out_data

    def upload_results(self, json_data: str) -> bool:
        org_slug = self.settings.value("OrgSlug")
        api_key = self.settings.value("ApiKey")
        timestamp = datetime.now().astimezone().isoformat()

        _logger.info(
            f"Uploading results to {_host}{_endpoint.format(org_slug)} at {timestamp}"
        )
        conn = HTTPSConnection(_host)
        headers = {
            "rr-ingest-api-key": api_key,
            "rr-results-ts": timestamp,
            "Content-Type": "application/json",
        }
        conn.request("POST", _endpoint.format(org_slug), json_data, headers)
        resp = conn.getresponse()

        # TODO: handle 400 and 500 responses

        return resp.status == 200

    @Slot()
    def run(self):

        fpath = Path(self.settings.value("ResultsPath"))

        if not fpath.exists():
            raise FileNotFoundError()

        last_upload = datetime(1, 1, 1, tzinfo=timezone.utc)  # force update upon entry

        while True:

            if self.isInterruptionRequested():
                return

            mtime = datetime.fromtimestamp(
                fpath.stat().st_mtime, timezone.utc
            ).astimezone()

            # skip parsing if file has not been modified since last upload and not forcing
            if mtime <= last_upload and not self.force_update:
                continue

            try:
                _logger.info(f"Parsing results file at {fpath}")
                results = parse_axware_live_results(fpath)

                _logger.info("Sanitizing results")
                json_data = json.dumps(self.sanitize_data(results))

                if self.upload_results(json_data):
                    _logger.info("Results uploaded successfully!")
                    last_upload = mtime
                    self.status_update.emit(
                        f"Last upload successful at {mtime.strftime("%H:%M")}"
                    )
                    self.force_update = False

            # on any errors, continue to watch, just log error and wait for another update
            except Exception as e:
                _logger.error(format_exc())
                continue

    @property
    def CanRun(self) -> bool:
        return (
            all(
                bool(x)
                for x in (self.settings.value("OrgSlug"), self.settings.value("ApiKey"))
            )
            and Path(self.settings.value("ResultsPath")).exists()
        )
