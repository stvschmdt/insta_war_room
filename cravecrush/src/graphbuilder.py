import csv
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from nltk import word_tokenize

import logger
import instaparse
import formatter
import collections

class Node(object):

    def __init__(self, tag):
        self.tag = tag



class Edge(object):

    def __init__(self, n1, n2):
        self.left = n1
        self.right = n2


class GraphBuilder(object):

    def __init__(self, items=None):
        self.log = logger.Logging()
        self.G = nx.Graph()

    def create_nodes(self, l_items):
        l_nodes = []
        for n in l_items:
            l_nodes.append(Node(n))
        return l_nodes

    #this should take in nodes list and post dict of commens
    def edges_from_text(self, hashtags_dict, valid_list, home=''):
        for idx, tags in hashtags_dict.items():
            #tokenize the comment
            #get all permutations of edges - not to oneself tho
            edges = [(i,j) for i in tags for j in tags if i != j and i in valid_list and j in valid_list]
            #loop through each pair and add or update edge weight
            for e in edges:
                if self.G.has_edge(e[0], e[1]):
                    self.G[e[0]][e[1]]['weight'] += 1
                else:
                    self.G.add_edge(e[0], e[1], weight=1)
                    if self.G.node[e[0]].get('cluster',None) == None:
                        self.G.node[e[0]].update({'cluster' : home})
                        #print 'adding node', e[0], home
                    if self.G.node[e[1]].get('cluster',None) == None:
                        self.G.node[e[1]].update({'cluster' : home})
                        #print 'adding node', e[1], home
        self.log.info('graph contains %s nodes and %s edges'%(len(self.G.nodes()), len(self.G.edges())))


    def node_report(self, G):
        data = G.nodes()
        num_neighbors = collections.defaultdict(int)
        for node in data:
            num_neighbors[node] = len(list(G.neighbors(node)))
        return collections.OrderedDict(sorted(num_neighbors.items(), key=lambda val:val[1], reverse=True))

    def build_nodes(self, nodes):
        self.G.add_nodes_from(nodes)
        return 0
    
if __name__ == '__main__':
    bldr = GraphBuilder()
