@echo off
setlocal

cd /d "%~dp0\.."

where python >nul 2>nul
if errorlevel 1 (
    echo Erro: python nao foi encontrado no PATH.
    exit /b 1
)

echo Instalando/atualizando dependencias de build...
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

echo Gerando executavel Windows...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name hard_copy_paste ^
    --hidden-import platform_typers.linux_typer ^
    --hidden-import platform_typers.windows_typer ^
    --collect-submodules pynput ^
    main.py

if errorlevel 1 (
    echo Build do Windows falhou.
    exit /b 1
)

echo.
echo Build concluido: %CD%\dist\hard_copy_paste.exe
endlocal

