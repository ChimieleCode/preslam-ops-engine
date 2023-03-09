import matplotlib.pyplot as plt

from pathlib import Path
from ..utils import import_from_json


def print_opensees_model(model_path: Path):
    model = import_from_json(model_path)

    geometry = model['StructuralAnalysisModel']['geometry']

    # nodes
    nodes = geometry['nodes']
    nodes_positions = {
        'x': [],
        'y': []
    }
    for node in nodes:
        nodes_positions['x'].append(node['crd'][0])
        nodes_positions['y'].append(node['crd'][1])

    plt.scatter(
        nodes_positions['x'],
        nodes_positions['y'],
        4
    )

    # elements
    elements = geometry['elements']

    for element in elements:
        node_i = element['nodes'][0]
        node_j = element['nodes'][1]
        if element['type'] == 'ElasticBeam2d':
            color = 'r'
        else:
            color = 'g'
        
        plt.plot(
            [
                nodes_positions['x'][node_i],
                nodes_positions['x'][node_j]
            ],
            [
                nodes_positions['y'][node_i],
                nodes_positions['y'][node_j]
            ],
            color=color
        )

    plt.show()
