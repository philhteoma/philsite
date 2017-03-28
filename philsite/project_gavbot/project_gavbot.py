from philsite import app, request, session, render_template, redirect, send_from_directory
import philsite.project_gavbot.gavbot_page_manager as gavbot_page_manager
import os

current_bots = {}
logged_sessions = []
path = "/gavbot"

dir_name="project_gavbot/"
app_dir = os.getcwd()
static_dir = app_dir + "/philsite/project_gavbot/static"

@app.route("/gavbot_static/<path:filename>")
def gavbot_static(filename):
    return send_from_directory(static_dir, filename)

@app.route(path)
def gavbot_index():
    if request.remote_addr not in logged_sessions:
        logged_sessions.append(request.remote_addr)
        gavbot_log_addr(request.remote_addr)
    if 'username' in session:
        print(current_bots[session['username']].current_page)
        return render_template(dir_name+"templates/gavbot_index.html", gavbot=current_bots[session['username']])
    else:
        return render_template(dir_name+"templates/gavbot_index_null.html")

@app.route(path+"/login", methods=["GET", "POST"])
def gavbot_login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        current_bots[session["username"]] = gavbot_page_manager.Gavbot(session["username"])
        return redirect("/gavbot")

@app.route(path+"/logout")
def gavbot_logout():
    session.pop("username", None)
    return redirect("/gavbot")

@app.route(path+"/reset")
def gavbot_reset():
    current_bots[session['username']].reset_gavbot()
    return redirect("/gavbot")

@app.route(path+"/page/", defaults={'path': ''})
@app.route(path+"/page/<path:path>")
def gavbot_move_page(path):
    if 'username' in session:
        current_bots[session['username']].user_update_page(path)
        return redirect("/gavbot")
    else:
        return redirect("/gavbot")

def gavbot_log_addr(ip):
    with open("philsite/log/log.txt", "a") as file:
        file.write(ip + "\n")
