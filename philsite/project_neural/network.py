import numpy as np
import copy
import statistics as stat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageChops
#import draw_neural_net as printer
import philsite.project_neural.draw_neural_net as printer


#seed random number to make calculations consistent
#np.random.seed(1)

class Neuron:
    """A repeatable class that simulates a neural node. Stores the following information:
        [1] Name and location of neuron (name, layer, number)
        [2] The nodes type (input, output, normal or bias)
        [3] The synapses that terminate at this neuron (input_synapses)
        [4] The synapses that originate from this neuron (output_synapses)
        [5] The Neurons Last recorded value and error during propagation (value, error)"""
    def __init__(self, name, layer, number, neuron_type="normal", threshold=None, threshold_change=None):
        self.name = name
        self.layer = layer
        self.number = number
        self.neuron_type = neuron_type
        self.input_synapses = []
        self.output_synapses = []
        self.value = None
        self.threshold = threshold
        self.threshold_change = threshold_change
        self.error = None

    def __repr__(self):
        return "(Neuron Object. Layer {}, Number {}. Value {}.)".format(self.layer, self.number, self.value)

class Synapse:
    """A synapse linking two neurons together. Knows:
        [1] The neuron it originates from (start_neuron)
        [2] The neuron it terminates at (end_neuron)
        [3] Its own weight (weight)"""
    def __init__(self, start, end, weight=float(0)):
        self.start_neuron = start
        self.end_neuron = end
        self.weight = weight
        self.stored_data = None

    def __repr__(self):
        return "(synapse from ({}, {}) to ({}, {}), Weight {})".format(
            self.start_neuron.layer,
            self.start_neuron.number,
            self.end_neuron.layer,
            self.end_neuron.number,
            self.weight)

