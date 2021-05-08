from typing import Optional

from api.security import Security

_security: Optional[Security] = None


def security() -> Security:
    if _security is None:
        raise Exception("Initialization error")
    return _security
