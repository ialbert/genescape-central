import PySimpleGUI as sg
import os, sys
import webbrowser

from genescape import server

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
IMG_PATH = os.path.join(CURR_DIR, "data", "demo.png")

if not os.path.isfile(IMG_PATH):
    raise ValueError(f"Image file not found: {IMG_PATH}")

IMG_KEY = '-IMAGE-'

# A global variable to control the server's loop
RUNNING = False

def run():
    global RUNNING

    import PySimpleGUI as sg
    import threading

    # Function to start the server
    def start():
        threading.Thread(target=server.run, daemon=True).start()
        threading.Timer(1, lambda: webbrowser.open("http://localhost:8000")).start()

    # Define the layout of the GUI
    font = ('Verdana', 20)

    layout = [
        [
            sg.Text('Host:', font=font),
            sg.InputText('localhost', font=font, key='-HOST-', size=(10, 1)),
            sg.Text('Port:', font=font),
            sg.InputText('8080', font=font, key='-PORT-', size=(4, 1))
        ],
        [
            sg.Button(' Start Server', font=font, key='-START-'),
            sg.Button(' Stop Server', font=font, key='-STOP-')
        ],
        [
            sg.Multiline(size=(60, 10), font=font, key='-MESSAGES-', autoscroll=True, disabled=True)
        ]
    ]

    # Create the Window
    window = sg.Window('GeneScape', layout)


    def print_message(message):
        window['-MESSAGES-'].update(message, append=True)

    class Capture:
        def __init__(self, window, key):
            self.window, self.key = window, key
            self.stdout = sys.stdout  # Save a reference to the original stdout

        def write(self, message):
            # Redirect stdout to both the text area and the original stdout
            self.stdout.write(message)
            print_message(message)

        def flush(self):
            # This method is required for compatibility with the file-like interface.
            self.stdout.flush()

    # Capture the standard output and error
    sys.stderr = Capture(window, '-MESSAGES-')
    sys.stdout = Capture(window, '-MESSAGES-')

    # Event Loop to process "events"
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
            break
        elif event == '-START-':
            start()
        elif event == '-STOP-':
            break

    window.close()


if __name__ == "__main__":
    run()