class Network:
    """A simulation of a neural network using objects to represent neurons and the synapses between them. Use the following parameters:
        [1] dimensions (list of int) - a list for the dimensions on the network: [input neurons, output neurons, number of hidden layers, number of neurons per hidden layer] (requred)
        [1] input_count (int) - How many input neurons the network should have (required)
        [2] output_count (int) - How many output neurons the network should have (required)
        [3] hidden_layers (int) - How many hidden layers the network hidden_layers (required)
        [4] hidden_layers_count(int) - How many neurons are in each hidden layers (requried)
        [5] random_weights (bool) - True will give each synapse in the network a random weight on generation (Defaults to True)
        [6] threshold (int) - States the value above which a neuron will set its value to 1, and below which will set it to zero. If None, neurons value does not change. (Defaults to None)
        [7] threshold_change (string) - states how a neurons threshold can be modified during trainin. None keeps the value constant. (Defaults to None)
        [8] bias_node (bool) - Tells the network whether to include a bias node (A node with a permenant value of 1 which brnanches to all other non-input nodes) (default to True)"""
    def __init__(self, dimensions, random_weights=True, threshold=None, threshold_change=None, bias_node=False):
        self.input_count = dimensions[0]
        self.output_count = dimensions[1]
        self.hidden_layers_count = dimensions[2]
        self.hidden_layers_neuron_count = dimensions[3]
        self.threshold = threshold
        self.threshold_change = threshold_change
        self.neurons = []
        self.initialise_neurons()
        self.initialise_synapses()
        self.synapses = [[y.input_synapses for y in x] for x in self.neurons]
        self.initialise_bias(bias_node)
        if random_weights: self.randomise_synapse_weights()

    def propagate(self, data):
        """Send data through the network.
            Requires a list of values of equal length to the number of input neurons"""
        if len(data) != len(self.neurons[0]):
            raise AttributeError("Wrong number of data points provided. Expected {}, got {}".format(len(neurons[0]), len(data)))
        for i in range(len(data)):
            self.neurons[0][i].value = data[i]
        for i in range(1, len(self.neurons)):
            current_layer = self.neurons[i]
            for neuron in current_layer:
                total = 0
                for synapse in neuron.input_synapses:
                    total += synapse.start_neuron.value * synapse.weight
                neuron.value = self.stolen_sigmoid_function(total)
                if neuron.threshold:
                    neuron.value = 1 if neuron.value > neuron.threshold else 0

    def train_network_back_propagate(self, data, repititions):
        # for i in range(repititions):
        #     for example in data:
        #         self.propagate(example[0])
        #         result = [x.value for x in self.neurons[-1]]
        #         error = [x-y for x, y in zip(result, data[1])]
        #         error_slopes = [self.stolen_sigmoid_function(x, True) for x in error]len(self.neurons)len(self.neurons) #delta output sums
        #
        #         for i in range(len(self.neurons[-1])):
        #             neuron = self.neurons[-1][i]               #Set Neuron
        #             error_slope = error_slopes[i]              #Set appropriate error slope
        #             for synapse in neuron.input_synapses:
        #                 synapse.stored_data = synapse.weight + (synapse.weight * error_slope))   #Work out new weight ands store it
        #
        #         for i in range(len(self.neurons)-2, 0, -1): #For each layer of neurons, working backwards
        #             for neuron in self.neurons[i]:  #For each neuron in that layer
        #                 pass
        pass

    def initialise_neurons(self):
        """Create the requisite number of neurons in each layer, and store in self.neurons"""
        for layer in range(self.hidden_layers_count+2):
            self.neurons.append([])
            neuron_count = self.hidden_layers_neuron_count
            neuron_type = "normal"
            if layer == 0:
                neuron_type = "input"
                neuron_count = self.input_count
            if layer == self.hidden_layers_count+1:
                neuron_type = "output"
                neuron_count = self.output_count

            for number in range(neuron_count):
                self.neurons[layer].append(Neuron(
                    "Layer {} Neuron {}".format(layer, number),
                    layer,
                    number,
                    neuron_type,
                    self.threshold,
                    self.threshold_change))

    def initialise_synapses(self):
        for i in range(len(self.neurons)-1):
            next_layer_count = len(self.neurons[i+1])
            layer = self.neurons[i]
            for neuron in layer:
                for n in range(next_layer_count):
                    target_neuron = self.neurons[i+1][n]
                    synapse = Synapse(neuron, target_neuron)
                    neuron.output_synapses.append(synapse)
                    target_neuron.input_synapses.append(synapse)

    def initialise_bias(self, bias_node):
        if not bias_node:
            self.bias_node = None
            return
        self.bias_node = Neuron("Bias Node", -1, -1, neuron_type="bias")
        self.bias_node.value = 1
        for layer in self.neurons:
            for neuron in layer:
                if neuron.neuron_type != "input":
                    synapse = Synapse(self.bias_node, neuron)
                    self.bias_node.output_synapses.append(synapse)
                    neuron.input_synapses.append(synapse)

    def randomise_synapse_weights(self):
        for layer in self.synapses:
            for neuron in layer:
                for synapse in neuron:
                    synapse.weight = (2*np.random.random(1)[0]) - 1

    def retrieve_neuron(self, layer, number):
        return self.neurons[layer][number]

    def stolen_sigmoid_function(self, x, deriv=False):
        """With thanks to Andrew Trask
            iamtrask.github.io/2015/7/12/basic-python-network"""
        if deriv == True:
            return x*(1-x)      # Returns the slope of the sigmoid graph at x
        return 1/(1+np.exp(-x)) # 1 over (1 plus e to the power of negative x)

    def print_input_output(self):
        print("input", end=": ")
        for neuron in self.neurons[0]:
            print(round(neuron.value, 2), end = ", ")
        print("Output", end=": ")
        for neuron in self.neurons[-1]:
            print(round(neuron.value, 2), end = ", ")
        print()

    def print_self(self):
        for layer in self.neurons:
            for neuron in layer:
                print("(Neuron {}, {}: Value: {})".format(neuron.layer, neuron.number, neuron.value), end=", ")
            print()

    def print_all(self):
        for layer in self.neurons:
            for neuron in layer:
                print("Name: ", neuron.name)
                print("input_synapses", neuron.input_synapses)
                print("output_synapses", neuron.output_synapses)
                print()

    def export_graph(self, print_values=True):
        fig = plt.figure()
        printer.draw_neural_net(fig.gca(), self, print_values)
        plt.tight_layout()
        fig.set_size_inches(10, 10)
        fig.gca().xaxis.set_major_locator(plt.NullLocator())
        fig.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.savefig("philsite/project_neural/static/diagrams/plot.png", bbox_inches="tight", pad_inches=0)
        im = Image.open("philsite/project_neural/static/diagrams/plot.png")
        im = self.trim(im)
        im.save("philsite/project_neural/static/diagrams/plot.png")

    def trim(self, im):
        bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

