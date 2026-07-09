# gui.py
import customtkinter as ctk
import threading
from runtime_data import RUNTIMES
from checker import get_missing
from downloader import download_all
from installer import install_all

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VC++ Runtime Auto Installer")
        self.geometry("720x420")

        self.sidebar = ctk.CTkFrame(self, width=180)
        self.sidebar.pack(side="left", fill="y")

        self.main = ctk.CTkFrame(self)
        self.main.pack(side="right", expand=True, fill="both")

        self.title_lbl = ctk.CTkLabel(self.sidebar, text="VC++ Tool", font=("Arial",18))
        self.title_lbl.pack(pady=20)

        self.btn = ctk.CTkButton(self.sidebar, text="检测并安装", command=self.start)
        self.btn.pack(pady=10)

        self.log = ctk.CTkTextbox(self.main, width=500, height=250)
        self.log.pack(pady=20)

        self.progress = ctk.CTkProgressBar(self.main, width=400)
        self.progress.pack(pady=10)
        self.progress.set(0)

    def write(self, msg):
        self.log.insert("end", msg+"\n")
        self.log.see("end")

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        self.write("检测运行库...")
        miss = get_missing(RUNTIMES)

        if not miss:
            self.write("无需安装")
            return

        self.write(f"缺失 {len(miss)} 项")

        def cb(n,c,t):
            if t:
                self.progress.set(c/t)

        files = download_all(miss, cb=cb)

        self.write("下载完成，安装中...")

        res = install_all(files, miss)

        self.write("完成:")
        for k,v in res.items():
            self.write(f"{k}:{v}")

if __name__ == "__main__":
    App().mainloop()