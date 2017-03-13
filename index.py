from flask import Flask, render_template, request, make_response, redirect
import socket

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("projects.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

if __name__ == "__main__":

    host_name = socket.gethostname()

    if host_name == "Gavbot":
        bind = "192.168.1.3"
        port = 80 #remote
    else:
        bind = "127.0.0.1" #local
        port = 5000

    if len(sys.argv) == 2:
        bind = sys.argv[1]


    app.run(host=bind, port=port)
