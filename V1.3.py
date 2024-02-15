import tkinter as tk
from tkinter import *
from tkinter import messagebox
from youtubesearchpython import VideosSearch
from pytube import YouTube
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

        # My Warning Label for user experience (yes keep this, otherwise users will close out of it)
        self.warn_label = Label(self,
                                text="~When you click play nothing will happen, "
                                " just wait it works in the background~",
                                background=BG,
                                )
        self.warn_label.grid(column=0, row=3, ipady=10, columnspan=2)

    def search_videos(self):
        query = self.search_entry.get()

        if query:
            videos_search = VideosSearch(query, limit=10)
            results = videos_search.result()['result']

            # Clear previous results from the listbox
            self.results_listbox.delete(0, tk.END)

            # Populate listbox with search results
            for idx, result in enumerate(results, start=1):
                self.results_listbox.insert(tk.END, f"{idx}. {result['title']}")

    def play_selected_video(self):
        selected_index = self.results_listbox.curselection()

        if selected_index:
            index = int(selected_index[0])  # Converts to integer
            query = self.search_entry.get()
            videos_search = VideosSearch(query, limit=10)
            video_url = videos_search.result()['result'][index]['link']

            # Start a new thread to download the video
            threading.Thread(target=self.download_video, args=(video_url,)).start()

    def download_video(self, video_url):
        try:
            yt = YouTube(video_url)
            video_stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
            video_stream.download()
            downloaded_file_path = f"{yt.title}.mp4"
            self.play_locally(downloaded_file_path)
        except Exception as e:
            print(f"Error: {e}")

    @staticmethod
    def play_locally(file_path):
        try:
            os.startfile(file_path)
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"Could not open the media file:\n{e}")


if __name__ == "__main__":
    app = YouTubePlayer()
    app.mainloop()
