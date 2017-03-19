from philsite import app, render_template, os, sys, json, request
import philsite.project_noble_hq.nobles_management as nobles_management

NobleManager = nobles_management.NobleManager("philsite/project_noble_hq/nobles_dictionary.json", "philsite/project_noble_hq/noblenames.json")
path = "/noble_hq"

@app.route(path)
def noblehq():
    name_list = NobleManager.id_lookup
    return render_template("noblehq_template.html", name_list = name_list)

@app.route(path+"/noblepost", methods=["GET", "POST"])
def noblepost():
    name_list = NobleManager.id_lookup
    try:
        if request.method == "GET":
            pass
        if request.method == "POST":
            action = (request.form["action"])
            if action == "viewInfo":
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

@app.route(path+"/createnoble", methods=["GET"])
def createnoble():
    function_return = NobleManager.create_noble()
    name_list = NobleManager.id_lookup
    name_list = list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route(path+"/deleteall", methods=["GET"])
def deleteall():
    function_return = NobleManager.execute_all()
    name_list = NobleManager.id_lookup
    name_list = list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

@app.route(path+"/nobles_play", methods=["POST"])
def nobles_play():
    function_return = NobleManager.run_events()
    name_list = NobleManager.id_lookup
    name_list = list_to_option_string(name_list)
    response = (function_return, name_list)
    json_response = json.dumps(response)
    return json_response

def list_to_option_string(option_list):
    """Takes a list with tuple elements and returns a string to be used in an html document.
    The format is (option_text, option_value)"""
    string = ""
    for item in option_list:
        name = item[0]
        ident = item[1]
        string +=('<option value="%s">%s</option>' % (ident, name))
    return string
