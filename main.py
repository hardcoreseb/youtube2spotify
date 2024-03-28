from gui import AppGUI
from spotify_api import run_http_server, refresh_token
import threading
import time

def main():
    gui = AppGUI()
    gui.run()

if __name__ == "__main__":

    refresh_token_thread = threading.Thread(target=refresh_token)
    refresh_token_thread.daemon = True  # Daemonize the thread
    refresh_token_thread.start()

    # Start the HTTP server for handling Spotify authentication
    server_thread = threading.Thread(target=run_http_server)
    server_thread.daemon = True
    server_thread.start()
    
    main()