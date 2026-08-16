from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk

import pyautogui
from pynput import keyboard

from platform_typers.factory import get_character_typer


class HardCopyPasteApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("hard_copy_paste")
        self.root.geometry("760x720")
        self.root.minsize(200, 600)

        self.cancel_event = threading.Event()
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.closed = False
        self.is_active = False
        self.type_character, self.validate_platform = get_character_typer()

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0

        self._build_gui()
        self._start_escape_listener()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(50, self._process_events)

    def _build_gui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=3)
        container.rowconfigure(7, weight=2)
        container.rowconfigure(9, weight=2)

        ttk.Label(container, text="Texto a digitar:").grid(row=0, column=0, sticky="w")
        self.input_text = scrolledtext.ScrolledText(container, wrap="word", height=10)
        self.input_text.grid(row=1, column=0, sticky="nsew", pady=(4, 10))

        self.options_frame = ttk.Frame(container)
        self.options_frame.grid(row=2, column=0, sticky="ew")

        self.options_frame.columnconfigure(0, weight=1)
        self.options_frame.columnconfigure(1, weight=1)

        self.interval_label = ttk.Label(
            self.options_frame,
            text="Intervalo entre caracteres (ms):",
        )

        self.interval_var = tk.StringVar(value="700")
        self.interval_entry = ttk.Spinbox(
            self.options_frame,
            from_=0,
            to=60_000,
            increment=100,
            textvariable=self.interval_var,
            width=6,
        )

        self.wait_label = ttk.Label(
            self.options_frame,
            text="Tempo de espera (segundos):",
        )

        self.wait_var = tk.StringVar(value="5")
        self.wait_entry = ttk.Spinbox(
        self.options_frame,
        from_=0,
        to=3600,
        increment=1,
        textvariable=self.wait_var,
        width=6,
    )
        
        
        self.interval_label.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 2),
        )

        self.interval_entry.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 8),
        )

        self.wait_label.grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 2),
        )

        self.wait_entry.grid(
            row=3,
            column=0,
            sticky="w",
        )
        
        
        
        buttons = ttk.Frame(container)
        buttons.grid(row=3, column=0, sticky="w", pady=12)
        self.start_button = ttk.Button(buttons, text="Iniciar", command=self.start)
        self.start_button.pack(side="left", padx=(0, 8))
        self.stop_button = ttk.Button(buttons, text="Parar", command=self.stop, state="disabled")
        self.stop_button.pack(side="left")

        self.status_var = tk.StringVar(value="Em espera")
        ttk.Label(container, text="Status:").grid(row=4, column=0, sticky="w")
        ttk.Label(container, textvariable=self.status_var).grid(row=5, column=0, sticky="w", pady=(2, 10))

        ttk.Label(container, text="Progresso da digitação:").grid(row=6, column=0, sticky="w")
        self.progress_text = scrolledtext.ScrolledText(container, wrap="word", height=7, state="disabled")
        self.progress_text.grid(row=7, column=0, sticky="nsew", pady=(4, 10))

        ttk.Label(container, text="Histórico:").grid(row=8, column=0, sticky="w")
        self.log_text = scrolledtext.ScrolledText(container, wrap="word", height=8, state="disabled")
        self.log_text.grid(row=9, column=0, sticky="nsew", pady=(4, 0))

        self._log("Aplicativo iniciado. Aguardando comando.")

    def _start_escape_listener(self) -> None:
        def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
            if key == keyboard.Key.esc:
                self.events.put(("stop", "ESC pressionado"))

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.daemon = True
        self.listener.start()

    def start(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        text = self.input_text.get("1.0", "end-1c")
        if not text:
            messagebox.showwarning("Texto vazio", "Digite um texto antes de iniciar.")
            return
        try:
            interval_ms = int(self.interval_var.get())
            wait_seconds = int(self.wait_var.get())
            if interval_ms < 0 or wait_seconds < 0:
                raise ValueError
            self.validate_platform()
        except ValueError:
            messagebox.showerror("Valor inválido", "Use números inteiros iguais ou maiores que zero.")
            return
        except RuntimeError as exc:
            messagebox.showerror("Ambiente incompatível", str(exc))
            return

        self.cancel_event.clear()
        self.is_active = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self._set_progress("")
        self._log(f"Comando iniciado: {len(text)} caracteres.")
        self.worker = threading.Thread(
            target=self._run_typing,
            args=(text, interval_ms / 1000, wait_seconds),
            daemon=True,
        )
        self.worker.start()

    def _run_typing(self, text: str, interval: float, wait_seconds: int) -> None:
        typed = ""
        try:
            for remaining in range(wait_seconds, 0, -1):
                self.events.put(("status", f"Iniciando em {remaining}..."))
                if self.cancel_event.wait(1):
                    self.events.put(("cancelled", typed))
                    return

            total = len(text)
            for index, character in enumerate(text, start=1):
                if self.cancel_event.is_set():
                    self.events.put(("cancelled", typed))
                    return
                pyautogui.position()  # também dispara o fail-safe no canto superior esquerdo
                if character == "\n":
                    pyautogui.press("enter")
                elif character == "\t":
                    pyautogui.press("tab")
                else:
                    self.type_character(character)
                typed += character
                display = f"Digitando ({index}/{total} caracteres):\n{typed}"
                self.events.put(("progress", display))
                self.events.put(("status", f"Digitando {index}/{total}"))
                if interval and self.cancel_event.wait(interval):
                    self.events.put(("cancelled", typed))
                    return
            self.events.put(("completed", typed))
        except pyautogui.FailSafeException:
            self.events.put(("failed", "Interrompido pelo fail-safe do mouse."))
        except Exception as exc:
            self.events.put(("failed", f"Erro durante a digitação: {exc}"))

    def stop(self, reason: str = "Interrompido pelo usuário") -> None:
        if self.worker and self.worker.is_alive():
            self.cancel_event.set()
            self._log(reason)
        self.is_active = False
        self._set_idle()

    def _set_idle(self) -> None:
        self.status_var.set("Em espera")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def _process_events(self) -> None:
        if self.closed:
            return
        try:
            while True:
                event, value = self.events.get_nowait()
                if event == "status" and self.is_active:
                    self.status_var.set(str(value))
                elif event == "progress" and self.is_active:
                    self._set_progress(str(value))
                elif event == "stop":
                    self.stop(str(value))
                elif event == "completed":
                    self.is_active = False
                    self._log(f"Digitação concluída ({len(str(value))} caracteres):\n{value}")
                    self.status_var.set("Concluído")
                    self.start_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                elif event == "failed":
                    self.is_active = False
                    self._log(str(value))
                    self._set_idle()
                elif event == "cancelled" and value:
                    self._log(f"Trecho digitado antes da interrupção ({len(str(value))} caracteres):\n{value}")
        except queue.Empty:
            pass
        self.root.after(50, self._process_events)

    def _set_progress(self, content: str) -> None:
        self.progress_text.configure(state="normal")
        self.progress_text.delete("1.0", "end")
        self.progress_text.insert("end", content)
        self.progress_text.see("end")
        self.progress_text.configure(state="disabled")

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def close(self) -> None:
        self.closed = True
        self.cancel_event.set()
        self.listener.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    HardCopyPasteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
