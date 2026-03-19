from enum import Enum


class Notation(Enum):
    """La clase notaciones recopila diferentes notaciones binarias. Al definir el tipo se accede por `.value`."""

    LIL_ENDIAN = "little-endian"
    BIG_ENDIAN = "big-endian"
    GRAY_CODE = "gray-code"
    SIGN_MAGNITUDE = "sign-magnitude"
    TWOS_COMPLEMENT = "two's-complement"
