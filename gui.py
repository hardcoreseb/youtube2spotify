import os
from dotenv import load_dotenv, set_key
from youtube_api import validate_youtube_link, extraxt_playlist_id, retrieve_playlist_elements
from spotify_api import authenticate_spotify, create_playlist, filter_for_title, search_titles_in_spotify, add_tracks_to_playlist
from PIL import Image, ImageTk


import customtkinter

# Load environment variables from .env file
load_dotenv()

# Check if required environment variables are set
required_vars = ['SPOTIFY_ID', 'CLIENT_ID', 'CLIENT_SECRET', 'REDIRECT_URI', 'YOUTUBE_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

class AppGUI(customtkinter.CTk):
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

        settings_icon = customtkinter.CTkImage(
            light_image=Image.open('assets/settings_icon.png'),
            dark_image=Image.open('assets/settings_icon.png'),
            size=(20,20)
        )
       
        super().__init__()  # Initialize CTk

        self.frame = customtkinter.CTkFrame(master=self.root)
        self.frame.pack(pady=24, padx=40, fill="both", expand=True)

        self.button = customtkinter.CTkButton(master=self.frame, text="API KEYS", image=settings_icon, command=self.open_toplevel, font=customtkinter.CTkFont(family="system-ui", size=12))
        self.button.pack(pady=10, padx=6, side="top", anchor="ne")
        self.toplevel_window = None

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

    def env(self, event = None):
        print('Clicked')

    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = TopLevelWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it
            self.root.quit()

    def run(self):
        self.root.mainloop()

class TopLevelWindow(customtkinter.CTkToplevel):
    def __init__(self, parent) -> None:
        super().__init__(master=parent)  # Pass the parent to the superclass constructor
        self.geometry("500x400")
        self.resizable(False, False)

        self.label = customtkinter.CTkLabel(self, text="Environment Variables")
        self.label.pack(padx=20, pady=20)

        # Retrieve environment variables
        self.env_vars = {
            'SPOTIFY_ID': os.getenv('SPOTIFY_ID', ''),
            'CLIENT_ID': os.getenv('CLIENT_ID', ''),
            'CLIENT_SECRET': os.getenv('CLIENT_SECRET', ''),
            'REDIRECT_URI': os.getenv('REDIRECT_URI', ''),
            'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY', '')
        }

        self.placeholder = {
            'SPOTIFY_ID': 'abcd1234efgh5678ijkl9012mnop3456',
            'CLIENT_ID': 'abc123def456ghi789jkl012mno345pq',
            'CLIENT_SECRET': '12ab34cd56ef78gh90ij12kl34mn56op',
            'REDIRECT_URI': 'http://localhost:8888/callback',
            'YOUTUBE_API_KEY': 'AIzaSyA1b2C3d4EfGhIjKlMnOpQrStUvWxYzA'
        }

        self.entries = {}
        for var in self.env_vars:
            frame = customtkinter.CTkFrame(self)
            frame.pack(pady=5, padx=20, fill="x")

            label = customtkinter.CTkLabel(frame, text=var)
            label.pack(side="left", padx=(10, 10))

            self.entry = customtkinter.CTkEntry(frame, width=300, height=40, placeholder_text=self.placeholder[var])
            self.entry.pack(side="right", fill="x", expand=False)
            self.entry.insert(0, self.env_vars[var])  # Set the initial text
            self.entry.bind("<Return>", self.update)
            self.entries[var] = self.entry

        self.submit_button = customtkinter.CTkButton(self, text="Update .env-file", command=self.update)
        self.submit_button.pack(pady=20)


        # Create and pack entry widgets with initial text
        # self.create_entry('SPOTIFY_ID', self.env_vars['SPOTIFY_ID'], self.placeholder['SPOTIFY_ID'])
        # self.create_entry('CLIENT_ID', self.env_vars['CLIENT_ID'], self.placeholder['CLIENT_ID'])
        # self.create_entry('CLIENT_SECRET', self.env_vars['CLIENT_SECRET'], self.placeholder['CLIENT_SECRET'])
        # self.create_entry('REDIRECT_URI', self.env_vars['REDIRECT_URI'], self.placeholder['REDIRECT_URI'])
        # self.create_entry('YOUTUBE_API_KEY', self.env_vars['YOUTUBE_API_KEY'], self.placeholder['YOUTUBE_API_KEY'])

    # def create_entry(self, label_text, initial_text, placeholder_text):
    #     frame = customtkinter.CTkFrame(self)
    #     frame.pack(pady=5, padx=20, fill="x")

    #     label = customtkinter.CTkLabel(frame, text=label_text)
    #     label.pack(side="left", padx=(10, 10))

    #     entry = customtkinter.CTkEntry(frame, width=300, height=40, placeholder_text=placeholder_text)
    #     entry.pack(side="right", fill="x", expand=False)
    #     entry.insert(0, initial_text)  # Set the initial text
    #     entry.bind("<Return>", self.update(entry))

    def load_env_vars(self):
        load_dotenv()
        for var in self.env_vars:
            self.env_vars[var] = os.getenv(var, '')

    def update(self, event=None):
        # Handle the entry check or save logic
        for var in self.entries:
            value = self.entries[var].get()
            set_key('.env', var, value)
        ToastNotification(self, "Successfully updated .env file")

class ToastNotification(customtkinter.CTkToplevel):
    def __init__(self, parent, message):
        super().__init__(master=parent)
        self.geometry("400x100")  # Adjust the size as needed
        self.overrideredirect(True)  # Remove window borders and title bar
        self.attributes("-topmost", True)  # Make sure it's on top of other windows

        # Center the toast on the screen
        self.update_idletasks()
        x = parent.winfo_screenwidth() // 2 - 125
        y = parent.winfo_screenheight() // 2 - 50
        self.geometry(f"+{x}+{y}")

        label = customtkinter.CTkLabel(self, text=message, font=("system-ui", 24))
        label.pack(padx=20, pady=20, expand=True)

        # Automatically close the toast after 3 seconds
        self.after(3000, self.destroy)


if __name__ == "__main__":
    gui = AppGUI()
    gui.run()