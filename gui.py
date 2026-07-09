# gui.py
import customtkinter as ctk
import threading
from runtime_data import RUNTIMES
from checker import check_installed, is_supported_arch
from downloader import download_all
from installer import install_all

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VC++ Runtime Auto Installer")
        self.geometry("980x640")
        self.minsize(880, 560)
        self.configure(fg_color=("#f4f7fb", "#111827"))

        self.runtime_rows = {}
        self.is_busy = False

        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=("#e7edf7", "#0b1220"))
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color=("#f8fafc", "#111827"))
        self.main.pack(side="right", expand=True, fill="both")

        self.title_lbl = ctk.CTkLabel(self.sidebar, text="VC++ Runtime", font=("Segoe UI", 23, "bold"), anchor="w")
        self.title_lbl.pack(fill="x", padx=22, pady=(26, 4))

        self.subtitle_lbl = ctk.CTkLabel(self.sidebar, text="自动检测 / 选择安装 / 静默执行", font=("Segoe UI", 12), text_color=("#52637a", "#94a3b8"), anchor="w")
        self.subtitle_lbl.pack(fill="x", padx=22, pady=(0, 24))

        self.scan_btn = ctk.CTkButton(self.sidebar, text="重新检测", height=40, command=self.scan)
        self.scan_btn.pack(fill="x", padx=22, pady=(0, 10))

        self.select_missing_btn = ctk.CTkButton(self.sidebar, text="选择缺失项", height=40, fg_color=("#334155", "#334155"), command=self.select_missing)
        self.select_missing_btn.pack(fill="x", padx=22, pady=(0, 10))

        self.select_all_btn = ctk.CTkButton(self.sidebar, text="全选", height=40, fg_color=("#475569", "#475569"), command=lambda: self.set_all(True))
        self.select_all_btn.pack(fill="x", padx=22, pady=(0, 10))

        self.clear_btn = ctk.CTkButton(self.sidebar, text="清空选择", height=40, fg_color=("#64748b", "#64748b"), command=lambda: self.set_all(False))
        self.clear_btn.pack(fill="x", padx=22, pady=(0, 22))

        self.install_btn = ctk.CTkButton(self.sidebar, text="安装已选择", height=46, font=("Segoe UI", 14, "bold"), command=self.start)
        self.install_btn.pack(fill="x", padx=22, pady=(0, 14))

        self.status_lbl = ctk.CTkLabel(self.sidebar, text="等待检测", font=("Segoe UI", 12), text_color=("#52637a", "#94a3b8"), anchor="w")
        self.status_lbl.pack(fill="x", padx=22, pady=(6, 0))

        self.header = ctk.CTkFrame(self.main, fg_color="transparent")
        self.header.pack(fill="x", padx=28, pady=(24, 12))

        self.heading = ctk.CTkLabel(self.header, text="选择要安装的 VC++ 运行库", font=("Segoe UI", 24, "bold"), anchor="w")
        self.heading.pack(side="left", fill="x", expand=True)

        self.count_lbl = ctk.CTkLabel(self.header, text="0 项", font=("Segoe UI", 13), text_color=("#52637a", "#94a3b8"))
        self.count_lbl.pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self.main, height=310, fg_color=("#ffffff", "#172033"), corner_radius=10)
        self.list_frame.pack(fill="both", expand=True, padx=28, pady=(0, 14))

        self.footer = ctk.CTkFrame(self.main, fg_color="transparent")
        self.footer.pack(fill="x", padx=28, pady=(0, 24))

        self.progress = ctk.CTkProgressBar(self.footer, height=12)
        self.progress.pack(fill="x", pady=(0, 12))
        self.progress.set(0)

        self.log = ctk.CTkTextbox(self.footer, height=145, font=("Consolas", 12), fg_color=("#ffffff", "#0f172a"), corner_radius=10)
        self.log.pack(fill="x")

        self.build_runtime_list()
        self.scan()

    def ui(self, fn, *args, **kwargs):
        self.after(0, lambda: fn(*args, **kwargs))

    def write(self, msg):
        self.log.insert("end", msg+"\n")
        self.log.see("end")

    def build_runtime_list(self):
        for index, runtime in enumerate(RUNTIMES):
            row = ctk.CTkFrame(self.list_frame, fg_color=("#f8fafc", "#1f2937"), corner_radius=8)
            row.grid(row=index, column=0, sticky="ew", padx=10, pady=6)
            row.grid_columnconfigure(1, weight=1)

            variable = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(row, text="", width=24, variable=variable)
            checkbox.grid(row=0, column=0, padx=(14, 8), pady=12)

            name = ctk.CTkLabel(row, text=runtime["name"], font=("Segoe UI", 14, "bold"), anchor="w")
            name.grid(row=0, column=1, sticky="w", pady=(10, 0))

            detail = ctk.CTkLabel(row, text=f'{runtime["arch"]} | {runtime["offline_path"]}', font=("Segoe UI", 11), text_color=("#64748b", "#94a3b8"), anchor="w")
            detail.grid(row=1, column=1, sticky="w", pady=(0, 10))

            state = ctk.CTkLabel(row, text="待检测", width=76, height=26, corner_radius=13, fg_color=("#e2e8f0", "#334155"), text_color=("#334155", "#e2e8f0"))
            state.grid(row=0, column=2, rowspan=2, padx=14)

            self.runtime_rows[runtime["id"]] = {
                "runtime": runtime,
                "variable": variable,
                "checkbox": checkbox,
                "state": state,
                "installed": False,
                "supported": True,
            }

        self.list_frame.grid_columnconfigure(0, weight=1)

    def start(self):
        if self.is_busy:
            return
        selected = [row["runtime"] for row in self.runtime_rows.values() if row["variable"].get() and row["supported"]]
        if not selected:
            self.write("请先选择要安装的运行库")
            return
        self.set_busy(True)
        threading.Thread(target=self.run, args=(selected,), daemon=True).start()

    def scan(self):
        if self.is_busy:
            return
        self.set_busy(True)
        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        self.ui(self.write, "检测运行库状态...")
        missing_count = 0
        supported_count = 0

        for runtime_id, row in self.runtime_rows.items():
            runtime = row["runtime"]
            supported = is_supported_arch(runtime)
            installed = check_installed(runtime) if supported else False
            missing_count += 1 if supported and not installed else 0
            supported_count += 1 if supported else 0
            self.ui(self.update_runtime_state, runtime_id, installed, supported)

        self.ui(self.status_lbl.configure, text=f"缺失 {missing_count} 项，可安装 {supported_count} 项")
        self.ui(self.count_lbl.configure, text=f"{supported_count} 项可用")
        self.ui(self.write, f"检测完成：缺失 {missing_count} 项")
        self.ui(self.set_busy, False)

    def update_runtime_state(self, runtime_id, installed, supported):
        row = self.runtime_rows[runtime_id]
        row["installed"] = installed
        row["supported"] = supported

        if not supported:
            row["state"].configure(text="不支持", fg_color=("#e5e7eb", "#374151"), text_color=("#6b7280", "#cbd5e1"))
            row["checkbox"].deselect()
            row["checkbox"].configure(state="disabled")
            return

        row["checkbox"].configure(state="normal")
        if installed:
            row["state"].configure(text="已安装", fg_color=("#dcfce7", "#14532d"), text_color=("#166534", "#bbf7d0"))
            row["checkbox"].deselect()
        else:
            row["state"].configure(text="缺失", fg_color=("#fee2e2", "#7f1d1d"), text_color=("#991b1b", "#fecaca"))
            row["checkbox"].select()

    def set_all(self, selected):
        for row in self.runtime_rows.values():
            if row["supported"]:
                row["variable"].set(selected)

    def select_missing(self):
        for row in self.runtime_rows.values():
            row["variable"].set(row["supported"] and not row["installed"])

    def set_busy(self, busy):
        self.is_busy = busy
        state = "disabled" if busy else "normal"
        for button in (self.scan_btn, self.select_missing_btn, self.select_all_btn, self.clear_btn, self.install_btn):
            button.configure(state=state)
        for row in self.runtime_rows.values():
            row["checkbox"].configure(state="disabled" if busy or not row["supported"] else "normal")
        if busy:
            self.status_lbl.configure(text="正在处理...")

    def update_progress(self, current, total):
        self.progress.set(0 if total == 0 else current / total)

    def run(self, selected):
        self.ui(self.write, f"准备安装 {len(selected)} 项，主窗口将保持显示")
        self.ui(self.progress.set, 0)

        try:
            def cb(n,c,t):
                if t:
                    self.ui(self.progress.set, c/t)

            files = download_all(selected, cb=cb)

            self.ui(self.write, "安装包准备完成，开始静默安装...")

            total = len(selected)
            completed = 0

            def install_cb(name, stage, code):
                nonlocal completed
                if stage == "start":
                    self.ui(self.write, f"静默安装中：{name}")
                else:
                    completed += 1
                    self.ui(self.write, f"{name}: 返回码 {code}")
                    self.ui(self.update_progress, completed, total)

            install_all(files, selected, cb=install_cb)

            self.ui(self.write, "安装流程完成，正在重新检测...")
            self.ui(self.progress.set, 1)
            self.ui(self.set_busy, False)
            self.ui(self.scan)
        except Exception as exc:
            self.ui(self.write, f"安装流程出错：{exc}")
            self.ui(self.set_busy, False)

if __name__ == "__main__":
    App().mainloop()