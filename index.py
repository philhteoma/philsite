from flask import Flask, render_template, request, make_response, redirect, session
import sys
import re
import jinja2
import gavbot_page_manager
import os
import json
import socket

app = Flask(__name__)
app.jinja_env.autoescape = False
current_bots = {}
host_name = socket.gethostname()
app.secret_key = os.urandom(32)
logged_sessions = []

#
#-----Main Page-----
#

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

#
#-----Gavbot Rising-----
#

@app.route("/gavbot")
def gavbot_index():
    if request.remote_addr not in logged_sessions:
        logged_sessions.append(request.remote_addr)
        gavbot_log_addr(request.remote_addr)
    if 'username' in session:
        return render_template("gavbot_index.html", gavbot=current_bots[session['username']])
    else:
        return render_template("gavbot_index_null.html")

@app.route("/gavbot/login", methods=["GET", "POST"])
def gavbot_login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        current_bots[session["username"]] = gavbot_page_manager.Gavbot(session["username"])
        return redirect("/gavbot")

@app.route("/gavbot/logout")
def gavbot_logout():
    session.pop("username", None)
    return redirect("/gavbot")

@app.route("/gavbot/reset")
def gavbot_reset():
    current_bots[session['username']].reset_gavbot()
    return redirect("/gavbot")

@app.route('/gavbot/page/', defaults={'path': ''})
@app.route('/gavbot/page/<path:path>')
def gavbot_move_page(path):
    if 'username' in session:
        current_bots[session['username']].update_page(path)
        return redirect("/gavbot")
    else:
        return redirect("/gavbot")

def gavbot_log_addr(ip):
    with open("log/log.txt", "a") as file:
        file.write(ip + "\n")

#
#-----Noble HQ-----
#

@app.route("/noble_hq")
def noble_hq():
    return render_template("null.html")

#
#-----Wiki in the Valley-----
#

@app.route("/wiki_in_the_valley")
def wiki_in_the_valley():
    return render_template("null.html")

#
#-----Making it run-----
#

if __name__ == "__main__":

    host_name = socket.gethostname()

    if host_name == "Gavbot":
        bind = "192.168.1.3"
        port = 80 #remote
    else:
        bind = "127.0.0.1" #local
        port = 5000

    app.run(host=bind, port=port)
