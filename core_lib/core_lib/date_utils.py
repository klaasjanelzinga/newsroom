from datetime import datetime

import pytz


def now_in_utc() -> datetime:
    return datetime.now(tz=pytz.utc)
