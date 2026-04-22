from datetime import datetime
from pathlib import Path

default_host = "https://race-results.live"
default_auth_endpoint = "api/timing-client/auth"
default_cfg_fpath = Path.home() / "race-results.ini"
default_log_fpath = (
    Path.home()
    / ".race-results-client"
    / f'{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.log'
)
max_allowed_failures = 10

help_permalink = "https://github.com/Shamtam/race-results-client/blob/40db16075cf10b8f02abd12d188a4410322369a1/doc/EVENT_SETUP.md"
