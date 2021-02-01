from base64 import b64encode
from datetime import datetime

import pytz


def now_in_utc() -> datetime:
    return datetime.now(tz=pytz.utc)


def bytes_to_str_base64(bytes_to_decode: bytes) -> str:
    return b64encode(bytes_to_decode).decode("utf-8")
