import os
import tkinter as tk
from tkinter import scrolledtext
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_FILE_PATH = r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\Game.log"
FILTER_WORDS_YELLOW = ["Player", "Pizzaking"]
FILTER_WORDS_ORANGE = ["Kill", "Killed"]

# Variabele om bij te houden of de gebruiker aan het scrollen is
scrolling = False

# Functie om te markeren op basis van zoekwoorden
def highlight_words():
    # Verwijder eerdere markeringen
    text_area.tag_remove("highlight_yellow", "1.0", tk.END)
    text_area.tag_remove("highlight_orange", "1.0", tk.END)

    def highlight(word, tag):
        start_idx = "1.0"
        while True:
            start_idx = text_area.search(word, start_idx, stopindex=tk.END, nocase=True)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(word)}c"
            text_area.tag_add(tag, start_idx, end_idx)
            start_idx = end_idx

            # Zoek naar citaten rond het woord
            match = re.search(r"'.*?'", text_area.get(start_idx, tk.END))
            if match:
                quote_start = f"{start_idx}+{match.start()}c"
                quote_end = f"{start_idx}+{match.end()}c"
                text_area.tag_add(tag, quote_start, quote_end)

    # Markeer de woorden voor gele en oranje tags
    for word in FILTER_WORDS_YELLOW:
        highlight(word, "highlight_yellow")
    for word in FILTER_WORDS_ORANGE:
        highlight(word, "highlight_orange")

    # Pas de styling toe
    text_area.tag_config("highlight_yellow", foreground="yellow", font=("Courier", 12, "bold"))
    text_area.tag_config("highlight_orange", foreground="orange", font=("Courier", 12, "bold"))

# Update de weergave van het logbestand
def update_log_display():
    if not os.path.exists(LOG_FILE_PATH):
        text_area.insert(tk.END, "Game.log niet gevonden!\n")
        return

    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    filtered_lines = [line for line in lines if any(word in line for word in FILTER_WORDS_YELLOW + FILTER_WORDS_ORANGE)]

    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, "".join(filtered_lines))
    highlight_words()
    text_area.config(state=tk.DISABLED)

    # Automatisch scrollen als de gebruiker niet aan het scrollen is
    if not scrolling:
        text_area.yview(tk.END)

# Periodieke controle van het logbestand
def check_log_file():
    update_log_display()
    root.after(1000, check_log_file)

# Functie om te detecteren wanneer de gebruiker scrollt
def on_scroll(event):
    global scrolling
    scrolling = True

# Functie om de scrollstatus terug te zetten na het stoppen van de scroll
def on_mouse_release(event):
    global scrolling
    scrolling = False

# Watchdog om veranderingen in het logbestand te detecteren
class LogFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == LOG_FILE_PATH:
            update_log_display()

# Setup Watchdog
observer = Observer()
event_handler = LogFileHandler()
observer.schedule(event_handler, os.path.dirname(LOG_FILE_PATH), recursive=False)
observer.start()

# GUI Setup
root = tk.Tk()
root.title("Star Citizen Log Monitor")
root.geometry("800x600")
root.configure(bg="black")

# Text Area Setup
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 12), bg="black", fg="white", insertbackground="white", state=tk.DISABLED)
text_area.pack(expand=True, fill=tk.BOTH)

# Bind de scroll en mouse release events
text_area.bind("<ButtonRelease-1>", on_mouse_release)
text_area.bind("<B1-Motion>", on_scroll)

# Start de periodieke controle van het logbestand
root.after(1000, check_log_file)

# Stop observer bij sluiten
def on_closing():
    observer.stop()
    observer.join()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
