import sys
from flask import Flask, render_template, request, make_response, redirect, session
import re
import jinja2
import os
import json
import socket

app = Flask(__name__)

import philsite.blog_manager
import philsite.project_gavbot.project_gavbot
import philsite.project_noble_hq.project_noble_hq
import philsite.project_wiki_in_the_valley.project_wiki_in_the_valley

app.jinja_env.autoescape = False
host_name = socket.gethostname()
app.secret_key = os.urandom(32)
blog_object = blog_manager.Blog()

#
#-----Main Pages-----
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
