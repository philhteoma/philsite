from philsite import app, request, session, render_template, redirect, send_from_directory
import os, time
import philsite.project_neural.network as net_gen

path = "/neural_net"
dir_name="project_neural/"
app_dir = os.getcwd()
static_dir = app_dir + "/philsite/project_neural/static"

network = net_gen.Network([2, 1, 1, 3], threshold=0.5)
network.export_graph()
training_data = net_gen.TrainingData(network, [([0, 0], [0]), ([0, 1], [1]), ([1, 0], [1]), ([1, 1], [0])])

@app.route("/neural_static/<path:filename>")
def neural_static(filename):
    return send_from_directory(static_dir, filename)

@app.route(path)
def neural_index():
    return render_template(dir_name+"templates/neural_net.html", network=network, training_data=training_data)


@app.route(path+"/new_net", methods=["GET", "POST"])
def generate_new_net():
    if request.method == "POST":
        print(request.form)
        data = request.form
        network = net_gen.Network([int(data["inputs"]),
                                    int(data["outputs"]),
                                    int(data["hidden_layers"]),
                                    int(data["hidden_neurons"])],
                                    threshold=0.5)
        network.export_graph()
    return redirect(path)

@app.route(path+"/propagate", methods=["GET", "POST"])
def propagate():
    if request.method == "POST":
        data = request.form
        inputs = [(int(x[-1]), int(y)) for x, y in data.items() if x[:5] == "input"]
        inputs = [y for x, y in sorted(inputs, key=lambda tup: tup[0])]
        network.propagate(inputs)
        network.export_graph()
    return redirect(path)

@app.route(path+"/darwin_train", methods=["GET", "POST"])
def darwin_train():
    if request.method == "POST":
        global network
        reps = int(request.form["repititions"])
        if reps > 200:
            reps = 200
        trainer = net_gen.RandomTrainer(2)
        network = trainer.train(network, training_data.data, reps)
        network.export_graph(print_values=False)
    return redirect(path)

@app.route(path+"/new_data", methods=["GET", "POST"])
def add_data():
    if request.method == "POST":
        data = request.form
        print(data)
        inputs = [(int(x[-1]), int(y)) for x, y in data.items() if x[:5] == "input"]
        inputs = [y for x, y in sorted(inputs, key=lambda tup: tup[0])]
        outputs = [(int(x[-1]), int(y)) for x, y in data.items() if x[:6] == "output"]
        outputs = [y for x, y in sorted(outputs, key=lambda tup: tup[0])]
        training_data.add_data(inputs, outputs)
    return redirect(path)

@app.route(path+"/clear_data")
def clear_data():
    training_data.clear()
    return redirect(path)
