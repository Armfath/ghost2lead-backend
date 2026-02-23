from datetime import datetime, date


def timestamp_to_str_or_none(val: datetime | date | None) -> str | None:
    if val is None:
        return None
    return val.isoformat()
