"""Utility helpers for vds app.

Contains small helpers (e.g. revision label increments) so they can be
unit-tested independently of models.
"""
import re


def _increment_numeric(numstr: str) -> str:
    """Increment numeric string preserving zero-padding."""
    width = len(numstr)
    try:
        newn = int(numstr) + 1
    except ValueError:
        return numstr
    return str(newn).zfill(width)


def _increment_alpha(alpha: str) -> str:
    """Simple per-character alphabetic increment: increase each char by one
    except that 'Z' and 'z' are left unchanged (preserve current behavior).
    This mirrors the existing logic the project uses and intentionally does
    not implement rollover (e.g. Z->AA).
    """
    newrev = []
    for ch in alpha:
        if ch in ('Z', 'z'):
            newrev.append(ch)
        else:
            newrev.append(chr(ord(ch) + 1))
    return ''.join(newrev)
