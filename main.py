from gui import AppGUI
from spotify_api import run_http_server
import threading

def main():
    gui = AppGUI()
    gui.run()

if __name__ == "__main__":
    # Start the HTTP server for handling Spotify authentication
    server_thread = threading.Thread(target=run_http_server)
    server_thread.daemon = True
    server_thread.start()
    
    main()