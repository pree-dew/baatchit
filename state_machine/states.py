from enum import Enum


class Stage(str, Enum):
    VENTING = "venting"
    INTERVENING = "intervening"
    MONITORING = "monitoring"
    CHECKING_IN = "checking_in"
    CLOSING = "closing"
