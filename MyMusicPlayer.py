import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame.mixer as mixer
import pygame
import os
from PIL import Image
import threading
import time
from config import PREV_PATH, PAUSE_PATH, PLAY_PATH, RSUME_PATH, NEXT_PATH, LOGO_PATH


DEFAULT_DIR = "D:\\songs\\B"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class App(ctk.CTk):

    prev_icon = ctk.CTkImage(light_image=Image.open(PREV_PATH), size=(30, 30))
    pause_icon = ctk.CTkImage(light_image=Image.open(PAUSE_PATH), size=(30, 30))
    play_icon = ctk.CTkImage(light_image=Image.open(PLAY_PATH), size=(30, 30))
    resume_icon = ctk.CTkImage(light_image=Image.open(RSUME_PATH), size=(30, 30))
    next_icon = ctk.CTkImage(light_image=Image.open(NEXT_PATH), size=(30, 30))

    def __init__(self):
        super().__init__()
        self.title("My Music Player")
        self.resizable(0, 0)
        self.iconbitmap(LOGO_PATH)

        self.music_files = []
        self.current_song_index = 0
        self.is_playing = False
        self.is_paused = False
        self.loop = True
        self.song_length = 0
        self.seek_position = 0  # Stores the current seek position

        # Initialize mixer
        mixer.init()

        # UI Setup
        self.setup_ui()
        self.select_folder(False)

        # Start progress update in the main thread
        self.update_progress_bar()

    def setup_ui(self):
        """Sets up the UI elements for the music player."""
        self.topFrame = ctk.CTkFrame(self)
        self.topFrame.pack(fill="x", padx=10, pady=10)

        self.lblheading = ctk.CTkLabel(self.topFrame, text="Select Music Folder:", font=("Arial", 14, "bold"))
        self.lblheading.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.folder_button = ctk.CTkButton(self.topFrame, text="📁 Browse", width=100, command=self.select_folder)
        self.folder_button.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        self.musicbox = ctk.CTkComboBox(self.topFrame, values=["Select a Song"], command=self.play_selected_song)
        self.musicbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="we")

        # Playback Controls
        self.bottomFrame = ctk.CTkFrame(self)
        self.bottomFrame.pack(fill="x", expand=True, padx=10, pady=10, ipadx=10)

        self.imgFrame = ctk.CTkLabel(self.bottomFrame, text="🎵", font=("Arial", 50))
        self.imgFrame.pack(pady=10)
        
        self.musicName = ctk.CTkLabel(self.bottomFrame, text="Song Name", font=("Arial", 15), text_color="gray")
        self.musicName.pack(pady=(5,0), anchor="w", padx=10)

        self.musicBar = ctk.CTkProgressBar(self.bottomFrame, orientation="horizontal", width=300)
        self.musicBar.pack(pady=5)
        self.musicBar.set(0)
        self.musicBar.bind("<Button-1>", self.seek_music)

        self.btnsFrame = ctk.CTkFrame(self.bottomFrame)
        self.btnsFrame.pack(pady=10)

        self.prevPlay = ctk.CTkButton(self.btnsFrame, image=self.prev_icon, text="", width=50, fg_color="transparent", command=self.prev_song)
        self.prevPlay.grid(row=0, column=0, padx=5)

        self.pause = ctk.CTkButton(self.btnsFrame, image=self.pause_icon, text="", width=50, fg_color="transparent", command=self.pause_music)
        self.pause.grid(row=0, column=1, padx=5)

        self.playbtn = ctk.CTkButton(self.btnsFrame, image=self.play_icon, text="", width=50, fg_color="transparent", command=self.play_music)
        self.playbtn.grid(row=0, column=2, padx=5)

        self.resume = ctk.CTkButton(self.btnsFrame, image=self.resume_icon, text="", width=50, fg_color="transparent", command=self.resume_music)
        self.resume.grid(row=0, column=3, padx=5)

        self.nextPlay = ctk.CTkButton(self.btnsFrame, image=self.next_icon, text="", width=50, fg_color="transparent", command=self.next_song)
        self.nextPlay.grid(row=0, column=4, padx=5)

    def select_folder(self, ask = True):
        """Opens a file dialog to select a folder containing music files."""
        if ask:
            folder_path = filedialog.askdirectory()
        else:
            folder_path = DEFAULT_DIR
        if folder_path:
            self.music_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.mp3', '.wav'))]
            if not self.music_files:
                messagebox.showinfo("No Music Files", "The selected folder does not contain any music files.")
            else:
                self.musicbox.configure(values=[os.path.basename(f) for f in self.music_files])
                self.musicbox.set("Select a Song")
                self.current_song_index = 0
                self.play_music()

    def play_selected_song(self, choice):
        """Plays the song selected from the combobox."""
        selected_song = self.musicbox.get()
        if selected_song != "Select a Song":
            for index, file_path in enumerate(self.music_files):
                if os.path.basename(file_path) == selected_song:
                    self.current_song_index = index
                    self.play_music()
                    break

    def play_music(self):
        """Plays the selected song."""
        if self.music_files:
            while self.current_song_index < len(self.music_files):
                try:
                    self.musicName.configure(text=os.path.basename(self.music_files[self.current_song_index]))
                    mixer.music.load(self.music_files[self.current_song_index])
                    mixer.music.play()
                    self.is_playing = True
                    self.is_paused = False
                    self.song_length = mixer.Sound(self.music_files[self.current_song_index]).get_length()

                    mixer.music.set_endevent(pygame.USEREVENT)
                    self.after(500, self.check_music_end)
                    return  # If song plays successfully, exit the function
                except pygame.error:
                    print(f"Error playing {self.music_files[self.current_song_index]}. Skipping to the next song.")
                    self.current_song_index = (self.current_song_index + 1) % len(self.music_files)

            # If all songs are corrupt, stop playing
            self.is_playing = False
            messagebox.showerror("Playback Error", "No valid songs could be played.")


    def check_music_end(self):
        """Checks if the song has ended and plays the next song."""
        if not mixer.music.get_busy() and self.is_playing and not self.is_paused:
            self.next_song()
        self.after(500, self.check_music_end)

    def pause_music(self):
        """Pauses the currently playing song."""
        if self.is_playing and not self.is_paused:
            mixer.music.pause()
            self.is_paused = True

    def resume_music(self):
        """Resumes the paused song."""
        if self.is_playing and self.is_paused:
            mixer.music.unpause()
            self.is_paused = False

    def prev_song(self):
        """Plays the previous song in the list."""
        if self.music_files:
            self.current_song_index = (self.current_song_index - 1) % len(self.music_files)
            self.play_music()
            self.seek_position = 0

    def next_song(self):
        """Plays the next song in the list."""
        if self.music_files:
            self.current_song_index = (self.current_song_index + 1) % len(self.music_files)
            self.play_music()
            self.seek_position = 0
            
    def seek_music(self, event):
        """Seek to a specific position in the song."""
        if self.music_files and self.is_playing:
            x = event.x
            width = self.musicBar.winfo_width()
            seek_pos = x / width
            self.seek_position = seek_pos * self.song_length  # Store seek position

            mixer.music.play(start=self.seek_position)  # Play from new position

    def update_progress_bar(self):
        """Updates the progress bar in the main thread."""
        if self.is_playing and not self.is_paused:
            current_pos = (self.seek_position + mixer.music.get_pos() / 1000)  # Adjust position
            if self.song_length > 0:
                self.musicBar.set(current_pos / self.song_length)
        self.after(1000, self.update_progress_bar)


app = App()
app.mainloop()