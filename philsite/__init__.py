import sys
from flask import Flask, render_template, request, make_response, redirect, session, send_from_directory, make_response, g
import requests
import re
import jinja2
import os
import json
import socket

#import xml.etree.ElementTree

app = Flask(__name__, template_folder="")

app_dir = os.path.dirname(os.path.realpath(__file__))
module_dir = "/".join(app_dir.split("/")[:-1])
sys.path.insert(0, module_dir)


import philsite.blog_manager
import philsite.project_gavbot.project_gavbot
import philsite.project_noble_hq.project_noble_hq
import philsite.project_wiki_in_the_valley.project_wiki_in_the_valley
import philsite.project_neural.project_neural

app.jinja_env.autoescape = False
host_name = socket.gethostname()
app.secret_key = os.urandom(32)
blog_object = blog_manager.Blog(app_dir)


print(app_dir)

dir_name = "main/"
static_dir = app_dir + "/main/static"

#
#-----Object for app directory-----
#

class AppDir:
    def __init__(self, dir_name):
        self.dir_name = dir_name

directory = AppDir(app_dir)


#
#-----Custom Static Code-----
#

@app.route("/main_static/<path:filename>")
def main_static(filename):
    return send_from_directory(static_dir, filename)


#
#-----Main Pages-----
#

@app.route("/")
def index():
    return render_template(dir_name+"templates/index.html", dir_name=dir_name, main_static=main_static)

@app.route("/projects")
def projects():
    return render_template(dir_name+"templates/projects.html", dir_name=dir_name, main_static=main_static)

@app.route("/links")
def links():
    return render_template(dir_name+"templates/links.html", dir_name=dir_name, main_static=main_static)

@app.route("/physics")
def physicsGame():
    return render_template("physicsGame/HTML5/HtmlPerformanceTesting.html")

#
#-----About page to be added later-----
#

# @app.route("/about")
# def about():
#     return render_template(dir_name+"templates/about.html", dir_name=dir_name, main_static=main_static)


#-----Blog-----
#

@app.route("/blog")
def blog():
    page_object = blog_object.load_page()
    return render_template(dir_name+"templates/blog.html", blog=blog_object, page=page_object, dir_name=dir_name, main_static=main_static)

@app.route('/blog/', defaults={'path': ''})
@app.route('/blog/<path:path>')
def blog_request(path):
    print(path)
    page_object = blog_object.load_page(path)
    if page_object.request:
        return redirect("/blog/{}".format(page_object.formal_name))
    else:
        return render_template(dir_name+"templates/blog.html", blog=blog_object, page=page_object, dir_name=dir_name, main_static=main_static)

@app.route("/rss.xml")
def rss():
    with open ("rss.xml", "r") as file:
        rss_file = file.read()
    return(rss_file)


#
#-----Making it run-----
#

if __name__ == "__main__":

    host_name = socket.gethostname()
    print(host_name)


    #if host_name == "Gavbot":
    #bind = "192.168.1.3"
    #port = 80 #remote
    #else:
    #    bind = "127.0.0.1" #local
    #    port = 5000
    
    bind = "51.104.43.112"
    port = 2000
    
    app.run(host=bind, port=port)
    #app.run()
