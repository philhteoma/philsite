#!/usr/bin/env python3

"""
Created by @author: craffel
Modified on Sun Jan 15, 2017 by anbrjohn

Modifications:
    -Changed xrange to range for python 3
    -Added functionality to annotate nodes
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# def draw_neural_net(ax, left, right, bottom, top, layer_sizes, layer_text=None):
def draw_neural_net(ax, network, print_values=True):
    '''
    Draw a neural network cartoon using matplotilb.

    :usage:
        >>> fig = plt.figure(figsize=(12, 12))
        >>> draw_neural_net(fig.gca(), .1, .9, .1, .9, [4, 7, 2], ['x1', 'x2','x3','x4'])

    :parameters:
        - ax : matplotlib.axes.AxesSubplot
            The axes on which to plot the cartoon (get e.g. by plt.gca())
        - left : float
            The center of the leftmost node(s) will be placed here
        - right : float
            The center of the rightmost node(s) will be placed here
        - bottom : float
            The center of the bottommost node(s) will be placed here
        - top : float
            The center of the topmost node(s) will be placed here
        - layer_sizes : list of int
            List of layer sizes, including input and output dimensionality
        - layer_text : list of str
            List of node annotations in top-down left-right order
    '''
    top = .1
    bottom = .9
    left = .1
    right = .9

    layer_sizes = [len(x) for x in network.neurons]
    layer_text = [x.value for x in [x for y in network.neurons for x in y]]

    n_layers = len(layer_sizes)
    v_spacing = ((top - bottom)/float(max(layer_sizes)))
    h_spacing = ((right - left)/float(len(layer_sizes) - 1))
    ax.axis('off')
    # Nodes
    mpl.rcParams.update({"font.size": 12})
    for n, layer_size in enumerate(layer_sizes):
        layer_top = v_spacing*(layer_size - 1)/2. + (top + bottom)/2.
        for m in range(layer_size):
            x = n*h_spacing + left
            y = layer_top - m*v_spacing
            circle = plt.Circle((x,y), v_spacing/4.,
                                color='w', ec='k', zorder=4)
            ax.add_artist(circle)
            # Node annotations
            if print_values:
                text = layer_text.pop(0)
                plt.annotate(text, xy=(x, y), zorder=5, ha='center', va='center')


    # Edges
    mpl.rcParams.update({"font.size": 8})
    for n, (layer_size_a, layer_size_b) in enumerate(zip(layer_sizes[:-1], layer_sizes[1:])):
        layer_top_a = v_spacing*(layer_size_a - 1)/2. + (top + bottom)/2.
        layer_top_b = v_spacing*(layer_size_b - 1)/2. + (top + bottom)/2
        increase = False #Toggling bool to help space annotations
        for m in range(layer_size_a):
            increase = not increase
            offset = 1 if increase else 1
            for o in range(layer_size_b):
                weight = round(network.neurons[n][m].output_synapses[o].weight, 2) #Find synapse weight
                x = [n*h_spacing + left, (n + 1)*h_spacing + left]  #Line coords
                y= [layer_top_a - m*v_spacing, layer_top_b - o*v_spacing]
                length = np.sqrt(((x[1]-x[0])**2)+((y[1]-y[0])**2))
                offset = length*0.95
                word_location = [((x[1]-x[0])*offset)+x[0], (((y[1]-y[0])*offset)+y[0])] #Weight Coords
                word_location[1] += (y[1]-y[0])*0.045 #Offset y so that weight appears at consistent location
                gradient = (y[1]-y[0])/(x[1]-x[0])
                angle = np.rad2deg(np.arctan(gradient)) #Angle to display weight at
                angle *= 0.8 #Correct angle #justpyplotthings
                line = plt.Line2D(x, y, c='gray')
                ax.add_artist(line)
                ax.annotate(weight, xy=word_location, rotation=angle, xytext=(0,0), textcoords="offset points", horizontalalignment="left", verticalalignment="bottom")
