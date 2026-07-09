"""Desktop interface for inspecting and installing VC++ runtime packages."""

from __future__ import annotations

import os
import platform
import threading
from datetime import datetime
from tkinter import TclError, messagebox

import customtkinter as ctk

from checker import check_installed, get_installed_version, is_supported_arch
from downloader import download_all, package_validation_error
from installer import RESTART_CODES, SUCCESS_CODES, install_all, install_result_text
from paths import resolve_project_path
from runtime_data import RUNTIMES, get_offline_sha256
from sysinfo import get_arch, is_windows
from version_utils import compare_versions, download_latest_package, get_cloud_package_info


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


COLORS = {
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "sidebar": ("#0f172a", "#0b1220"),
    "sidebar_surface": ("#1e293b", "#172033"),
    "main": ("#f4f7fb", "#101722"),
    "surface": ("#ffffff", "#182230"),
    "surface_muted": ("#f8fafc", "#1d2939"),
    "row": ("#fbfdff", "#1a2636"),
    "border": ("#dfe7f1", "#2b3a4e"),
    "text": ("#172033", "#f8fafc"),
    "muted": ("#64748b", "#a8b7ca"),
    "sidebar_text": ("#f8fafc", "#f8fafc"),
    "sidebar_muted": ("#a8b7ca", "#a8b7ca"),
}

STATUS_STYLES = {
    "installed": {
        "text": "已安装",
        "fg": ("#dcfce7", "#153b2e"),
        "text_color": ("#166534", "#bbf7d0"),
    },
    "missing": {
        "text": "待安装",
        "fg": ("#ffedd5", "#512d13"),
        "text_color": ("#9a3412", "#fed7aa"),
    },
    "unsupported": {
        "text": "不适用",
        "fg": ("#e2e8f0", "#334155"),
        "text_color": ("#475569", "#cbd5e1"),
    },
    "checking": {
        "text": "检测中",
        "fg": ("#dbeafe", "#1e3a5f"),
        "text_color": ("#1d4ed8", "#bfdbfe"),
    },
}


