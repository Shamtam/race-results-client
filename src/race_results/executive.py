import json
import requests
import time

from logging import ERROR, DEBUG, INFO, WARNING
from datetime import datetime, timezone, timedelta
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Slot, Signal
from traceback import format_exc
from typing import Any, Tuple
from urllib.parse import urljoin

from .axware.parser import (
    parse_axware_live_results,
    parse_axware_heats_txt,
    ResultsParseError,
    HeatsParseError,
)
from .defaults import (
    default_host,
    default_auth_endpoint,
    results_file_watch_timeout_min,
    max_allowed_failures,
)
from .settings import SettingsStore


class ServerUploadError(Exception):
    def __init__(self, server_response: dict[str, Any]) -> None:
        self.data = server_response


class CloseEventError(ServerUploadError):
    pass


class ResultUploadError(ServerUploadError):
    pass


class NoCurrentEvent(Exception):
    pass


class TerminateWorker(Exception):
    pass


class ResultsFileWatcher(QThread):
    connected = Signal(dict)
    log_message = Signal(int, str)
    notification = Signal(str)
    update_status = Signal(str)

    def __init__(self, parent: QObject, settings: SettingsStore):
        super().__init__(parent)
        self.settings = settings
        self._initialized = False

    def initialize(self):
        self.force_update_flag = False
        self.close_event_flag = False
        self.event_selected_flag = False
        self.skip_heats_upload = False
        self.state = {}
        self.current_event = {}
        self._initialized = True

    def confirm_termination(
        self,
        log_level: int = DEBUG,
        log_msg: str = "Worker thread exiting by user request",
    ):
        self.log_message.emit(log_level, log_msg)
        self._initialized = False

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

            if all(x in data for x in ("org", "events")) and all(
                x in data["org"] for x in ("id", "name", "slug", "apis")
            ):
                if not data["events"]:
                    raise NoCurrentEvent

                self.current_event = (
                    data["events"][0] if len(data["events"]) == 1 else {}
                )

                self.event_selected_flag = True if self.current_event else False
                self.state = data
                return True

        except NoCurrentEvent:
            self.log_message.emit(
                ERROR, "No current event configured on Race Results server!"
            )
            return False

        except Exception:
            self.log_message.emit(ERROR, format_exc())

        self.log_message.emit(ERROR, "Unable to authenticate")
        return False

    def wait_for_results_file(self) -> bool:

        results_fpath = Path(self.settings.value("ResultsPath"))

        if results_fpath.exists():
            return True

        else:

            start_time = datetime.now()
            current_time = datetime.now()

            self.update_status.emit(f'Waiting for "{results_fpath}" to be generated...')

            while current_time < start_time + timedelta(
                minutes=results_file_watch_timeout_min
            ):

                if self.isInterruptionRequested():
                    return False

                time.sleep(5)
                current_time = datetime.now()

                if results_fpath.exists():
                    return True

            self.log_message.emit(
                ERROR,
                (
                    f'Results file "{results_fpath}" does not exist after '
                    + f"{results_file_watch_timeout_min} minute timeout. "
                    + "Ensure AxWare live timing is enabled and exporting to the path specified"
                    + "in the Race Results configuration."
                ),
            )
            return False

    def upload_results(
        self, result_data: list[dict[str, Any]], close=False
    ) -> Tuple[bool, dict[str, Any]]:

        if any(not x for x in (self.state, self.current_event)):
            raise RuntimeError("Unable to connect to server or determine current event")

        host = self.get_host()
        endpoint_base = self.state["org"]["apis"][
            "close-event" if close else "live-timing"
        ]
        event_id = self.current_event["eventId"]
        endpoint = f"{endpoint_base}/{event_id}"

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

        is_success = r.status_code == 200
        response_data = {"status_code": r.status_code, **r.json()}
        return is_success, response_data

    def upload_heats(self, data: dict[str, list[str]]) -> Tuple[bool, dict[str, Any]]:
        if any(not x for x in (self.state, self.current_event)):
            raise RuntimeError(
                "Connection to server not established or current event not determined, unable to upload heats"
            )

        if "run-work" not in self.state["org"]["apis"]:
            return (
                False,
                {
                    "message": "Run/Work feature not enabled on server, skipping upload of run/work heat info"
                },
            )

        host = self.get_host()
        endpoint_base = self.state["org"]["apis"]["run-work"]
        event_id = self.current_event["eventId"]
        endpoint = f"{endpoint_base}/{event_id}"

        url = urljoin(host, endpoint)
        api_key = self.settings.ApiKey
        timestamp = datetime.now().astimezone().isoformat()

        self.log_message.emit(
            DEBUG,
            f"Uploading run/work heat information to <tt>{url}</tt> at <tt>{timestamp}</tt>",
        )
        headers = {
            "rr-ingest-api-key": api_key,
            "rr-results-ts": timestamp,
            "Content-Type": "application/json",
        }
        r = requests.post(
            url,
            headers=headers,
            json=data,
        )

        is_success = r.status_code == 200
        response_data = {"status_code": r.status_code, **r.json()}

        return is_success, response_data

    def process_heats(self):
        heats_fpath = Path(self.settings.value("HeatsPath"))

        if "run-work" not in self.state["org"]["apis"]:
            self.skip_heats_upload = True

        elif heats_fpath and not heats_fpath.exists():
            self.log_message.emit(
                WARNING, f'Unable to find run/work heat assignment file "{heats_fpath}"'
            )
            self.skip_heats_upload = True

        elif not heats_fpath:
            self.log_message.emit(
                WARNING, "No run/work heat assignment file specified, skipping upload"
            )
            self.skip_heats_upload = True

        if not self.skip_heats_upload:
            try:
                self.log_message.emit(DEBUG, "Parsing heats text file")
                heats_data = parse_axware_heats_txt(heats_fpath)
            except:
                raise HeatsParseError

            success, response = self.upload_heats(heats_data)
            if success:
                self.skip_heats_upload = True
            else:
                raise ServerUploadError(response)

    def generate_exception_messages(self, exc: Exception):
        msgs = {}

        if isinstance(exc, ServerUploadError):
            # extra logging for server upload errors
            if isinstance(exc, ServerUploadError):
                response_data = exc.data

                if isinstance(exc, CloseEventError):
                    level = ERROR
                    fail_type = "close event"
                elif isinstance(exc, ResultUploadError):
                    level = ERROR
                    fail_type = "upload_results"
                else:
                    level = WARNING
                    fail_type = "upload run/work heat assignments"

                msg_base = f"Server error when trying to {fail_type}:"
                usr_msg = f"{msg_base} {response_data['message']}"
                dbg_msg = f"{msg_base} {response_data}"
                self.log_message.emit(DEBUG, dbg_msg)

                # invalid state response from server, kill watcher
                if response_data["status_code"] == 409:
                    self.log_message.emit(level, usr_msg)

                msgs[DEBUG] = dbg_msg
                msgs[WARNING] = usr_msg
        else:
            msgs[ERROR] = format_exc()

        for level, msg in msgs.items():
            self.log_message.emit(level, msg)

    @Slot()
    def queue_event_close(self):
        self.close_event_flag = True

    @Slot()
    def queue_force_update(self):
        self.force_update_flag = True

    @Slot(dict)
    def set_current_event(self, event_info: dict[str, Any]):
        self.current_event = event_info
        self.event_selected_flag = True

    @Slot()
    def run(self):

        self.log_message.emit(DEBUG, "Worker thread starting")

        if not self._initialized:
            self.initialize()

        # authenticate with server
        if not self.authenticate():
            return

        # update UI
        self.connected.emit(self.state)

        # wait for event selection, if necessary
        while not self.event_selected_flag:
            if self.isInterruptionRequested():
                self.confirm_termination()
                return

        # try to upload heats information
        try:
            self.process_heats()

        except Exception as e:
            self.generate_exception_messages(e)

            # invalid state response from server, kill watcher
            if isinstance(e, ServerUploadError):
                if e.data["status_code"] == 409:
                    self.confirm_termination()
                    return

        # prepare results watcher loop
        results_fpath = Path(self.settings.value("ResultsPath"))

        # force update upon entry
        last_modified = datetime(1, 1, 1, tzinfo=timezone.utc)
        consecutive_failures = 0

        # begin main worker loop
        while True:

            try:

                mtime = datetime.fromtimestamp(
                    results_fpath.stat().st_mtime, timezone.utc
                ).astimezone()

                # force one final update if event closure requested
                if self.close_event_flag:
                    self.force_update_flag = True

                if consecutive_failures > max_allowed_failures:
                    self.log_message.emit(
                        ERROR,
                        f"{max_allowed_failures:d} consecutive upload failures, killing upload worker",
                    )
                    self._initialized = False
                    return

                if self.isInterruptionRequested():
                    raise TerminateWorker

                # skip parsing if file has not been modified since last upload and not forcing
                if mtime <= last_modified and not self.force_update_flag:
                    continue
                else:
                    last_modified = mtime

                # issue specific warning if parsing fails
                try:
                    self.log_message.emit(
                        DEBUG, f"Parsing results file at {results_fpath}"
                    )
                    results = parse_axware_live_results(results_fpath)

                except ResultsParseError:
                    self.log_message.emit(
                        WARNING,
                        f"Error parsing {results_fpath}, ensure file exists and contains results!",
                    )
                    consecutive_failures += 1
                    if self.force_update_flag:
                        self.force_update_flag = False
                    continue

                except Exception:
                    raise

                success, response = self.upload_results(
                    results, close=self.close_event_flag
                )
                if success:
                    self.log_message.emit(
                        INFO,
                        f"Results last generated at {mtime.strftime('%H:%M')}"
                        + f" | Last Uploaded at {datetime.now().strftime('%H:%M')}",
                    )
                    self.update_status.emit("Watching results file")
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

                else:
                    # clear flag if event closure failed
                    if self.close_event_flag:
                        self.close_event_flag = False

                    raise ServerUploadError(response)

            except FileNotFoundError:
                self.log_message.emit(
                    WARNING,
                    f"Unable to find results file {results_fpath}. "
                    + f"Waiting up to {results_file_watch_timeout_min} minutes.",
                )

                if not self.wait_for_results_file():
                    return

                # reset last modified time if file (re-)appears
                last_modified = datetime(1, 1, 1, tzinfo=timezone.utc)
                continue

            except TerminateWorker:
                self.confirm_termination()
                return

            except Exception as e:

                # extra logging for server upload errors
                if isinstance(e, ServerUploadError):
                    response_data = e.data

                    if isinstance(e, CloseEventError):
                        level = ERROR
                        fail_type = "close event"
                    elif isinstance(e, ResultUploadError):
                        level = ERROR
                        fail_type = "upload_results"
                    else:
                        level = WARNING
                        fail_type = "upload run/work heat assignments"

                    msg_base = f"Server error when trying to {fail_type}:"
                    usr_msg = f"{msg_base} {response_data['message']}"
                    dbg_msg = f"{msg_base} {response_data}"
                    self.log_message.emit(DEBUG, dbg_msg)

                    # invalid state response from server, kill watcher
                    if response_data["status_code"] == 409:
                        self.log_message.emit(level, usr_msg)
                        self.confirm_termination()
                        return

                # on any errors, continue to watch, just log error and wait for another update
                else:
                    level = ERROR
                    usr_msg = format_exc()

                self.log_message.emit(level, usr_msg)
                consecutive_failures += 1
                continue

    @property
    def CanRun(self) -> bool:
        return bool(self.settings.ApiKey) and bool(self.settings.ResultsPath)
