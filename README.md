# hard_copy_paste

Aplicativo Tkinter que digita um texto, caractere por caractere, na janela que estiver ativa após uma contagem regressiva.

## Recursos

- Intervalo configurável entre caracteres (padrão: 700 ms).
- Tempo para posicionar o cursor (padrão: 10 segundos).
- Suporte a acentos e caracteres PT-BR no Windows e no Linux/X11.
- `Enter` para quebras de linha e `Tab` para tabulações.
- Interrupção pelo botão **Parar**, pela tecla global `Esc` ou pelo fail-safe do PyAutoGUI (mouse no canto superior esquerdo).
- Progresso acumulado e histórico rolável.

## Linux (Ubuntu/X11)

```bash
sudo apt install python3-tk xdotool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Confirme a sessão gráfica:

```bash
echo $XDG_SESSION_TYPE
```

O resultado esperado é `x11`. Wayland não é suportado nesta versão.

## Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Uso

1. Digite ou cole o texto na área principal.
2. Ajuste os tempos, se necessário.
3. Clique em **Iniciar**.
4. Durante a contagem, clique na janela e no campo que receberá o texto.
5. Para interromper, pressione `Esc`, use **Parar** ou mova o mouse ao canto superior esquerdo.

> Alguns aplicativos executados como administrador no Windows podem bloquear entradas vindas de um programa sem elevação. Nesse caso, execute ambos com o mesmo nível de permissão.

