from pathlib import Path
from datetime import datetime

default_host = 'https://www.race-results.org'
default_auth_endpoint = 'api/timing-client/auth'
default_cfg_fpath = Path.home() / 'race-results.ini'
default_log_fpath = Path.home() / '.race-results-client' / f'{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.log'
max_allowed_failures = 10