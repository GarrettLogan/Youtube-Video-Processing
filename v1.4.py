import tkinter as tk
from tkinter import *
from tkinter import messagebox
from youtubesearchpython import VideosSearch
import yt_dlp
import os
import threading

BG = "#FFEBD8"


class YouTubePlayer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("480x320")
        self.title("YouTube Player")
        self.configure(background=BG, padx=20)
        self.iconbitmap('dl-icon.ico')

        self.download_button_image = PhotoImage(file="dl-btn.png")
        self.download_button_image = self.download_button_image.subsample(4, 4)
        self.search_button_image = PhotoImage(file="src-btn.png")
        self.search_button_image = self.search_button_image.subsample(4, 4)

        # Entry for YouTube search
        self.search_entry = Entry(self, width=50)
        self.search_entry.grid(column=0, row=0, ipadx=10, ipady=5)

        # Button to initiate search
        self.search_button = Button(self,
                                    image=self.search_button_image,
                                    command=self.search_videos,
                                    bd=0,
                                    highlightthickness=0,
                                    bg=BG,
                                    padx=20
                                    )
        self.search_button.grid(column=1, row=0, ipady=10)

        # Listbox to display search results
        self.results_listbox = tk.Listbox(self, width=50, height=10, selectmode=tk.SINGLE)
        self.results_listbox.grid(column=0, row=1, ipady=10)

        # Button to play the selected video
        self.play_button = Button(self,
                                  image=self.download_button_image,
                                  command=self.play_selected_video,
                                  bd=0,
                                  highlightthickness=0,
                                  bg=BG,
                                  padx=20
                                  )
        self.play_button.grid(column=1, row=1, ipady=10)

        # Warning Label for user experience
        self.warn_label = Label(self,
                                text="~When you click play nothing will happen, "
                                " just wait it works in the background~",
                                background=BG,
                                )
        self.warn_label.grid(column=0, row=3, ipady=10, columnspan=2)

    def search_videos(self):
        query = self.search_entry.get()

        if query:
            try:
                videos_search = VideosSearch(query, limit=10)
                results = videos_search.result()['result']

                # Clear previous results from the listbox
                self.results_listbox.delete(0, tk.END)

                # Add items to listbox using search results
                for idx, result in enumerate(results, start=1):
                    self.results_listbox.insert(tk.END, f"{idx}. {result['title']}")
            except Exception as e:
                messagebox.showerror("Search Error", f"An error occurred while searching for videos:\n{e}")

    def play_selected_video(self):
        selected_index = self.results_listbox.curselection()

        if selected_index:
            try:
                index = int(selected_index[0])
                query = self.search_entry.get()
                videos_search = VideosSearch(query, limit=10)
                video_url = videos_search.result()['result'][index]['link']

                # Start a new thread to download the video
                threading.Thread(target=self.download_video, args=(video_url,)).start()
            except Exception as e:
                messagebox.showerror("Selection Error", f"An error occurred while selecting the video:\n{e}")

    def download_video(self, video_url):
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',  # Best video and audio
                'outtmpl': '%(title)s.%(ext)s',  # Output file name based on video title
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',  # Convert to MP4
                }],
                'merge_output_format': 'mp4',  # Ensure merged format is MP4
            }

            # Initialize yt-dlp with the options
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(video_url)
        except Exception as e:
            messagebox.showerror("Download Error", f"An error occurred while downloading the video:\n{e}")

    @staticmethod
    def play_locally(file_path):
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Playback Error", f"Could not open the media file:\n{e}")


if __name__ == "__main__":
    app = YouTubePlayer()
    app.mainloop()