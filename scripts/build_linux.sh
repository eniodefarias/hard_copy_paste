#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Erro: $PYTHON_BIN não foi encontrado."
    exit 1
fi

echo "Instalando/atualizando dependências de build..."
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt pyinstaller

echo "Gerando executável Linux..."
"$PYTHON_BIN" -m PyInstaller \
    --noconfirm \
    --clean \
    --onefile \
    --windowed \
    --name hard_copy_paste \
    --hidden-import platform_typers.linux_typer \
    --hidden-import platform_typers.windows_typer \
    --collect-submodules pynput \
    main.py

echo
echo "Build concluído: $PROJECT_DIR/dist/hard_copy_paste"
echo "Observação: a máquina que executar o programa precisa de X11 e xdotool."

