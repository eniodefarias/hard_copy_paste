"""Digitação Unicode no Linux usando xdotool em uma sessão X11."""

from __future__ import annotations

import os
import shutil
import subprocess


def validate_environment() -> None:
    if os.environ.get("XDG_SESSION_TYPE", "x11").lower() != "x11":
        raise RuntimeError("No Linux, o hard_copy_paste requer uma sessão X11.")
    if shutil.which("xdotool") is None:
        raise RuntimeError("O xdotool não foi encontrado. Instale com: sudo apt install xdotool")


def type_character(character: str) -> None:
    """Digita exatamente um caractere UTF-8 na janela ativa."""
    validate_environment()
    subprocess.run(
        ["xdotool", "type", "--clearmodifiers", "--delay", "0", "--", character],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )

