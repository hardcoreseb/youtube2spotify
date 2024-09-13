from youtube_api import validate_youtube_link, extraxt_playlist_id, retrieve_playlist_elements
from spotify_api import authenticate_spotify, create_playlist, filter_for_title, search_titles_in_spotify, add_tracks_to_playlist
from PIL import Image

import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

class AppGUI:
    width = 650
    height = 500

    def __init__(self) -> None:
        self.root = customtkinter.CTk()
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(False, False)
        self.root.title("Youtube2Spotify")
        self.root.iconbitmap(r"assets/ytb2sptfy.ico")

        default_font = customtkinter.CTkFont(family="system-ui", size=16)
        logo_image = customtkinter.CTkImage(
            light_image=Image.open('assets/yt2sptfy_nobg.png'), 
            dark_image=Image.open('assets/yt2sptfy_nobg.png'),
            size=(100,100)
            )
        
        self.frame = customtkinter.CTkFrame(master=self.root)
        self.frame.pack(pady=24, padx=40, fill="both", expand=True)

        self.logo_image_label = customtkinter.CTkLabel(master=self.frame, text="", image=logo_image)
        self.logo_image_label.pack(pady=(0,0), padx=16)

        self.label = customtkinter.CTkLabel(master=self.frame, text="Youtube2Spotify Converter", font=customtkinter.CTkFont(family="system-ui", size=24))
        self.label.pack(pady=(8,32), padx=16)

        self.entryLabel = customtkinter.CTkLabel(master=self.frame, text="Please insert a full YouTube playlist link", font=default_font)
        self.entryLabel.pack(pady=(24,8), padx=16)

        self.entry = customtkinter.CTkEntry(master=self.frame, placeholder_text="example: https://www.youtube.com/playlist?list=PLy6N_9yB8Qwy6LL0J7zLUyW8XNX-BPeDl", width=400, height=40)
        self.entry.pack(pady=8, padx=16)
        self.entry.bind("<Return>", self.check)


        self.button = customtkinter.CTkButton(master=self.frame, text="Get all Playlist Elements", command=self.check, font=default_font)
        self.button.pack(pady=(16,40), padx=24, ipady=4, ipadx=4, side="bottom")

        self.labelDone = customtkinter.CTkLabel(master=self.frame, text="Done!", font=default_font)
        

    def check(self, event = None):
        link = self.entry.get()
        print("Hello")
        if validate_youtube_link(link):
            print("Working so far")
            playlist_id = extraxt_playlist_id(link)
            print(playlist_id)
            retrieve_playlist_elements(playlist_id)
            sp = authenticate_spotify()
            playlist_info = create_playlist(sp)
            spotify_playlist_id = playlist_info["id"]
            titles = filter_for_title()
            spotify_uris = search_titles_in_spotify(sp, titles)
            print("Spotify URIs:", spotify_uris)
            add_tracks_to_playlist(sp, spotify_uris, spotify_playlist_id)

            
            self.labelDone.pack(pady=8, padx=16)
            self.labelDone.configure(text="Done!", text_color="white")
        else:
            self.labelDone.pack(pady=8, padx=16)
            self.labelDone.configure(text="Please insert a correct link (FULL YouTube-Playlist link)!", text_color="red")

    def run(self):
        self.root.mainloop()