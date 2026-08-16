"""Digitação Unicode no Windows por meio da API SendInput."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


def _send_utf16_unit(unit: int, key_up: bool = False) -> None:
    flags = KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if key_up else 0)
    event = INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(0, unit, flags, 0, None),
    )
    sent = ctypes.windll.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT))
    if sent != 1:
        raise ctypes.WinError()


def type_character(character: str) -> None:
    """Envia um caractere como unidades UTF-16, inclusive pares substitutos."""
    encoded = character.encode("utf-16-le")
    for offset in range(0, len(encoded), 2):
        unit = int.from_bytes(encoded[offset : offset + 2], "little")
        _send_utf16_unit(unit)
        _send_utf16_unit(unit, key_up=True)