def format_size(size: int) -> str:
    """Format a byte count for the package-status column."""
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{int(size)} B"


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("VC++ Runtime Manager")
        self.geometry("1180x760")
        self.minsize(1000, 680)
        self.configure(fg_color=COLORS["main"])
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.runtime_rows: dict[str, dict] = {}
        self.is_busy = False
        self.is_closing = False
        self.restart_required = False
        self.theme_var = ctk.StringVar(value="跟随系统")

        self._build_sidebar()
        self._build_main()
        self.build_runtime_list()
        self.after(120, self.scan)

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self, width=254, corner_radius=0, fg_color=COLORS["sidebar"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(24, 22))

        mark = ctk.CTkLabel(
            brand,
            text="VC",
            width=42,
            height=42,
            corner_radius=8,
            fg_color=COLORS["accent"],
            text_color="#ffffff",
            font=("Segoe UI", 15, "bold"),
        )
        mark.pack(side="left", padx=(0, 11))

        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            brand_text,
            text="Runtime Manager",
            anchor="w",
            text_color=COLORS["sidebar_text"],
            font=("Segoe UI", 16, "bold"),
        ).pack(fill="x")
        ctk.CTkLabel(
            brand_text,
            text="VC++ Redistributable",
            anchor="w",
            text_color=COLORS["sidebar_muted"],
            font=("Segoe UI", 11),
        ).pack(fill="x", pady=(1, 0))

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2b3a4e").pack(
            fill="x", padx=22, pady=(0, 18)
        )
        ctk.CTkLabel(
            self.sidebar,
            text="操作",
            anchor="w",
            text_color=COLORS["sidebar_muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(fill="x", padx=22, pady=(0, 8))

        self.scan_btn = self._sidebar_button("重新扫描", self.scan, primary=True)
        self.select_missing_btn = self._sidebar_button("选择待处理项", self.select_missing)
        self.select_all_btn = self._sidebar_button("全选可用项", lambda: self.set_all(True))
        self.clear_btn = self._sidebar_button("清除选择", lambda: self.set_all(False))
        self.open_folder_btn = self._sidebar_button("打开离线包目录", self.open_offline_folder)

        ctk.CTkLabel(
            self.sidebar,
            text="外观",
            anchor="w",
            text_color=COLORS["sidebar_muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(fill="x", padx=22, pady=(22, 8))
        self.theme_selector = ctk.CTkSegmentedButton(
            self.sidebar,
            values=["跟随系统", "浅色", "深色"],
            variable=self.theme_var,
            command=self.change_theme,
            height=32,
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color="#1e293b",
            unselected_hover_color="#334155",
            text_color="#f8fafc",
            font=("Segoe UI", 11),
        )
        self.theme_selector.pack(fill="x", padx=22)

        self.sidebar_footer = ctk.CTkFrame(
            self.sidebar,
            corner_radius=8,
            fg_color=COLORS["sidebar_surface"],
            border_width=1,
            border_color="#2b3a4e",
        )
        self.sidebar_footer.pack(side="bottom", fill="x", padx=22, pady=22)

        self.install_btn = ctk.CTkButton(
            self.sidebar_footer,
            text="安装 0 个项目",
            height=44,
            corner_radius=7,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            font=("Segoe UI", 13, "bold"),
            command=self.start,
        )
        self.install_btn.pack(fill="x", padx=12, pady=(12, 9))
        self.status_lbl = ctk.CTkLabel(
            self.sidebar_footer,
            text="准备就绪",
            anchor="w",
            text_color=COLORS["sidebar_text"],
            font=("Segoe UI", 11, "bold"),
        )
        self.status_lbl.pack(fill="x", padx=13)
        self.system_lbl = ctk.CTkLabel(
            self.sidebar_footer,
            text=f"{platform.system() or 'Windows'} / {get_arch()}",
            anchor="w",
            text_color=COLORS["sidebar_muted"],
            font=("Segoe UI", 11),
        )
        self.system_lbl.pack(fill="x", padx=13, pady=(2, 12))

    def _sidebar_button(self, text: str, command, primary: bool = False) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self.sidebar,
            text=text,
            anchor="w",
            height=38,
            corner_radius=7,
            fg_color=COLORS["accent"] if primary else "transparent",
            hover_color=COLORS["accent_hover"] if primary else "#1e293b",
            text_color="#ffffff",
            font=("Segoe UI", 12),
            command=command,
        )
        button.pack(fill="x", padx=14, pady=2)
        return button

    def _build_main(self) -> None:
        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["main"])
        self.main.pack(side="right", expand=True, fill="both")

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(25, 17))
        heading_block = ctk.CTkFrame(header, fg_color="transparent")
        heading_block.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            heading_block,
            text="WINDOWS COMPONENTS",
            anchor="w",
            text_color=COLORS["accent"],
            font=("Segoe UI", 10, "bold"),
        ).pack(fill="x")
        ctk.CTkLabel(
            heading_block,
            text="VC++ 运行库",
            anchor="w",
            text_color=COLORS["text"],
            font=("Segoe UI", 28, "bold"),
        ).pack(fill="x", pady=(1, 0))
        ctk.CTkLabel(
            heading_block,
            text="本机组件状态",
            anchor="w",
            text_color=COLORS["muted"],
            font=("Segoe UI", 12),
        ).pack(fill="x", pady=(2, 0))

        self.scan_state_lbl = ctk.CTkLabel(
            header,
            text="等待扫描",
            height=30,
            corner_radius=15,
            fg_color=("#e2e8f0", "#334155"),
            text_color=COLORS["muted"],
            font=("Segoe UI", 11, "bold"),
            padx=13,
        )
        self.scan_state_lbl.pack(side="right", anchor="n", pady=(14, 0))

        stats = ctk.CTkFrame(self.main, fg_color="transparent")
        stats.pack(fill="x", padx=28, pady=(0, 16))
        for column in range(4):
            stats.grid_columnconfigure(column, weight=1, uniform="stats")

        self.stat_labels: dict[str, ctk.CTkLabel] = {}
        stat_specs = (
            ("installed", "已安装", "#16a34a"),
            ("missing", "待安装", "#ea580c"),
            ("offline", "离线就绪", "#7c3aed"),
            ("selected", "已选择", COLORS["accent"]),
        )
        for column, (key, label, accent) in enumerate(stat_specs):
            card = ctk.CTkFrame(
                stats,
                corner_radius=8,
                fg_color=COLORS["surface"],
                border_width=1,
                border_color=COLORS["border"],
            )
            card.grid(row=0, column=column, sticky="nsew", padx=(0, 10) if column < 3 else 0)
            ctk.CTkFrame(card, height=3, corner_radius=2, fg_color=accent).pack(
                fill="x", padx=14, pady=(12, 6)
            )
            value = ctk.CTkLabel(
                card,
                text="0",
                anchor="w",
                text_color=COLORS["text"],
                font=("Segoe UI", 23, "bold"),
            )
            value.pack(fill="x", padx=15)
            ctk.CTkLabel(
                card,
                text=label,
                anchor="w",
                text_color=COLORS["muted"],
                font=("Segoe UI", 11),
            ).pack(fill="x", padx=15, pady=(0, 12))
            self.stat_labels[key] = value

        self._build_runtime_panel()
        self._build_activity_panel()

    def _build_runtime_panel(self) -> None:
        panel = ctk.CTkFrame(
            self.main,
            corner_radius=8,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["border"],
        )
        panel.pack(fill="both", expand=True, padx=28, pady=(0, 15))

        panel_header = ctk.CTkFrame(panel, fg_color="transparent")
        panel_header.pack(fill="x", padx=16, pady=(14, 10))
        ctk.CTkLabel(
            panel_header,
            text="运行库清单",
            anchor="w",
            text_color=COLORS["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")
        self.runtime_count_lbl = ctk.CTkLabel(
            panel_header,
            text=f"{len(RUNTIMES)} 个项目",
            anchor="e",
            text_color=COLORS["muted"],
            font=("Segoe UI", 11),
        )
        self.runtime_count_lbl.pack(side="right")

        table_header = ctk.CTkFrame(panel, height=32, corner_radius=0, fg_color=COLORS["surface_muted"])
        table_header.pack(fill="x", padx=8)
        self._configure_runtime_columns(table_header)
        headers = (("", 0), ("运行库", 1), ("本机版本", 2), ("安装包", 3), ("状态", 4))
        for text, column in headers:
            ctk.CTkLabel(
                table_header,
                text=text,
                anchor="w",
                text_color=COLORS["muted"],
                font=("Segoe UI", 10, "bold"),
            ).grid(row=0, column=column, sticky="ew", padx=10, pady=8)

        self.list_frame = ctk.CTkScrollableFrame(
            panel,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_button_color=("#cbd5e1", "#475569"),
            scrollbar_button_hover_color=("#94a3b8", "#64748b"),
        )
        self.list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.list_frame.grid_columnconfigure(0, weight=1)

    def _build_activity_panel(self) -> None:
        activity = ctk.CTkFrame(
            self.main,
            corner_radius=8,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["border"],
        )
        activity.pack(fill="x", padx=28, pady=(0, 18))

        activity_header = ctk.CTkFrame(activity, fg_color="transparent")
        activity_header.pack(fill="x", padx=16, pady=(12, 7))
        ctk.CTkLabel(
            activity_header,
            text="活动",
            anchor="w",
            text_color=COLORS["text"],
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left")
        self.activity_lbl = ctk.CTkLabel(
            activity_header,
            text="等待操作",
            anchor="e",
            text_color=COLORS["muted"],
            font=("Segoe UI", 11),
        )
        self.activity_lbl.pack(side="right")

        self.progress = ctk.CTkProgressBar(
            activity,
            height=7,
            progress_color=COLORS["accent"],
            fg_color=("#e2e8f0", "#334155"),
        )
        self.progress.pack(fill="x", padx=16, pady=(0, 10))
        self.progress.set(0)

        self.log = ctk.CTkTextbox(
            activity,
            height=84,
            corner_radius=6,
            fg_color=COLORS["surface_muted"],
            text_color=COLORS["text"],
            font=("Cascadia Mono", 11),
            border_width=0,
        )
        self.log.pack(fill="x", padx=16, pady=(0, 14))
        self.write("应用已启动，等待扫描。")

    @staticmethod
    def _configure_runtime_columns(frame) -> None:
        frame.grid_columnconfigure(0, minsize=48)
        frame.grid_columnconfigure(1, weight=3, minsize=210)
        frame.grid_columnconfigure(2, weight=1, minsize=132)
        frame.grid_columnconfigure(3, weight=1, minsize=150)
        frame.grid_columnconfigure(4, minsize=92)

    def build_runtime_list(self) -> None:
        for index, runtime in enumerate(RUNTIMES):
            row = ctk.CTkFrame(
                self.list_frame,
                corner_radius=7,
                fg_color=COLORS["row"],
                border_width=1,
                border_color=COLORS["border"],
            )
            row.grid(row=index, column=0, sticky="ew", padx=2, pady=(0, 5))
            self._configure_runtime_columns(row)

            variable = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(
                row,
                text="",
                width=24,
                checkbox_width=18,
                checkbox_height=18,
                corner_radius=4,
                border_width=2,
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                variable=variable,
                command=self.refresh_selection_count,
            )
            checkbox.grid(row=0, column=0, rowspan=2, padx=(16, 8), pady=10)

            identity = ctk.CTkFrame(row, fg_color="transparent")
            identity.grid(row=0, column=1, rowspan=2, sticky="ew", pady=8)
            identity.grid_columnconfigure(0, weight=1)
            title = ctk.CTkLabel(
                identity,
                text=runtime["name"],
                anchor="w",
                text_color=COLORS["text"],
                font=("Segoe UI", 13, "bold"),
            )
            title.grid(row=0, column=0, sticky="w")
            arch = ctk.CTkLabel(
                identity,
                text=runtime["arch"].upper(),
                width=38,
                height=20,
                corner_radius=5,
                fg_color=("#e8eef7", "#304057"),
                text_color=COLORS["muted"],
                font=("Segoe UI", 10, "bold"),
            )
            arch.grid(row=0, column=1, sticky="e", padx=(9, 0))
            detail = ctk.CTkLabel(
                identity,
                text="正在检测",
                anchor="w",
                text_color=COLORS["muted"],
                font=("Segoe UI", 10),
            )
            detail.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))

            local = ctk.CTkLabel(
                row,
                text="检测中",
                anchor="w",
                text_color=COLORS["muted"],
                font=("Segoe UI", 11),
            )
            local.grid(row=0, column=2, rowspan=2, sticky="ew", padx=10, pady=8)

            package = ctk.CTkLabel(
                row,
                text="检查缓存中",
                anchor="w",
                justify="left",
                wraplength=142,
                text_color=COLORS["muted"],
                font=("Segoe UI", 10),
            )
            package.grid(row=0, column=3, rowspan=2, sticky="ew", padx=10, pady=8)

            state = ctk.CTkLabel(
                row,
                text=STATUS_STYLES["checking"]["text"],
                width=76,
                height=28,
                corner_radius=14,
                fg_color=STATUS_STYLES["checking"]["fg"],
                text_color=STATUS_STYLES["checking"]["text_color"],
                font=("Segoe UI", 10, "bold"),
            )
            state.grid(row=0, column=4, rowspan=2, padx=(4, 14), pady=9)

            self.runtime_rows[runtime["id"]] = {
                "runtime": runtime,
                "frame": row,
                "variable": variable,
                "checkbox": checkbox,
                "detail": detail,
                "local": local,
                "package": package,
                "state": state,
                "installed": False,
                "supported": True,
                "offline_ready": False,
                "source_online": None,
            }

    def ui(self, callback, *args, **kwargs) -> None:
        """Schedule a widget change from a worker thread if the window is open."""
        if self.is_closing:
            return
        try:
            self.after(0, lambda: callback(*args, **kwargs) if not self.is_closing else None)
        except (RuntimeError, TclError):
            pass

    def write(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.insert("end", f"[{timestamp}] {message}\n")
        self.log.see("end")

    def set_activity(self, text: str, progress: float | None = None) -> None:
        self.activity_lbl.configure(text=text)
        if progress is not None:
            self.progress.set(max(0, min(1, progress)))

    def scan(self) -> None:
        if self.is_busy:
            return
        self.set_busy(True)
        self.scan_state_lbl.configure(
            text="正在扫描",
            fg_color=STATUS_STYLES["checking"]["fg"],
            text_color=STATUS_STYLES["checking"]["text_color"],
        )
        self.status_lbl.configure(text="正在扫描")
        self.set_activity("正在读取本机组件状态", 0)
        threading.Thread(target=self.run_scan, name="runtime-scan", daemon=True).start()

    def run_scan(self) -> None:
        if not is_windows():
            self.ui(self.finish_scan, 0, 0, 0, 0, 0, "该工具仅支持 Windows")
            return

        installed_count = 0
        missing_count = 0
        offline_count = 0
        online_checked = 0
        online_available = 0
        total = len(self.runtime_rows)

        self.ui(self.write, "开始扫描 VC++ 运行库。")
        for index, (runtime_id, row) in enumerate(self.runtime_rows.items(), start=1):
            runtime = row["runtime"]
            supported = is_supported_arch(runtime)
            installed = check_installed(runtime) if supported else False
            local_version = get_installed_version(runtime) if supported and installed else ""

            package_path = resolve_project_path(runtime["offline_path"])
            package_error = package_validation_error(package_path, get_offline_sha256(runtime))
            offline_ready = package_error is None
            package_size = package_path.stat().st_size if offline_ready else 0

            source_online = None
            source_error = ""
            if supported and runtime.get("cloud_version_check"):
                online_checked += 1
                try:
                    get_cloud_package_info(runtime)
                    source_online = True
                    online_available += 1
                except Exception as exc:
                    source_online = False
                    source_error = str(exc).splitlines()[0]
                    self.ui(self.write, f"在线源未验证：{runtime['name']}（{source_error}）")

            installed_count += int(supported and installed)
            missing_count += int(supported and not installed)
            offline_count += int(offline_ready)
            self.ui(
                self.update_runtime_state,
                runtime_id,
                installed,
                supported,
                local_version,
                offline_ready,
                package_size,
                package_error,
                source_online,
                source_error,
                True,
            )
            self.ui(self.set_activity, f"正在扫描 {index}/{total}", index / total)

        self.ui(
            self.finish_scan,
            installed_count,
            missing_count,
            offline_count,
            online_checked,
            online_available,
            "扫描完成",
        )

    def update_runtime_state(
        self,
        runtime_id: str,
        installed: bool,
        supported: bool,
        local_version: str,
        offline_ready: bool,
        package_size: int,
        package_error: str | None,
        source_online: bool | None,
        source_error: str,
        auto_select_missing: bool,
    ) -> None:
        row = self.runtime_rows[runtime_id]
        row.update(
            installed=installed,
            supported=supported,
            offline_ready=offline_ready,
            source_online=source_online,
        )

        if not supported:
            state_key = "unsupported"
            local_text = "当前系统不支持"
            package_text = "不需要处理"
            row["variable"].set(False)
        elif installed:
            state_key = "installed"
            local_text = local_version or "已检测到"
            package_text = self.package_text(offline_ready, package_size, package_error, source_online)
        else:
            state_key = "missing"
            local_text = "未安装"
            package_text = self.package_text(offline_ready, package_size, package_error, source_online)
            if auto_select_missing:
                row["variable"].set(True)

        if source_error and not offline_ready:
            package_text = "离线包不可用 / 在线源未验证"

        style = STATUS_STYLES[state_key]
        row["detail"].configure(text=f"{row['runtime']['version_key']} 系列 / {row['runtime']['arch'].upper()}")
        row["local"].configure(text=local_text)
        row["package"].configure(text=package_text)
        row["state"].configure(
            text=style["text"], fg_color=style["fg"], text_color=style["text_color"]
        )
        row["checkbox"].configure(
            state="disabled" if self.is_busy or not supported else "normal"
        )
        self.refresh_selection_count()

    @staticmethod
    def package_text(
        offline_ready: bool,
        package_size: int,
        package_error: str | None,
        source_online: bool | None,
    ) -> str:
        if offline_ready:
            if source_online is True:
                suffix = " / 在线可用"
            elif source_online is False:
                suffix = " / 在线未验证"
            else:
                suffix = ""
            return f"离线包就绪 {format_size(package_size)}{suffix}"
        if source_online:
            return "安装时下载 / 在线可用"
        if source_online is False:
            return "安装时下载 / 在线未验证"
        if package_error and package_error != "安装包不存在":
            return "缓存需要重新获取"
        return "安装时下载"

    def finish_scan(
        self,
        installed_count: int,
        missing_count: int,
        offline_count: int,
        online_checked: int,
        online_available: int,
        message: str,
    ) -> None:
        self.stat_labels["installed"].configure(text=str(installed_count))
        self.stat_labels["missing"].configure(text=str(missing_count))
        self.stat_labels["offline"].configure(text=str(offline_count))
        self.refresh_selection_count()
        online_text = (
            f"在线源已验证 {online_available}/{online_checked}"
            if online_checked
            else "离线模式"
        )
        self.scan_state_lbl.configure(
            text=online_text,
            fg_color=("#e2e8f0", "#334155"),
            text_color=COLORS["muted"],
        )
        self.status_lbl.configure(text=f"{message} / {missing_count} 项待处理")
        self.set_activity("等待操作", 0)
        self.write(f"{message}：已安装 {installed_count} 项，待安装 {missing_count} 项。")
        self.set_busy(False)

    def refresh_selection_count(self) -> None:
        selected = 0
        for row in self.runtime_rows.values():
            is_selected = row["supported"] and row["variable"].get()
            selected += int(is_selected)
            row["frame"].configure(
                border_width=2 if is_selected else 1,
                border_color=COLORS["accent"] if is_selected else COLORS["border"],
            )
        self.stat_labels["selected"].configure(text=str(selected))
        self.install_btn.configure(text=f"安装 {selected} 个项目")

    def set_all(self, selected: bool) -> None:
        if self.is_busy:
            return
        for row in self.runtime_rows.values():
            if row["supported"]:
                row["variable"].set(selected)
        self.refresh_selection_count()

    def select_missing(self) -> None:
        if self.is_busy:
            return
        for row in self.runtime_rows.values():
            row["variable"].set(row["supported"] and not row["installed"])
        self.refresh_selection_count()

    def set_busy(self, busy: bool) -> None:
        self.is_busy = busy
        state = "disabled" if busy else "normal"
        for button in (
            self.scan_btn,
            self.select_missing_btn,
            self.select_all_btn,
            self.clear_btn,
            self.open_folder_btn,
            self.install_btn,
        ):
            button.configure(state=state)
        for row in self.runtime_rows.values():
            row["checkbox"].configure(
                state="disabled" if busy or not row["supported"] else "normal"
            )

    def change_theme(self, choice: str) -> None:
        modes = {"跟随系统": "system", "浅色": "light", "深色": "dark"}
        ctk.set_appearance_mode(modes[choice])

    def open_offline_folder(self) -> None:
        folder = resolve_project_path("offline")
        folder.mkdir(parents=True, exist_ok=True)
        launcher = getattr(os, "startfile", None)
        if launcher is None:
            messagebox.showinfo("离线包目录", str(folder), parent=self)
            return
        try:
            launcher(str(folder))
        except OSError as exc:
            messagebox.showerror("无法打开目录", str(exc), parent=self)

    def start(self) -> None:
        if self.is_busy:
            return
        selected = [
            row["runtime"]
            for row in self.runtime_rows.values()
            if row["supported"] and row["variable"].get()
        ]
        if not selected:
            self.write("请先选择至少一个运行库。")
            self.status_lbl.configure(text="尚未选择项目")
            return

        accepted = messagebox.askokcancel(
            "确认安装",
            f"将处理 {len(selected)} 个 VC++ 运行库。\n\n"
            "安装程序会静默运行，个别项目完成后可能需要重启 Windows。",
            icon="warning",
            parent=self,
        )
        if not accepted:
            return

        self.restart_required = False
        self.set_busy(True)
        self.status_lbl.configure(text="正在准备安装")
        self.set_activity("正在准备安装包", 0)
        threading.Thread(
            target=self.run_install, args=(selected,), name="runtime-install", daemon=True
        ).start()

    def run_install(self, selected: list[dict]) -> None:
        install_items: list[dict] = []
        files: list[str] = []
        skipped = 0

        self.ui(self.write, f"开始处理 {len(selected)} 个运行库。")
        try:
            for item in selected:
                install_item = dict(item)
                if item.get("cloud_version_check"):
                    self.ui(self.set_activity, f"正在获取最新版：{item['name']}", 0)
                    try:
                        cloud_path, cloud_version = download_latest_package(
                            item, cb=self.download_progress
                        )
                        local_version = get_installed_version(item)
                        if (
                            check_installed(item)
                            and cloud_version
                            and local_version
                            and compare_versions(cloud_version, local_version) <= 0
                        ):
                            skipped += 1
                            self.ui(
                                self.write,
                                f"跳过 {item['name']}：本机版本 {local_version} 已是最新。",
                            )
                            continue
                        install_item["_install_path"] = cloud_path
                        # The cloud package changes over time, so only the static cache uses a pinned hash.
                        install_item["_install_sha256"] = ""
                        self.ui(
                            self.write,
                            f"已准备最新版：{item['name']} {cloud_version or '版本未知'}。",
                        )
                    except Exception as exc:
                        offline_path = resolve_project_path(item["offline_path"])
                        offline_error = package_validation_error(
                            offline_path, get_offline_sha256(item)
                        )
                        if offline_error is None:
                            install_item["_install_path"] = str(offline_path)
                            install_item["_install_sha256"] = get_offline_sha256(item)
                            self.ui(
                                self.write,
                                f"在线获取失败，改用离线包：{item['name']}。",
                            )
                        else:
                            self.ui(self.write, f"无法准备 {item['name']}：{exc}")
                            continue

                install_items.append(install_item)
                if install_item.get("_install_path"):
                    files.append(install_item["_install_path"])

            download_items = [item for item in install_items if not item.get("_install_path")]
            if download_items:
                self.ui(self.set_activity, "正在准备离线安装包", 0)
                files.extend(download_all(download_items, cb=self.download_progress))

            if not install_items:
                self.ui(self.finish_install, False, skipped, "没有需要安装的项目")
                return

            total = len(install_items)
            completed = 0

            def install_callback(name: str, stage: str, payload) -> None:
                nonlocal completed
                if stage == "start":
                    self.ui(self.set_activity, f"正在安装：{name}", completed / total)
                    self.ui(self.write, f"开始静默安装：{name}。")
                    return

                completed += 1
                if stage == "done":
                    code = payload if isinstance(payload, int) else None
                    self.restart_required = self.restart_required or code in RESTART_CODES
                    result_text = install_result_text(code)
                    if code not in SUCCESS_CODES:
                        result_text += "；未确认成功，请检查安装日志"
                    self.ui(self.write, f"{name}：{result_text}。")
                else:
                    self.ui(self.write, f"{name}：{payload}")
                self.ui(self.set_activity, f"已完成 {completed}/{total}", completed / total)

            install_all(files, install_items, cb=install_callback)
            self.ui(self.finish_install, self.restart_required, skipped, "安装处理完成")
        except Exception as exc:
            self.ui(self.install_failed, str(exc))

    def download_progress(self, name: str, current: int, total: int) -> None:
        if total:
            percent = current / total
            text = f"正在准备：{name} {percent:.0%}"
        else:
            percent = 0
            text = f"正在准备：{name} {format_size(current)}"
        self.ui(self.set_activity, text, percent)

    def finish_install(self, restart_required: bool, skipped: int, message: str) -> None:
        if skipped:
            self.write(f"已跳过 {skipped} 个无需更新的项目。")
        if restart_required:
            self.write("至少一个安装程序要求重启 Windows 后才能完全生效。")
            self.status_lbl.configure(text="安装完成，需要重启")
        else:
            self.status_lbl.configure(text=message)
        self.set_busy(False)
        self.set_activity("正在重新扫描本机状态", 1)
        self.scan()

    def install_failed(self, error: str) -> None:
        self.write(f"安装流程未完成：{error}")
        self.status_lbl.configure(text="安装流程未完成")
        self.set_activity("操作未完成", 0)
        self.set_busy(False)

    def on_close(self) -> None:
        if self.is_busy and not messagebox.askyesno(
            "仍在处理", "后台任务仍在运行，确定要关闭窗口吗？", parent=self
        ):
            return
        self.is_closing = True
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
