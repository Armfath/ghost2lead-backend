from enum import Enum


class EventName(str, Enum):
    EXPORTED_FILE = "exported_file"
    SIGNED_UP = "signed_up"
    VISIT = "visit"
    VIEWED_PRICING = "viewed_pricing"


class OrderBy(str, Enum):
    ASC = "ASC"
    DESC = "DESC"
