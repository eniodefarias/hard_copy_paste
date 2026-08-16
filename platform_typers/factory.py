"""Seleciona automaticamente a implementação adequada ao sistema."""

from __future__ import annotations

import platform
from collections.abc import Callable


def get_character_typer() -> tuple[Callable[[str], None], Callable[[], None]]:
    system = platform.system()
    if system == "Windows":
        from platform_typers.windows_typer import type_character

        return type_character, lambda: None
    if system == "Linux":
        from platform_typers.linux_typer import type_character, validate_environment

        return type_character, validate_environment
    raise RuntimeError(f"Sistema operacional não suportado: {system}")