class RandomTrainer:
    """A trainer for networks
        Trains by slightly picking the best network out of a group of twenty (using mean squared error) """
    def __init__(self, intensity=10):
        self.intensity = intensity

    def clone_networks(self, network, copies):
        network_list = []
        for i in range(copies):
            network_list.append(copy.deepcopy(network))
        return network_list

    def modulate_weights(self, network):
        for layer in network.synapses:
            for neuron in layer:
                for synapse in neuron:
                    synapse.weight += ((2*(np.random.random(1)[0]))-1)/self.intensity
                    if synapse.weight > 1: synapse.weight = 1
                    if synapse.weight < -1: synapse.weight = -1
        if network.threshold_change == "random":
            for layer in network.neurons:
                for neuron in layer:
                    neuron.threshold += ((2*(np.random.random(1)[0]))-1)/self.intensity
                    if neuron.threshold > 1: synapse.weight = 1
                    if neuron.threshold < -1: synapse.weight = -1

    def train(self, network, data, repititions):
        best_network = network
        for rep in range(repititions):
            network_list = self.clone_networks(best_network, 5)
            for i in range(1, len(network_list)):
                self.modulate_weights(network_list[i])
            errors = []
            for network in network_list:
                error_data = []
                for datum in data:
                    network.propagate(datum[0])
                    result = [x.value for x in network.neurons[-1]]
                    squared_errors = [(x - y)**2 for x, y in zip(result, datum[1])]
                    root_mean_error = stat.mean(squared_errors)**0.5
                    error_data.append(root_mean_error)
                errors.append(stat.mean(error_data))
            best_network = network_list[errors.index(min(errors))]
            if rep % (repititions/10) == 0:
                print("rep {}".format(rep))
        return best_network

class TrainingData:
    """A class to hold training data"""
    def __init__(self, master_network, data=[]):
        self.master_network = master_network
        self.inputs = len(master_network.neurons[0])
        self.outputs = len(master_network.neurons[-1])
        self.data = data

    def add_data(self, inputs, outputs):
        if len(inputs) != self.inputs:
            raise AttributeError("Wrong number of inputs. Got {}, need {}".format(inputs, self.inputs))
        if len(outputs) != self.outputs:
            raise AttributeError("Wrong number of outputs. Got {}, need {}".format(outputs, self.outputs))
        self.data.append((inputs, outputs))

    def clear(self):
        self.data = []

    def export_data(self):
        return self.data

if __name__ == "__main__":
    #Data to train with, Format ([input], [output])
        #Example here is xor switch
    data = [
        ([0, 0], [0]),
        ([0, 1], [1]),
        ([1, 0], [1]),
        ([1, 1], [0])
        ]

    #Initialise Network
    network = Network([2, 1, 2, 5], threshold=0.5)

    #Build Darwinian Trainer
        #Argument is how much the trainer can eandomly modify the weights each generation: the highers the number, the less is can
        #mess with them.
    ran = RandomTrainer(2)

    #Train Network
    #Argument here is number of repititions
    network = ran.train(network, data, 50)

    #Print network results
    for datum in data:
        network.propagate(datum[0])
        network.print_input_output()

    network.export_graph()
