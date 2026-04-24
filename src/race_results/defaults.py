from datetime import datetime
from pathlib import Path

default_app_guid = "3D7E4601-5769-48C0-9698-69F0807E61B3"
default_host = "https://race-results.live"
default_auth_endpoint = "api/timing-client/auth"
default_cfg_fpath = Path.home() / "race-results.ini"
default_log_fpath = (
    Path.home()
    / ".race-results-client"
    / f'{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.log'
)

results_file_watch_timeout_min = 5
max_allowed_failures = 10

help_permalink = "https://github.com/Shamtam/race-results-client/blob/40db16075cf10b8f02abd12d188a4410322369a1/doc/EVENT_SETUP.md"
