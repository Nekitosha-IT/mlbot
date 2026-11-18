import json
import os
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import psutil
import requests

APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "NekitoshaAutoFarm"
APP_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = APP_DIR / "agent-state.json"
DEFAULT_API = "https://YOUR-WORKER.workers.dev"

class AgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nekitosha AutoFarm Agent")
        self.root.geometry("620x510")
        self.root.minsize(560, 460)
        self.token = ""
        self.agent_id = ""
        self.running = False
        self.worker = None
        self.api = DEFAULT_API
        self.processes = []
        self.load_state()
        self.build_ui()
        self.refresh_processes()
        if self.token:
            self.status.set("Сохранён токен Agent. Проверь API и подключение.")
            self.start_heartbeat()

    def load_state(self):
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            self.token = data.get("token", "")
            self.agent_id = data.get("agentId", "")
            self.api = data.get("api", DEFAULT_API)
        except Exception:
            pass

    def save_state(self):
        STATE_FILE.write_text(json.dumps({"token": self.token, "agentId": self.agent_id, "api": self.api}, ensure_ascii=False), encoding="utf-8")

    def build_ui(self):
        pad = {"padx": 12, "pady": 6}
        frame = ttk.Frame(self.root, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="NEKITOSHA AUTOFARM", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Windows companion · My Lands Steam", foreground="#6f8aa6").pack(anchor="w", pady=(0, 12))
        ttk.Label(frame, text="Адрес API (Cloudflare Worker)").pack(anchor="w")
        self.api_var = tk.StringVar(value=self.api)
        ttk.Entry(frame, textvariable=self.api_var).pack(fill="x", **pad)
        ttk.Label(frame, text="Одноразовый код из веб-кабинета").pack(anchor="w")
        self.code_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.code_var).pack(fill="x", **pad)
        ttk.Button(frame, text="Привязать Agent по коду", command=self.pair).pack(anchor="w", **pad)
        ttk.Separator(frame).pack(fill="x", pady=10)
        row = ttk.Frame(frame); row.pack(fill="x")
        ttk.Label(row, text="Процесс My Lands").pack(side="left")
        ttk.Button(row, text="Обновить список", command=self.refresh_processes).pack(side="right")
        self.process_var = tk.StringVar()
        self.process_box = ttk.Combobox(frame, textvariable=self.process_var, state="readonly")
        self.process_box.pack(fill="x", **pad)
        self.status = tk.StringVar(value="Не подключено")
        ttk.Label(frame, textvariable=self.status, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=8)
        ttk.Label(frame, text="Agent обнаруживает процесс MyLands.exe и синхронизирует настройки аккаунта. Он не читает память игры, не перехватывает трафик и не отправляет игровые команды.", wraplength=560, foreground="#9aabc0").pack(anchor="w", pady=8)
        buttons = ttk.Frame(frame); buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Подключить выбранный процесс", command=self.connect_process).pack(side="left")
        ttk.Button(buttons, text="Отключить Agent", command=self.disconnect).pack(side="left", padx=8)
        self.log = tk.Text(frame, height=7, wrap="word", bg="#101a27", fg="#dce8f7", insertbackground="white")
        self.log.pack(fill="both", expand=True, pady=(8, 0))
        self.api_var.set(self.api)

    def write_log(self, text):
        stamp = time.strftime("%H:%M:%S")
        self.root.after(0, lambda: (self.log.insert("end", f"[{stamp}] {text}\n"), self.log.see("end")))

    def refresh_processes(self):
        found = []
        for p in psutil.process_iter(["pid", "name", "exe"]):
            try:
                name = (p.info.get("name") or "").lower()
                if name == "mylands.exe" or "mylands" in name:
                    found.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.processes = found
        values = [f'{x["name"]} · PID {x["pid"]}' for x in found]
        self.process_box["values"] = values
        if values and not self.process_var.get():
            self.process_var.set(values[0])
        self.status.set(f"Найдено процессов My Lands: {len(values)}")
        self.write_log(f"Найдено процессов: {len(values)}")

    def pair(self):
        api = self.api_var.get().strip().rstrip("/")
        code = self.code_var.get().strip()
        if not api.startswith("https://") or "YOUR-WORKER" in api:
            messagebox.showerror("API не настроен", "Сначала разверни Cloudflare Worker и укажи его URL.")
            return
        if len(code) != 6 or not code.isdigit():
            messagebox.showerror("Код", "Введи шестизначный код из веб-кабинета.")
            return
        self.api = api
        try:
            selected = self.process_var.get()
            pid = int(selected.rsplit("PID ", 1)[1]) if "PID " in selected else 0
            proc = next((p for p in self.processes if p["pid"] == pid), {})
            res = requests.post(api + "/api/agent/pair", json={"code": code, "name": os.environ.get("COMPUTERNAME", "Windows Agent"), "processName": proc.get("name", ""), "pid": pid}, timeout=15)
            res.raise_for_status()
            data = res.json()
            self.token = data["token"]
            self.agent_id = data["agentId"]
            self.save_state()
            self.write_log("Agent привязан к аккаунту.")
            self.start_heartbeat()
        except Exception as exc:
            messagebox.showerror("Ошибка подключения", str(exc))
            self.write_log(f"Ошибка привязки: {exc}")

    def connect_process(self):
        selected = self.process_var.get()
        if not selected:
            self.refresh_processes()
            return
        self.write_log("Выбран " + selected)
        self.send_heartbeat()

    def start_heartbeat(self):
        if self.running:
            return
        self.running = True
        self.worker = threading.Thread(target=self.heartbeat_loop, daemon=True)
        self.worker.start()

    def heartbeat_loop(self):
        while self.running and self.token:
            try:
                self.send_heartbeat()
                r = requests.get(self.api + "/api/agent/config", headers={"Authorization": "Bearer " + self.token}, timeout=15)
                r.raise_for_status()
                config = r.json()
                self.write_log(f"Синхронизировано: правил {len(config.get('rules', []))}, шаблонов армий {len(config.get('armies', []))}.")
            except Exception as exc:
                self.write_log(f"Синхронизация: {exc}")
            time.sleep(25)

    def send_heartbeat(self):
        if not self.token:
            return
        selected = self.process_var.get()
        pid = int(selected.rsplit("PID ", 1)[1]) if "PID " in selected else 0
        proc = next((p for p in self.processes if p["pid"] == pid), {})
        alive = False
        if pid:
            try:
                psutil.Process(pid); alive = True
            except psutil.Error:
                pass
        try:
            r = requests.post(self.api + "/api/agent/heartbeat", headers={"Authorization": "Bearer " + self.token}, json={"processName": proc.get("name", ""), "pid": pid, "running": alive}, timeout=10)
            r.raise_for_status()
            self.root.after(0, lambda: self.status.set("API подключён · процесс " + ("найден" if alive else "не выбран/не найден")))
        except Exception as exc:
            self.write_log(f"Heartbeat: {exc}")

    def disconnect(self):
        self.running = False
        self.token = ""
        self.agent_id = ""
        self.save_state()
        self.status.set("Agent отключён локально. Удали устройство в кабинете для полного отзыва.")
        self.write_log("Локальный Agent остановлен.")

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AgentApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
