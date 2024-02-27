from genescape.bottle import route, run, template

@route('/')
def index():
    print("HEHEY")
    return "The server is running!"


def serve():
    # You need to restart the server on each request to check the global variable
    # This is a workaround and might not be the most efficient way to handle this.
    try:
        run(host='localhost', port=8080)
    except Exception as e:
        print(f"Server Error: {e}")

if __name__ == "__main__":
    serve()
