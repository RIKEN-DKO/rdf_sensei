# louvain_community_detector.py

import rdflib
import networkx as nx
from rdflib.namespace import RDF, RDFS
from collections import defaultdict
import logging
import community.community_louvain as community_louvain
from path_community_detector import PathCommunityDetector

logging.getLogger('rdflib').setLevel(logging.ERROR)

class LouvainCommunityDetector(PathCommunityDetector):
    def __init__(self, rg, use_labels=True):
        super().__init__(rg, use_labels=use_labels)
        self.communities = self.detect_communities()

    def detect_communities(self):
        G_undirected = self.G.to_undirected()
        partition = community_louvain.best_partition(G_undirected)
        communities = defaultdict(list)
        for node, community_id in partition.items():
            communities[community_id].append(node)
        return communities

    def get_communities(self):
        community_info_list = []
        for community_id, nodes in self.communities.items():
            community_nodes_set = set(nodes)
            subgraph_graph = rdflib.Graph()
            for s, p, o in self.graph.triples((None, None, None)):
                if s in community_nodes_set and o in community_nodes_set:
                    subgraph_graph.add((s, p, o))
            subgraph_turtle = subgraph_graph.serialize(format='turtle')
            community_size = len(nodes)
            community_info = {
                'community_id': community_id,
                'size': community_size,
                'subgraph_turtle': subgraph_turtle
            }
            community_info_list.append(community_info)
        return community_info_list
