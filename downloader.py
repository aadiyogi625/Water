"""
YouTube Shorts Channel Downloader
- Downloads all shorts from a YouTube channel in 1080p
- Modern dark-themed GUI with progress tracking
- Saves videos in a 'Shorts' folder
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import os
import sys
import re
import json
import shutil
import tempfile
from datetime import datetime


class YouTubeShortsDownloader:
    ANDROID_TV_USER_AGENT = (
        "Mozilla/5.0 (Linux; Android 10; BRAVIA 4K VH2 Build/QTG3.200305.006.S292; wv) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
        "Chrome/122.0.6261.120 Safari/537.36"
    )

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Shorts Downloader")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#0f0f1a")
        
        # State
        self.is_downloading = False
        self.process = None
        self.total_videos = 0
        self.downloaded_count = 0
        
        # Colors
        self.colors = {
            "bg": "#0f0f1a",
            "card": "#1a1a2e",
            "card_border": "#2a2a4a",
            "accent": "#e94560",
            "accent_hover": "#ff6b81",
            "text": "#ffffff",
            "text_dim": "#8888aa",
            "success": "#00d2a0",
            "input_bg": "#16213e",
            "input_border": "#0f3460",
            "progress_bg": "#1a1a2e",
            "progress_fill": "#e94560",
            "btn_stop": "#ff4757",
        }
        
        self._setup_styles()
        self._build_ui()
        
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Progress bar
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=self.colors["progress_bg"],
            background=self.colors["accent"],
            bordercolor=self.colors["card_border"],
            lightcolor=self.colors["accent"],
            darkcolor=self.colors["accent"],
            thickness=22,
        )
    
    def _build_ui(self):
        # Main container with padding
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=24, pady=18)
        
        # Header
        header = tk.Frame(main, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 18))
        
        title_label = tk.Label(
            header,
            text="YouTube Shorts Downloader",
            font=("Segoe UI", 22, "bold"),
            fg=self.colors["accent"],
            bg=self.colors["bg"],
        )
        title_label.pack(side="left")
        
        subtitle = tk.Label(
            header,
            text="Channel ke saare Shorts 1080p mein download karo",
            font=("Segoe UI", 10),
            fg=self.colors["text_dim"],
            bg=self.colors["bg"],
        )
        subtitle.pack(side="left", padx=(16, 0), pady=(8, 0))
        
        # URL Card
        url_card = tk.Frame(main, bg=self.colors["card"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        url_card.pack(fill="x", pady=(0, 12))
        url_inner = tk.Frame(url_card, bg=self.colors["card"])
        url_inner.pack(fill="x", padx=18, pady=14)
        
        tk.Label(url_inner, text="Channel / Playlist URL", font=("Segoe UI", 11, "bold"), fg=self.colors["text"], bg=self.colors["card"]).pack(anchor="w")
        
        url_entry_frame = tk.Frame(url_inner, bg=self.colors["input_bg"], highlightbackground=self.colors["input_border"], highlightthickness=1)
        url_entry_frame.pack(fill="x", pady=(8, 0))
        
        self.url_var = tk.StringVar(value="https://www.youtube.com/@ShortsBreak_Official/shorts")
        self.url_entry = tk.Entry(
            url_entry_frame,
            textvariable=self.url_var,
            font=("Consolas", 12),
            fg=self.colors["text"],
            bg=self.colors["input_bg"],
            insertbackground=self.colors["accent"],
            relief="flat",
            bd=0,
        )
        self.url_entry.pack(fill="x", padx=10, pady=8)
        
        # Settings Card
        settings_card = tk.Frame(main, bg=self.colors["card"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        settings_card.pack(fill="x", pady=(0, 12))
        settings_inner = tk.Frame(settings_card, bg=self.colors["card"])
        settings_inner.pack(fill="x", padx=18, pady=14)
        
        tk.Label(settings_inner, text="Settings", font=("Segoe UI", 11, "bold"), fg=self.colors["text"], bg=self.colors["card"]).pack(anchor="w")
        
        settings_row = tk.Frame(settings_inner, bg=self.colors["card"])
        settings_row.pack(fill="x", pady=(10, 0))
        
        # Output folder
        folder_frame = tk.Frame(settings_row, bg=self.colors["card"])
        folder_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(folder_frame, text="Save Location:", font=("Segoe UI", 9), fg=self.colors["text_dim"], bg=self.colors["card"]).pack(anchor="w")
        
        folder_pick = tk.Frame(folder_frame, bg=self.colors["input_bg"], highlightbackground=self.colors["input_border"], highlightthickness=1)
        folder_pick.pack(fill="x", pady=(4, 0))
        
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Shorts")
        self.folder_var = tk.StringVar(value=default_path)
        self.folder_entry = tk.Entry(
            folder_pick,
            textvariable=self.folder_var,
            font=("Consolas", 10),
            fg=self.colors["text"],
            bg=self.colors["input_bg"],
            insertbackground=self.colors["accent"],
            relief="flat",
            bd=0,
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=8, pady=6)
        
        browse_btn = tk.Button(
            folder_pick,
            text="Browse",
            font=("Segoe UI", 11),
            fg=self.colors["text"],
            bg=self.colors["card"],
            activebackground=self.colors["accent"],
            relief="flat",
            cursor="hand2",
            command=self._browse_folder,
        )
        browse_btn.pack(side="right", padx=4, pady=2)
        
        # Quality selector
        quality_frame = tk.Frame(settings_row, bg=self.colors["card"])
        quality_frame.pack(side="right", padx=(16, 0))
        
        tk.Label(quality_frame, text="Quality:", font=("Segoe UI", 9), fg=self.colors["text_dim"], bg=self.colors["card"]).pack(anchor="w")
        
        self.quality_var = tk.StringVar(value="1080p")
        quality_menu = tk.OptionMenu(quality_frame, self.quality_var, "1080p", "720p", "480p", "360p", "Best Available")
        quality_menu.config(
            font=("Segoe UI", 10),
            fg=self.colors["text"],
            bg=self.colors["input_bg"],
            activebackground=self.colors["accent"],
            highlightthickness=0,
            relief="flat",
            width=14,
        )
        quality_menu["menu"].config(
            fg=self.colors["text"],
            bg=self.colors["input_bg"],
            activebackground=self.colors["accent"],
            font=("Segoe UI", 10),
        )
        quality_menu.pack(pady=(4, 0))
        
        # Buttons Row
        btn_row = tk.Frame(main, bg=self.colors["bg"])
        btn_row.pack(fill="x", pady=(4, 12))
        
        self.start_btn = tk.Button(
            btn_row,
            text="Start Download",
            font=("Segoe UI", 13, "bold"),
            fg="#ffffff",
            bg=self.colors["accent"],
            activebackground=self.colors["accent_hover"],
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=10,
            command=self._start_download,
        )
        self.start_btn.pack(side="left")
        
        self.stop_btn = tk.Button(
            btn_row,
            text="Stop",
            font=("Segoe UI", 13, "bold"),
            fg="#ffffff",
            bg=self.colors["btn_stop"],
            activebackground="#ff6b6b",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=10,
            state="disabled",
            command=self._stop_download,
        )
        self.stop_btn.pack(side="left", padx=(12, 0))
        
        self.open_folder_btn = tk.Button(
            btn_row,
            text="Open Folder",
            font=("Segoe UI", 11),
            fg=self.colors["text_dim"],
            bg=self.colors["card"],
            activebackground=self.colors["card_border"],
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=8,
            command=self._open_folder,
        )
        self.open_folder_btn.pack(side="right")
        
        # Progress Card
        progress_card = tk.Frame(main, bg=self.colors["card"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        progress_card.pack(fill="x", pady=(0, 12))
        progress_inner = tk.Frame(progress_card, bg=self.colors["card"])
        progress_inner.pack(fill="x", padx=18, pady=14)
        
        progress_header = tk.Frame(progress_inner, bg=self.colors["card"])
        progress_header.pack(fill="x")
        
        tk.Label(progress_header, text="Progress", font=("Segoe UI", 11, "bold"), fg=self.colors["text"], bg=self.colors["card"]).pack(side="left")
        
        self.progress_label = tk.Label(
            progress_header,
            text="Ready",
            font=("Segoe UI", 10),
            fg=self.colors["success"],
            bg=self.colors["card"],
        )
        self.progress_label.pack(side="right")
        
        self.progress_bar = ttk.Progressbar(
            progress_inner,
            style="Custom.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
        )
        self.progress_bar.pack(fill="x", pady=(10, 6))
        
        self.status_label = tk.Label(
            progress_inner,
            text="Download start karne ke liye Start button dabayein",
            font=("Segoe UI", 9),
            fg=self.colors["text_dim"],
            bg=self.colors["card"],
            anchor="w",
        )
        self.status_label.pack(fill="x")
        
        # Log Card
        log_card = tk.Frame(main, bg=self.colors["card"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        log_card.pack(fill="both", expand=True)
        log_inner = tk.Frame(log_card, bg=self.colors["card"])
        log_inner.pack(fill="both", expand=True, padx=18, pady=14)
        
        log_header = tk.Frame(log_inner, bg=self.colors["card"])
        log_header.pack(fill="x")
        
        tk.Label(log_header, text="Download Log", font=("Segoe UI", 11, "bold"), fg=self.colors["text"], bg=self.colors["card"]).pack(side="left")
        
        clear_btn = tk.Button(
            log_header,
            text="Clear",
            font=("Segoe UI", 9),
            fg=self.colors["text_dim"],
            bg=self.colors["card"],
            activebackground=self.colors["card_border"],
            relief="flat",
            cursor="hand2",
            command=self._clear_log,
        )
        clear_btn.pack(side="right")
        
        log_scroll = tk.Frame(log_inner, bg=self.colors["input_bg"])
        log_scroll.pack(fill="both", expand=True, pady=(8, 0))
        
        scrollbar = tk.Scrollbar(log_scroll)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text = tk.Text(
            log_scroll,
            font=("Consolas", 9),
            fg=self.colors["text_dim"],
            bg=self.colors["input_bg"],
            insertbackground=self.colors["accent"],
            relief="flat",
            wrap="word",
            state="disabled",
            yscrollcommand=scrollbar.set,
        )
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)
        scrollbar.config(command=self.log_text.yview)
        
        # Tag for highlighting
        self.log_text.tag_configure("success", foreground=self.colors["success"])
        self.log_text.tag_configure("error", foreground=self.colors["accent"])
        self.log_text.tag_configure("info", foreground="#6c8fff")
        self.log_text.tag_configure("title", foreground="#ffffff", font=("Consolas", 9, "bold"))
    
    # Actions
    
    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Save Location Select Karo")
        if folder:
            self.folder_var.set(folder)
    
    def _open_folder(self):
        folder = self.folder_var.get()
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showwarning("Folder Not Found", f"Folder abhi bana nahi hai:\n{folder}")
    
    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
    
    def _log(self, msg, tag=None):
        """Thread-safe logging"""
        def _do():
            self.log_text.config(state="normal")
            if tag:
                self.log_text.insert("end", msg + "\n", tag)
            else:
                self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(0, _do)
    
    def _update_progress(self, count, total, current_title=""):
        def _do():
            if total > 0:
                pct = (count / total) * 100
                self.progress_bar["value"] = pct
                self.progress_label.config(text=f"{count}/{total}  ({pct:.0f}%)")
            if current_title:
                self.status_label.config(text=f"Downloading: {current_title}")
        self.root.after(0, _do)
    
    def _set_ui_state(self, downloading):
        def _do():
            self.is_downloading = downloading
            if downloading:
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                self.url_entry.config(state="disabled")
            else:
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.url_entry.config(state="normal")
        self.root.after(0, _do)
    
    def _run_quick_version_check(self, cmd):
        try:
            result = subprocess.run(
                cmd + ["--version"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _resolve_yt_dlp_command(self):
        module_cmd = [sys.executable, "-m", "yt_dlp"]
        if self._run_quick_version_check(module_cmd):
            return module_cmd

        yt_dlp_bin = shutil.which("yt-dlp")
        if yt_dlp_bin:
            binary_cmd = [yt_dlp_bin]
            if self._run_quick_version_check(binary_cmd):
                return binary_cmd

        return None

    def _resolve_ffmpeg_path(self):
        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin:
            return ffmpeg_bin

        # Fallback to packaged ffmpeg binary from imageio-ffmpeg.
        try:
            import imageio_ffmpeg

            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_bin and os.path.exists(ffmpeg_bin):
                return ffmpeg_bin
        except Exception:
            pass

        return None

    def _get_quality_format(self):
        q = self.quality_var.get()
        # Always prefer progressive formats that already contain audio+video in one file.
        quality_map = {
            "1080p": "best[height<=1080][vcodec^=avc1][acodec!=none][ext=mp4]/best[height<=1080][vcodec!=none][acodec!=none][ext=mp4]/best[height<=1080][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]",
            "720p": "best[height<=720][vcodec^=avc1][acodec!=none][ext=mp4]/best[height<=720][vcodec!=none][acodec!=none][ext=mp4]/best[height<=720][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]",
            "480p": "best[height<=480][vcodec^=avc1][acodec!=none][ext=mp4]/best[height<=480][vcodec!=none][acodec!=none][ext=mp4]/best[height<=480][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]",
            "360p": "best[height<=360][vcodec^=avc1][acodec!=none][ext=mp4]/best[height<=360][vcodec!=none][acodec!=none][ext=mp4]/best[height<=360][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]",
            "Best Available": "best[vcodec^=avc1][acodec!=none][ext=mp4]/best[vcodec!=none][acodec!=none][ext=mp4]/best[vcodec!=none][acodec!=none]",
        }

        return quality_map.get(q, quality_map["1080p"])

    @staticmethod
    def _normalize_video_key(name):
        base = os.path.basename(name.strip())
        stem, _ = os.path.splitext(base)
        stem = re.sub(r"\.f\d+$", "", stem)
        return stem.strip().lower()

    def _build_shorts_batch_file(self, output_dir, video_ids, prefix="yt_shorts_urls_"):
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=output_dir,
            prefix=prefix,
            suffix=".txt",
        ) as tmp:
            for vid in video_ids:
                tmp.write(f"https://www.youtube.com/shorts/{vid}\n")
            return tmp.name

    def _merge_split_stream_files(self, output_dir, ffmpeg_path):
        if not ffmpeg_path or not os.path.isdir(output_dir):
            return 0

        grouped = {}
        split_re = re.compile(r"^(?P<stem>.+)\.f\d+\.(?P<ext>mp4|m4a)$", re.IGNORECASE)

        for entry in os.scandir(output_dir):
            if not entry.is_file():
                continue
            match = split_re.match(entry.name)
            if not match:
                continue

            stem = match.group("stem")
            ext = match.group("ext").lower()
            key = stem.lower()

            bucket = grouped.setdefault(key, {"stem": stem, "video": None, "audio": None})
            if ext == "mp4" and bucket["video"] is None:
                bucket["video"] = entry.path
            elif ext == "m4a" and bucket["audio"] is None:
                bucket["audio"] = entry.path

        merged_count = 0
        for bucket in grouped.values():
            video_path = bucket["video"]
            audio_path = bucket["audio"]
            if not video_path or not audio_path:
                continue

            merged_path = os.path.join(output_dir, f"{bucket['stem']}.mp4")
            if os.path.exists(merged_path):
                continue

            merge_cmd = [
                ffmpeg_path,
                "-y",
                "-i",
                video_path,
                "-i",
                audio_path,
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                merged_path,
            ]

            result = subprocess.run(
                merge_cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            if result.returncode == 0 and os.path.exists(merged_path):
                merged_count += 1
                try:
                    os.remove(video_path)
                except Exception:
                    pass
                try:
                    os.remove(audio_path)
                except Exception:
                    pass
            else:
                err = (result.stderr or result.stdout or "").strip()
                if err:
                    self._log(f"WARNING: auto-merge failed for {bucket['stem']}: {err[-220:]}", "error")

        return merged_count
    
    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("URL Required", "Pehle YouTube channel/playlist URL daalein!")
            return
        
        output_dir = self.folder_var.get().strip()
        if not output_dir:
            messagebox.showwarning("Folder Required", "Save location select karein!")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        self._set_ui_state(True)
        self._clear_log()
        self.progress_bar["value"] = 0
        self.downloaded_count = 0
        
        self._log(f"URL: {url}", "info")
        self._log(f"Save: {output_dir}", "info")
        self._log(f"Quality: {self.quality_var.get()}", "info")
        self._log("-" * 60)
        
        # Start download thread
        thread = threading.Thread(target=self._download_thread, args=(url, output_dir), daemon=True)
        thread.start()
    
    def _download_thread(self, url, output_dir):
        try:
            batch_file_path = None
            yt_dlp_cmd = self._resolve_yt_dlp_command()
            if not yt_dlp_cmd:
                self._log("ERROR: yt-dlp missing hai. Install karein: python -m pip install yt-dlp", "error")
                self._set_ui_state(False)
                return

            ffmpeg_path = self._resolve_ffmpeg_path()
            if ffmpeg_path:
                pre_merged = self._merge_split_stream_files(output_dir, ffmpeg_path)
                if pre_merged > 0:
                    self._log(f"Info: Purani split files auto-merge hui: {pre_merged}", "success")

            # Step 1: Count total videos
            self._log("Info: Channel ki videos count kar rahe hain... (thoda wait karo)", "info")
            self.root.after(0, lambda: self.status_label.config(text="Videos count ho rahi hain..."))
            self.root.after(0, lambda: self.progress_bar.config(mode="indeterminate"))
            self.root.after(0, lambda: self.progress_bar.start(15))

            count_cmd = [
                *yt_dlp_cmd,
                "--flat-playlist",
                "--print",
                "id",
                "--ignore-config",
                "--no-warnings",
                url,
            ]

            result = subprocess.run(
                count_cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            self.root.after(0, lambda: self.progress_bar.stop())
            self.root.after(0, lambda: self.progress_bar.config(mode="determinate"))

            video_ids = []
            if result.returncode != 0:
                err = (result.stdout or result.stderr or "").strip()
                self._log("Warning: Video list fetch nahi hui. Direct fallback mode try kar rahe hain.", "error")
                if err:
                    self._log(err[-600:], "error")
            else:
                video_ids = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
            self.total_videos = len(video_ids)

            if self.total_videos == 0:
                self._log("Warning: Video ID list empty hai, direct playlist fallback mode use hoga.", "error")
            else:
                self._log(f"Success: Total Videos Found: {self.total_videos}", "success")
                batch_file_path = self._build_shorts_batch_file(output_dir, video_ids)
                self._log("Info: Android TV user-agent mode enabled for better playback compatibility.", "info")
            self._log("-" * 60)

            # Step 2: Download all videos (direct audio+video progressive files)
            fmt = self._get_quality_format()
            archive_path = os.path.join(output_dir, ".yt_download_archive.txt")

            if ffmpeg_path:
                self._log(f"Info: ffmpeg found -> {ffmpeg_path}", "info")
            else:
                self._log("Info: ffmpeg nahi mila, single-file fallback mode use ho raha hai.", "info")
            self._log("Info: Direct audio+video single-file mode enabled (no merge step).", "info")

            anti_rate_limit_flags = [
                "--download-archive",
                archive_path,
                "-t",
                "sleep",
                "--sleep-requests",
                "1.0",
                "--sleep-interval",
                "15",
                "--max-sleep-interval",
                "30",
                "--extractor-retries",
                "3",
                "--retries",
                "10",
                "--fragment-retries",
                "10",
                "--retry-sleep",
                "http:5",
                "--retry-sleep",
                "extractor:10",
                "--socket-timeout",
                "20",
                "--concurrent-fragments",
                "1",
                "--throttled-rate",
                "100K",
                "--force-ipv4",
            ]

            batch_download_cmd = None
            if batch_file_path:
                batch_download_cmd = [
                    *yt_dlp_cmd,
                    "--ignore-config",
                    "--user-agent",
                    self.ANDROID_TV_USER_AGENT,
                    "--batch-file",
                    batch_file_path,
                    "-f",
                    fmt,
                    "-o",
                    os.path.join(output_dir, "%(title)s.%(ext)s"),
                    "--no-overwrites",
                    "--newline",
                    "--no-warnings",
                    "--ignore-errors",
                    *anti_rate_limit_flags,
                ]

            self._log("Info: Download shuru ho raha hai...", "info")
            self._log("-" * 60)
            rate_limit_hits = 0
            rate_limited_video_ids = set()

            def run_download_attempt(cmd, attempt_label, seen_video_keys):
                nonlocal rate_limit_hits, rate_limited_video_ids
                self._log(f"Info: Attempt -> {attempt_label}", "info")
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )

                for line in self.process.stdout:
                    if not self.is_downloading:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    if "[download]" in line and "Destination:" in line:
                        filename = line.split("Destination:", 1)[-1].strip()
                        current_title = os.path.basename(filename)
                        video_key = self._normalize_video_key(current_title)
                        if video_key and video_key not in seen_video_keys:
                            seen_video_keys.add(video_key)
                            self.downloaded_count += 1
                            clean_title = re.sub(r"\.f\d+\.", ".", current_title)
                            self._update_progress(self.downloaded_count, self.total_videos, clean_title)
                            self._log(f"[{self.downloaded_count}/{self.total_videos}] {clean_title}", "title")

                    elif "[download]" in line and "has already been downloaded" in line:
                        already_match = re.search(r"\[download\]\s+(.*?)\s+has already been downloaded", line)
                        existing_name = already_match.group(1) if already_match else line
                        video_key = self._normalize_video_key(existing_name)
                        if video_key and video_key not in seen_video_keys:
                            seen_video_keys.add(video_key)
                            self.downloaded_count += 1
                            self._update_progress(self.downloaded_count, self.total_videos)
                            self._log(f"[{self.downloaded_count}/{self.total_videos}] Already exists - Skipped", "info")

                    elif "[download]" in line and "%" in line:
                        pct_match = re.search(r"(\d+\.?\d*)%", line)
                        if pct_match:
                            file_pct = float(pct_match.group(1))
                            if self.total_videos > 0:
                                completed = max(self.downloaded_count - 1, 0)
                                overall = ((completed + file_pct / 100) / self.total_videos) * 100
                                self.root.after(0, lambda o=overall: self.progress_bar.__setitem__("value", o))
                            speed_match = re.search(r"at\s+(\S+)", line)
                            eta_match = re.search(r"ETA\s+(\S+)", line)
                            speed = speed_match.group(1) if speed_match else ""
                            eta = eta_match.group(1) if eta_match else ""
                            self.root.after(
                                0,
                                lambda s=speed, e=eta, p=file_pct: self.status_label.config(
                                    text=f"{p:.0f}%  |  Speed: {s}  |  ETA: {e}"
                                ),
                            )

                    elif "[Merger]" in line or "[ExtractAudio]" in line or "Merging" in line:
                        # In direct progressive mode, merger lines are ignored in UI log.
                        pass

                    elif "ERROR" in line or "Got error:" in line:
                        lower_line = line.lower()
                        if "rate-limited by youtube" in lower_line or "this content isn't available, try again later" in lower_line:
                            rate_limit_hits += 1
                            vid_match = re.search(r"\[youtube\]\s+([A-Za-z0-9_-]{6,})", line)
                            if vid_match:
                                vid = vid_match.group(1)
                                if vid not in rate_limited_video_ids:
                                    self._log(f"Warning: Rate-limit on video {vid}. Retry queue me add kiya.", "error")
                                rate_limited_video_ids.add(vid)
                            if rate_limit_hits in (1, 3):
                                self._log(
                                    "Warning: YouTube rate-limit detect hua. Downloader slow mode pe continue kar raha hai.",
                                    "error",
                                )
                            if rate_limit_hits >= 8:
                                self._log(
                                    "ERROR: Rate-limit errors bahut zyada hain. Current attempt stop kar rahe hain to avoid more blocking.",
                                    "error",
                                )
                                try:
                                    self.process.terminate()
                                except Exception:
                                    pass
                                break
                        else:
                            self._log(f"Warning: {line}", "error")

                return self.process.wait()

            seen_video_keys = set()

            playlist_fallback_cmd = [
                *yt_dlp_cmd,
                "--ignore-config",
                "-f",
                fmt,
                "-o",
                os.path.join(output_dir, "%(title)s.%(ext)s"),
                "--no-overwrites",
                "--newline",
                "--no-warnings",
                "--ignore-errors",
                *anti_rate_limit_flags,
                url,
            ]
            attempts = []
            if batch_download_cmd:
                fallback_cmd = list(batch_download_cmd)
                if "--user-agent" in fallback_cmd:
                    ua_idx = fallback_cmd.index("--user-agent")
                    del fallback_cmd[ua_idx : ua_idx + 2]
                android_api_cmd = list(fallback_cmd)
                android_api_cmd.extend(["--extractor-args", "youtube:player_client=android"])
                attempts.append(("Android API primary", android_api_cmd))
                attempts.append(("Android TV user-agent fallback", batch_download_cmd))
                attempts.append(("Default user-agent fallback", fallback_cmd))

            playlist_android_cmd = list(playlist_fallback_cmd)
            playlist_android_cmd.extend(["--extractor-args", "youtube:player_client=android"])
            attempts.append(("Direct playlist Android API fallback", playlist_android_cmd))
            attempts.append(("Direct playlist fallback", playlist_fallback_cmd))

            return_code = 1
            for idx, (attempt_label, attempt_cmd) in enumerate(attempts, start=1):
                if not self.is_downloading:
                    break
                return_code = run_download_attempt(attempt_cmd, attempt_label, seen_video_keys)
                if return_code == 0:
                    break
                if idx < len(attempts):
                    self._log(
                        f"Warning: Attempt failed (code {return_code}). Next fallback try kar rahe hain...",
                        "error",
                    )

            if self.is_downloading and return_code != 0:
                self._log(f"ERROR: yt-dlp exited with code {return_code}", "error")
            if rate_limit_hits > 0:
                self._log(f"Warning: Rate-limit hits detected: {rate_limit_hits}", "error")
                if rate_limited_video_ids:
                    sample_ids = ", ".join(sorted(list(rate_limited_video_ids))[:6])
                    self._log(f"Warning: Affected video IDs (sample): {sample_ids}", "error")

            if self.is_downloading and rate_limited_video_ids:
                pending_ids = sorted(rate_limited_video_ids)
                retry_batch_path = None
                try:
                    retry_batch_path = self._build_shorts_batch_file(output_dir, pending_ids, prefix="yt_retry_urls_")
                    retry_cmd = [
                        *yt_dlp_cmd,
                        "--ignore-config",
                        "--batch-file",
                        retry_batch_path,
                        "--extractor-args",
                        "youtube:player_client=android",
                        "-f",
                        "18/best[acodec!=none][vcodec!=none]/best",
                        "-o",
                        os.path.join(output_dir, "%(title)s.%(ext)s"),
                        "--no-overwrites",
                        "--newline",
                        "--no-warnings",
                        "--ignore-errors",
                        *anti_rate_limit_flags,
                    ]
                    self._log(f"Info: Rate-limit recovery pass start ({len(pending_ids)} IDs)", "info")
                    retry_code = run_download_attempt(retry_cmd, "Rate-limit recovery", seen_video_keys)
                    if retry_code == 0:
                        self._log("Success: Rate-limit recovery pass complete.", "success")
                    else:
                        self._log(f"Warning: Recovery pass exited with code {retry_code}", "error")

                    archived_ids = set()
                    if os.path.exists(archive_path):
                        try:
                            with open(archive_path, "r", encoding="utf-8", errors="ignore") as f:
                                for row in f:
                                    m = re.search(r"youtube\s+([A-Za-z0-9_-]{6,})", row)
                                    if m:
                                        archived_ids.add(m.group(1))
                        except Exception:
                            pass

                    unresolved_ids = [vid for vid in pending_ids if vid not in archived_ids]
                    if unresolved_ids:
                        sample_unresolved = ", ".join(unresolved_ids[:6])
                        self._log(f"Warning: Kuch IDs abhi bhi blocked hain: {sample_unresolved}", "error")
                    else:
                        rate_limited_video_ids.clear()
                        rate_limit_hits = 0
                        if return_code != 0:
                            return_code = 0
                finally:
                    if retry_batch_path and os.path.exists(retry_batch_path):
                        try:
                            os.remove(retry_batch_path)
                        except Exception:
                            pass

            if ffmpeg_path:
                post_merged = self._merge_split_stream_files(output_dir, ffmpeg_path)
                if post_merged > 0:
                    self._log(f"Info: Download ke baad extra auto-merge hui: {post_merged}", "success")

            self._log("-" * 60)
            if self.is_downloading and return_code == 0:
                self._log(f"Download Complete! ({self.downloaded_count} videos)", "success")
                self.root.after(0, lambda: self.progress_bar.__setitem__("value", 100))
                display_total = self.total_videos if self.total_videos > 0 else self.downloaded_count
                self.root.after(0, lambda t=display_total: self.progress_label.config(text=f"Complete ({self.downloaded_count}/{t})"))
                self.root.after(0, lambda: self.status_label.config(text="Download complete! Open Folder se videos dekhein"))
            elif self.is_downloading:
                if rate_limit_hits > 0:
                    self._log("Download paused due to YouTube rate-limit. 45-60 min baad retry karein ya network change karein.", "error")
                    self.root.after(0, lambda: self.status_label.config(text="YouTube rate-limit detect hua. 45-60 min baad retry karein."))
                else:
                    self._log("Download failed. Retry karein ya network/cookies check karein.", "error")
                    self.root.after(0, lambda: self.status_label.config(text="Download failed. Log check karein."))
            else:
                self._log(f"Download stopped by user. ({self.downloaded_count} downloaded)", "error")
                self.root.after(0, lambda: self.status_label.config(text="Download stopped by user"))

        except Exception as e:
            self._log(f"Error: {str(e)}", "error")
            import traceback
            self._log(traceback.format_exc(), "error")

        finally:
            if batch_file_path and os.path.exists(batch_file_path):
                try:
                    os.remove(batch_file_path)
                except Exception:
                    pass
            self._set_ui_state(False)
            self.process = None

    def _stop_download(self):
        self.is_downloading = False
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass
        self._log("Stopping download...", "error")
        self.root.after(0, lambda: self.stop_btn.config(state="disabled"))


def main():
    root = tk.Tk()
    
    # Set icon (Windows)
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    
    app = YouTubeShortsDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()

