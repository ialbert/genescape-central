import sys, os
from genescape.bottle import route, run, template

from genescape.bottle import Bottle, static_file, template

# The current directory.
CURR_DIR = os.path.dirname(os.path.realpath(__file__))

# The directory containing the templates.
TEMPLATE_DIR = os.path.join(CURR_DIR, "templates")

# The user's home directory.
HOME_DIR = os.path.expanduser("~")

# Default genescape directory
GENESCAPE_DIR = os.path.join(HOME_DIR, "genescape")

app = Bottle()

@app.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static')

@app.route('/')
def home():
    return 'Welcome to the home page! Access static files at /static/<filename>'


def serve():
    # You need to restart the server on each request to check the global variable
    # This is a workaround and might not be the most efficient way to handle this.
    try:
        run(host='localhost', port=8080, reloader=True)
    except Exception as e:
        print(f"Server Error: {e}", sys.stderr)

if __name__ == "__main__":
    serve()
