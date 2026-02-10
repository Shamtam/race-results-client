import json
import requests

from logging import ERROR, DEBUG, INFO, WARNING
from datetime import datetime, timezone
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Slot, Signal
from traceback import format_exc
from typing import Any
from urllib.parse import urljoin

from .axware.parser import parse_axware_live_results
from .defaults import default_host, default_auth_endpoint, max_allowed_failures
from .settings import SettingsStore


class ResultsFileWatcher(QThread):
    connected = Signal(str, str)
    log_message = Signal(int, str)
    notification = Signal(str)

    def __init__(self, parent: QObject, settings: SettingsStore):
        super().__init__(parent)
        self.settings = settings
        self.force_update_flag = False
        self.close_event_flag = False

        self.state = {}

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

    def get_host(self):
        return self.settings.Host if self.settings.Host else default_host

    def get_auth_endpoint(self):
        return (
            self.settings.AuthEndpoint
            if self.settings.AuthEndpoint
            else default_auth_endpoint
        )

    def authenticate(self) -> bool:
        """Establishes connection with the server.

        If connection is successful, updates local state with API endpoints, emits a signal with
        organization and event information for the UI, then returns `True`

        Returns `False` otherwise.
        """
        host = self.get_host()
        endpoint = self.get_auth_endpoint()
        url = urljoin(host, endpoint)
        key = self.settings.ApiKey

        try:

            r = requests.post(
                url,
                json={"apiKey": key},
            )

            if r.status_code != 200:
                self.log_message.emit(
                    ERROR,
                    f"Unable to authenticate. Server response {r.status_code:d}: {r.text}",
                )
                return False

            # validate response
            data = json.loads(r.content)
            if "org" in data and all(
                x in data["org"] for x in ("id", "name", "slug", "apis")
            ):
                self.state = data
                return True

        except Exception:
            self.log_message.emit(ERROR, format_exc())

        self.log_message.emit(ERROR, "Unable to authenticate")
        return False

    def upload_results(self, result_data: list[dict[str, Any]], close=False) -> bool:
        if not self.state:
            raise RuntimeError("Connection to server not established, unable to upload")

        host = self.get_host()
        endpoint = self.state["org"]["apis"]["close-event" if close else "live-timing"]
        url = urljoin(host, endpoint)
        api_key = self.settings.ApiKey
        timestamp = datetime.now().astimezone().isoformat()

        self.log_message.emit(
            DEBUG, f"Uploading results to <tt>{url}</tt> at <tt>{timestamp}</tt>"
        )
        headers = {
            "rr-ingest-api-key": api_key,
            "rr-results-ts": timestamp,
            "Content-Type": "application/json",
        }
        r = requests.post(
            url,
            headers=headers,
            json=result_data,
        )

        if r.status_code != 200:
            fail_type = "close event" if close else "upload results"
            msg = f"Failed to {fail_type} ([{r.status_code:d}] {r.text})"
            self.log_message.emit(WARNING, msg)

        return r.status_code == 200

    @Slot()
    def queue_event_close(self):
        self.close_event_flag = True

    @Slot()
    def queue_force_update(self):
        self.force_update_flag = True

    @Slot()
    def run(self):

        self.log_message.emit(DEBUG, "Worker thread starting")

        # authenticate with server
        if not self.authenticate():
            return

        # update UI
        try:
            self.connected.emit(
                self.state["org"]["name"], "TODO: get event from server"
            )
        except KeyError:
            self.log_message.emit(ERROR, "Invalid state, unable to start watcher")
            self.log_message.emit(ERROR, f"State: {str(self.state)}")
            return

        fpath = Path(self.settings.value("ResultsPath"))

        if not fpath.exists():
            raise FileNotFoundError()

        last_modified = datetime(
            1, 1, 1, tzinfo=timezone.utc
        )  # force update upon entry
        consecutive_failures = 0

        while True:

            # force one final update if event closure requested
            if self.close_event_flag:
                self.force_update_flag = True

            if consecutive_failures > max_allowed_failures:
                self.log_message.emit(
                    ERROR,
                    f"{max_allowed_failures:d} consecutive upload failures, killing upload worker",
                )
                return

            if self.isInterruptionRequested():
                self.state = {}
                self.log_message.emit(DEBUG, "Worker thread exiting by user request")
                return

            mtime = datetime.fromtimestamp(
                fpath.stat().st_mtime, timezone.utc
            ).astimezone()

            # skip parsing if file has not been modified since last upload and not forcing
            if mtime <= last_modified and not self.force_update_flag:
                continue

            try:
                self.log_message.emit(DEBUG, f"Parsing results file at {fpath}")
                results = parse_axware_live_results(fpath)

                self.log_message.emit(DEBUG, "Sanitizing results")
                results = self.sanitize_data(results)

                if self.upload_results(results, close=self.close_event_flag):
                    self.log_message.emit(
                        INFO,
                        f"Results last generated at {mtime.strftime('%H:%M')}"
                        + f" | Last Uploaded at {datetime.now().strftime('%H:%M')}",
                    )
                    last_modified = mtime
                    consecutive_failures = 0

                    if self.force_update_flag:
                        self.notification.emit(
                            f'Forced update successful at {datetime.now().strftime("%H:%M")}'
                        )
                    self.force_update_flag = False

                    # kill worker if event closed successfully
                    if self.close_event_flag:
                        self.close_event_flag = False
                        self.requestInterruption()

                # clear flag if event closure failed
                elif self.close_event_flag:
                    self.close_event_flag = False

            # on any errors, continue to watch, just log error and wait for another update
            except Exception as e:
                self.log_message.emit(ERROR, format_exc())
                consecutive_failures += 1
                continue

    @property
    def CanRun(self) -> bool:
        return bool(self.settings.ApiKey) and Path(self.settings.ResultsPath).exists()
