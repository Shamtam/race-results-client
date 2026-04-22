import json
import requests

from logging import ERROR, DEBUG, INFO, WARNING
from datetime import datetime, timezone
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Slot, Signal
from traceback import format_exc
from typing import Any, Optional, Tuple
from urllib.parse import urljoin

from .axware.parser import (
    parse_axware_live_results,
    parse_axware_heats_txt,
    ResultsParseError,
    HeatsParseError,
)
from .defaults import default_host, default_auth_endpoint, max_allowed_failures
from .settings import SettingsStore


class ServerUploadError(Exception):
    def __init__(self, server_response: dict[str, Any]) -> None:
        self.data = server_response


class NoCurrentEvent(Exception):
    pass


class CloseEventError(ServerUploadError):
    pass


class ResultUploadError(ServerUploadError):
    pass


class TerminateWorker(Exception):
    pass


class ResultsFileWatcher(QThread):
    connected = Signal(dict)
    log_message = Signal(int, str)
    notification = Signal(str)

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

    def confirm_termination(self):
        self.log_message.emit(DEBUG, "Worker thread exiting by user request")
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

            if (
                "org" in data
                and any(x in data for x in ("event", "events"))
                and all(x in data["org"] for x in ("id", "name", "slug", "apis"))
            ):

                # latest multi-event server schema
                if "events" in data and not data["events"]:
                    raise NoCurrentEvent

                elif "events" in data:
                    self.current_event = (
                        data["events"][0] if len(data["events"]) == 1 else {}
                    )

                # TODO: deprecated single-event schema
                else:
                    if not data['event']:
                        raise NoCurrentEvent
                    
                    self.current_event = data["event"]

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

    def upload_results(
        self, result_data: list[dict[str, Any]], close=False
    ) -> Tuple[bool, dict[str, Any]]:

        if any(not x for x in (self.state, self.current_event)):
            raise RuntimeError(
                "Connection to server not established or current event not determined, unable to upload"
            )

        host = self.get_host()
        endpoint_base = self.state["org"]["apis"][
            "close-event" if close else "live-timing"
        ]

        # latest multi-event server schema
        if "events" in self.state:
            event_id = self.current_event["eventId"]
            endpoint = f"{endpoint_base}/{event_id}"

        # TODO: deprecated single-event schema
        else:
            endpoint = endpoint_base

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

        # latest multi-event server schema
        if "events" in self.state:
            event_id = self.current_event["eventId"]
            endpoint = f"{endpoint_base}/{event_id}"

        # TODO: deprecated single-event schema
        else:
            endpoint = endpoint_base

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

        # prepare results watcher loop
        results_fpath = Path(self.settings.value("ResultsPath"))
        heats_fpath = Path(self.settings.value("HeatsPath"))

        if not results_fpath.exists():
            self.log_message.emit(
                ERROR, f'Unable to find results file "{results_fpath}"'
            )
            self.confirm_termination()
            return

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

        # force update upon entry
        last_modified = datetime(1, 1, 1, tzinfo=timezone.utc)
        consecutive_failures = 0

        # begin main worker loop
        while True:

            mtime = datetime.fromtimestamp(
                results_fpath.stat().st_mtime, timezone.utc
            ).astimezone()

            try:

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

                # try to parse and upload run/work heat assignments first, if needed
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

            finally:
                last_modified = mtime

    @property
    def CanRun(self) -> bool:
        return bool(self.settings.ApiKey) and Path(self.settings.ResultsPath).exists()
