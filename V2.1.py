import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox
import threading


def search_videos():
    query = search_entry.get().strip()
    if not query:
        messagebox.showerror("Error", "Please enter a search query.")
        return

    search_button.config(state=tk.DISABLED)
    video_list.delete(0, tk.END)
    status_label.config(text="Searching...")

    def perform_search():
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch10:{query}", download=False)

        root.after(0, update_search_results, result)

    threading.Thread(target=perform_search, daemon=True).start()


def update_search_results(result):
    video_list.delete(0, tk.END)
    search_button.config(state=tk.NORMAL)
    status_label.config(text="Select a video to download")

    if 'entries' in result and result['entries']:
        global video_entries
        video_entries = result['entries']
        for i, entry in enumerate(video_entries):
            video_list.insert(tk.END, f"{i + 1}. {entry['title']}")
    else:
        messagebox.showerror("Error", "No results found.")


def download_video():
    selected_index = video_list.curselection()
    if not selected_index:
        messagebox.showerror("Error", "Please select a video to download.")
        return

    video_url = video_entries[selected_index[0]]['url']
    status_label.config(text="Downloading... Please wait.")
    progress_bar.start()

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'merge_output_format': 'mp4',
    }

    def run_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        root.after(0,
                   lambda: [status_label.config(text="Download complete!"), progress_bar.stop(), show_success_popup()])

    threading.Thread(target=run_download, daemon=True).start()


def show_success_popup():
    popup = tk.Toplevel(root)
    popup.title("Download Complete")
    popup.geometry("300x150")
    popup.configure(bg='#1E1E1E')

    label = ttk.Label(popup, text="The video has been downloaded successfully!", foreground='white',
                      background='#1E1E1E', font=('Arial', 10))
    label.pack(pady=20)

    ok_button = ttk.Button(popup, text="OK", command=popup.destroy)
    ok_button.pack(pady=10)


# GUI Setup
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("550x500")
root.configure(bg='#1E1E1E')

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", foreground='black', background='#D4AF37', font=('Arial', 10, 'bold'), padding=5)
style.configure("TLabel", foreground='white', background='#1E1E1E', font=('Arial', 12))
style.configure("TEntry", fieldbackground='#333333', foreground='white', padding=5)
style.configure("TListbox", background='#2C2C2C', foreground='#D4AF37', font=('Arial', 10))

frame = ttk.Frame(root, padding=10, style="TFrame")
frame.pack(fill=tk.BOTH, expand=True)

search_label = ttk.Label(frame, text="Search YouTube:")
search_label.pack(pady=5)

search_entry = ttk.Entry(frame, width=50)
search_entry.pack(pady=5)

search_button = ttk.Button(frame, text="Search", command=search_videos)
search_button.pack(pady=5)

video_list = tk.Listbox(frame, width=60, height=10, bg='#2C2C2C', fg='#D4AF37', selectbackground='#555555')
video_list.pack(pady=5)

download_button = ttk.Button(frame, text="Download", command=download_video)
download_button.pack(pady=10)

progress_bar = ttk.Progressbar(frame, mode='indeterminate', length=300)
progress_bar.pack(pady=5)

status_label = ttk.Label(frame, text="Enter a query and search for videos", font=('Arial', 10))
status_label.pack(pady=5)

root.mainloop()
