import sys
import os
import threading
import json
import yt_dlp
from qtpy.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QFileDialog, QProgressBar, QStackedWidget,
    QSpinBox, QComboBox
)
from qtpy.QtCore import Qt

SETTINGS_FILE = "yt_downloader_settings.json"

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.resize(900, 600)

        # --- Load settings ---
        self.load_settings()

        # --- Main Layout ---
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Sidebar (Discord-style navigation)
        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(10)

        self.search_tab_btn = QPushButton("Search")
        self.search_tab_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.settings_tab_btn = QPushButton("Settings")
        self.settings_tab_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        for btn in [self.search_tab_btn, self.settings_tab_btn]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2C2F33;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 6px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3A3F44;
                }
                QPushButton:checked {
                    background-color: #5865F2;
                }
            """)
            self.sidebar.addWidget(btn)

        self.sidebar.addStretch()

        # Content stack
        self.stack = QStackedWidget()

        # --- Search Page ---
        search_page = QWidget()
        search_layout = QVBoxLayout(search_page)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search YouTube...")
        self.search_bar.setStyleSheet("padding: 8px; border-radius: 6px; background-color: #23272A; color: white;")
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("background-color: #5865F2; color: white; border-radius: 6px; padding: 6px;")
        self.search_button.clicked.connect(self.search_videos)

        search_controls = QHBoxLayout()
        search_controls.addWidget(self.search_bar)
        search_controls.addWidget(self.search_button)

        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #2C2F33;
                color: white;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #5865F2;
                border-radius: 6px;
            }
        """)

        self.download_btn = QPushButton("Download")
        self.download_btn.setStyleSheet("background-color: #5865F2; color: white; border-radius: 6px; padding: 8px;")
        self.download_btn.clicked.connect(self.download_video)

        self.progress = QProgressBar()
        self.progress.setStyleSheet("QProgressBar {background: #23272A; color: white; border-radius: 6px;} QProgressBar::chunk {background: #5865F2;}")
        self.progress.setValue(0)

        search_layout.addLayout(search_controls)
        search_layout.addWidget(self.results_list)
        search_layout.addWidget(self.download_btn)
        search_layout.addWidget(self.progress)

        # --- Settings Page ---
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)

        # Output folder
        self.folder_label = QLabel(f"Download Folder: {self.output_dir}")
        self.folder_label.setStyleSheet("color: white;")
        self.folder_btn = QPushButton("Change Folder")
        self.folder_btn.setStyleSheet("background-color: #5865F2; color: white; border-radius: 6px;")
        self.folder_btn.clicked.connect(self.change_folder)

        # Search limit
        self.limit_spin = QSpinBox()
        self.limit_spin.setValue(self.search_limit)
        self.limit_spin.setRange(1, 50)
        self.limit_spin.setStyleSheet("color: white; background-color: #23272A; border-radius: 6px;")

        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mp3"])
        self.format_combo.setCurrentText(self.download_format)
        self.format_combo.setStyleSheet("color: white; background-color: #23272A; border-radius: 6px;")

        # Save button
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setStyleSheet("background-color: #5865F2; color: white; border-radius: 6px; padding: 8px; max-width: 120px;")
        self.save_btn.clicked.connect(self.save_settings)

        settings_layout.addWidget(self.folder_label)
        settings_layout.addWidget(self.folder_btn)
        settings_layout.addWidget(QLabel("Search Results Limit:", self))
        settings_layout.addWidget(self.limit_spin)
        settings_layout.addWidget(QLabel("Download Format:", self))
        settings_layout.addWidget(self.format_combo)
        settings_layout.addWidget(self.save_btn)
        settings_layout.addStretch()

        self.stack.addWidget(search_page)
        self.stack.addWidget(settings_page)

        # Add to main layout
        main_layout.addLayout(self.sidebar, 1)
        main_layout.addWidget(self.stack, 4)

        self.setStyleSheet("background-color: #36393F; font-family: Arial; font-size: 12pt;")

    # --- Logic ---
    def search_videos(self):
        query = self.search_bar.text().strip()
        if not query:
            return

        self.results_list.clear()
        self.progress.setValue(0)

        def perform_search():
            try:
                ydl_opts = {'quiet': True, 'extract_flat': True, 'skip_download': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(f"ytsearch{self.limit_spin.value()}:{query}", download=False)

                entries = result.get("entries", [])
                self.video_entries = [{'title': e['title'], 'url': f"https://www.youtube.com/watch?v={e['id']}"} for e in entries]

                self.results_list.clear()
                for v in self.video_entries:
                    item = QListWidgetItem(v['title'])
                    self.results_list.addItem(item)

            except Exception as e:
                self.results_list.addItem(f"Error: {e}")

        threading.Thread(target=perform_search, daemon=True).start()

    def download_video(self):
        selected = self.results_list.currentRow()
        if selected == -1:
            return
        video_url = self.video_entries[selected]['url']

        self.progress.setValue(0)

        def run_download():
            fmt = self.format_combo.currentText()
            if fmt == "mp3":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                    'progress_hooks': [self.hook],
                }
            else:
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.hook],
                }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            except Exception as e:
                self.results_list.addItem(f"Download failed: {e}")

        # Meh Meh Meh why are you threading this, you dont need to do that, it uses more resources
        # Shut up, it stops the entire app and feels clunky without it, youre running a pc not a commadore 83
        threading.Thread(target=run_download, daemon=True).start()

    def hook(self, d):
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                self.progress.setValue(percent)
        elif d['status'] == 'finished':
            self.progress.setValue(100)

    def change_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.output_dir = folder
            self.folder_label.setText(f"Download Folder: {self.output_dir}")

    # --- Settings JSON ---
    def save_settings(self):
        self.search_limit = self.limit_spin.value()
        self.download_format = self.format_combo.currentText()

        settings = {
            "output_dir": self.output_dir,
            "search_limit": self.search_limit,
            "download_format": self.download_format
        }

        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                self.output_dir = settings.get("output_dir", os.getcwd())
                self.search_limit = settings.get("search_limit", 10)
                self.download_format = settings.get("download_format", "mp4")
            except Exception:
                self.output_dir = os.getcwd()
                self.search_limit = 10
                self.download_format = "mp4"
        else:
            self.output_dir = os.getcwd()
            self.search_limit = 10
            self.download_format = "mp4"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = YouTubeDownloader()
    win.show()
    sys.exit(app.exec_())
