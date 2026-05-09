"""Byte-exact block-header builder per addendum §1."""

LIME_BG = b"\x1b[48;2;138;206;0m"
BLACK_FG = b"\x1b[30m"
RESET = b"\x1b[0m"


def block_header(filename: str) -> bytes:
    """Return the three-row ANSI block header for filename.

    Geometry: width = max(50, len(name) + 4); 2-space gutters either side
    of the (lowercased) filename, then space-pad to width.
    """
    name = filename.lower()
    width = max(50, len(name) + 4)
    pad = width - len(name) - 4
    blank_row = LIME_BG + b" " * width + RESET + b"\n"
    name_row = (
        LIME_BG + BLACK_FG
        + b"  " + name.encode() + b"  " + b" " * pad
        + RESET + b"\n"
    )
    return blank_row + name_row + blank_row
