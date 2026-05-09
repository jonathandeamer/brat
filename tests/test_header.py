"""Unit tests for the block-header byte builder (addendum §1)."""
from tests._lib.header import block_header, LIME_BG, BLACK_FG, RESET


def test_ansi_constants():
    assert LIME_BG == b"\x1b[48;2;138;206;0m"
    assert BLACK_FG == b"\x1b[30m"
    assert RESET == b"\x1b[0m"


def test_short_filename_pads_to_width_50():
    out = block_header("readme.md")
    expected = (
        LIME_BG + b" " * 50 + RESET + b"\n"
        + LIME_BG + BLACK_FG + b"  readme.md  " + b" " * 37 + RESET + b"\n"
        + LIME_BG + b" " * 50 + RESET + b"\n"
    )
    assert out == expected


def test_uppercase_filename_is_lowercased():
    out = block_header("README.MD")
    assert b"  readme.md  " in out
    assert b"README.MD" not in out


def test_long_filename_grows_block_with_no_trailing_pad():
    name = "x" * 47  # len=47 -> width=51, trailing pad = 0
    out = block_header(name)
    expected = (
        LIME_BG + b" " * 51 + RESET + b"\n"
        + LIME_BG + BLACK_FG + b"  " + name.encode() + b"  " + RESET + b"\n"
        + LIME_BG + b" " * 51 + RESET + b"\n"
    )
    assert out == expected
