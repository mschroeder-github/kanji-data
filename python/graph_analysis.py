import json

import networkx as nx
from networkx import DiGraph
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


def radical_graph():
    g = DiGraph()

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    for entry in kanji_kyouiku:
        #if entry['grade'] > 1:
        #    break

        g.add_node(entry['kanji'], meaning=entry['meanings_de'][0])

        for rad_meaning, rad_kanji in zip(entry['wk_radicals_de'], entry['wk_radicals_kanji']):

            if rad_kanji.strip() == '':
                rad_kanji = rad_meaning

            g.add_node(rad_kanji, meaning=rad_meaning)
            g.add_edge(rad_kanji, entry['kanji'])

    print(g.number_of_edges(), 'edges')
    print(g.number_of_nodes(), 'nodes')

    no_incoming = [(node, data) for node, data in g.nodes(data=True) if g.in_degree(node) == 0]

    # 133  no incoming nodes
    print(len(no_incoming), ' no incoming nodes')

    for node in no_incoming:
        print(node)

    #for edge in g.edges:
    #    print(edge)

    # Create hierarchical layout
    pos = graphviz_layout(g, prog="dot")

    plt.figure(figsize=(8, 6))
    # Draw the graph
    nx.draw(g, pos, with_labels=True, arrows=True, node_size=2000, node_color="lightblue", font_size=10, font_family="sans-serif")

    # Save the graph as SVG
    plt.savefig("../radical.svg", format="svg")

    nx.write_graphml(g, "../radical.graphml", encoding="utf-8")
