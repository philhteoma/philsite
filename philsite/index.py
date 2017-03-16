import sys
sys.path.append("noble_manager")
sys.path.append("wiki_in_the_valley")
from flask import Flask, render_template, request, make_response, redirect, session
import nobles_management
import re
import jinja2
import gavbot_page_manager
import os
import json
import socket
import blog_manager
import valley_generator

app = Flask(__name__)
app.jinja_env.autoescape = False
current_bots = {}
host_name = socket.gethostname()
app.secret_key = os.urandom(32)
logged_sessions = []
blog_object = blog_manager.Blog()
NobleManager = nobles_management.NobleManager("noble_manager/nobles_dictionary.json", "noble_manager/noblenames.json")
wiki_in_use = False

#
#-----Main Page-----
#

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/links")
def links():
    return render_template("links.html")

@app.route("/about")
def about():
    return render_template("about.html")

#
#-----Blog-----
#

@app.route("/blog")
def blog():
    page_object = blog_object.load_page()
    return render_template("blog.html", blog=blog_object, page=page_object)

@app.route('/blog/', defaults={'path': ''})
@app.route('/blog/<path:path>')
def blog_request(path):
    print(path)
    page_object = blog_object.load_page(path)
    if page_object.request:
        return redirect("/blog/{}".format(page_object.formal_name))
    else:
        return render_template("blog.html", blog=blog_object, page=page_object)

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
def noblehq():
    name_list = NobleManager.id_lookup
    return render_template("noblehq_template.html", name_list = name_list)

@app.route("/noble_hq/noblepost", methods=["GET", "POST"])
def noblepost():
    print("Mark 1")
    name_list = NobleManager.id_lookup
    try:
        if request.method == "GET":
            pass
        if request.method == "POST":
            print("Mark 2")
            action = (request.form["action"])
            if action == "viewInfo":
                print("Mark 3")
                name = NobleManager.get_name_from_id(request.form["noble"])
                function_return = NobleManager.view_single_noble(name)
            if action == "executeNoble":
                name = NobleManager.get_name_from_id(request.form["noble"])
                function_return = NobleManager.execute_noble(name)
        else: return "nothing hahaha"
    except Exception as e:
        print(e)
        return "you ballsed up m8"
    if name_list: name_list = list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route("/noble_hq/createnoble", methods=["GET"])
def createnoble():
    function_return = NobleManager.create_noble()
    name_list = NobleManager.id_lookup
    name_list = list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route("/noble_hq/deleteall", methods=["GET"])
def deleteall():
    function_return = NobleManager.execute_all()
    name_list = NobleManager.id_lookup
    name_list = list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route("/noble_hq/nobles_play", methods=["POST"])
def nobles_play():
    function_return = NobleManager.run_events()
    print(function_return)
    name_list = NobleManager.id_lookup
    name_list = list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

#
#-----Wiki in the Valley-----
#

@app.route("/wiki_in_the_valley_o")
def wiki_in_the_valley_o():
    return render_template("template_in_the_valley_o.html")

@app.route("/wiki_in_the_valley_o/get_song", methods=["POST"])
def get_song():
    global wiki_in_use
    # print("INVOKED")
    url = request.form["url"]
    # print(url[:25])
    if url[:24] != "https://en.wikipedia.org" and url[:25] != "https://www.wikipedia.org":
        return json.dumps(("use a wikipedia url!", "use a wikipedia url!"))
    while True:
        if wiki_in_use == True:
            print("In use, waiting...")
            time.sleep(1)
        elif wiki_in_use == False:
            wiki_in_use = True
            break
    list_and_song = valley_generator.make_a_song(url)
    wiki_in_use = False
    # print("List:\n\n", list_and_song[0])
    # print("Song:\n\n", list_and_song[1])
    list_and_song[0] = list_to_string(list_and_song[0])
    response = json.dumps(list_and_song)
    return response

@app.route("/wiki_in_the_valley_o/about")
def about_wiki():
    return render_template("about_wiki.html")

#
#-----Misc Functions-----
#

def list_to_option_string(option_list):
    """Takes a list with tuple elements and returns a string to be used in an html document.
    The format is (option_text, option_value)"""
    string = ""
    for item in option_list:
        name = item[0]
        ident = item[1]
        string +=('<option value="%s">%s</option>' % (ident, name))
    return string

def list_to_string(the_list):
    string = ""
    for item in the_list:
        string += item
        string += "\n"
    return string

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
