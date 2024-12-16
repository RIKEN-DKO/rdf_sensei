import rdflib
import networkx as nx
from rdflib.namespace import RDF, RDFS
from collections import defaultdict, Counter
from rdflib import Graph, Namespace, URIRef
import matplotlib.pyplot as plt
import logging
logging.getLogger('rdflib').setLevel(logging.ERROR)  # Suppress the warnings from rdflib

class PathCommunityDetector:
    def __init__(self, rg, use_labels=True, 
                 filter_schema=True,
                 use_class_paths = True,
                 
                 ):
        self.rg = rg
        self.use_labels = use_labels
        self.filter_rdfs = filter_schema
        self.id_to_label = {}
        self.graph_info = self.get_graph_information()
        self.G = self.graph_info['graph']
        self.classes = self.graph_info['classes']
        self.nodes_to_classes = self.graph_info['nodes_to_classes']
        self.schema_keywords = ['rdfs','subclassof']#['rdfs', 'schema']
        self.use_class_paths = use_class_paths
        
    def get_graph_information(self):
        # Build networkx graph with edge labels as predicates
        G = nx.MultiDiGraph()
        for s, p, o in self.rg:
            # Exclude rdf:type edges
            if p != RDF.type:
                G.add_edge(s, o, key=p, label=p)
        # Get all classes and mapping from nodes to classes
        classes = set()
        nodes_to_classes = defaultdict(set)
        for s, p, o in self.rg.triples((None, RDF.type, None)):
            classes.add(o)
            nodes_to_classes[s].add(o)
        return {
            'graph': G,
            'classes': classes,
            'nodes_to_classes': nodes_to_classes
        }

    def get_seed_nodes(self, cls):
        return [node for node in self.G.nodes() if cls in self.nodes_to_classes.get(node, set())]

    def map_instance_path_to_class_path(self, path):
        class_path = []
        for s, p, o in path:
            s_classes = self.nodes_to_classes.get(URIRef(s), {'Unknown'})
            o_classes = self.nodes_to_classes.get(URIRef(o), {'Unknown'})
            s_class = next(iter(s_classes), 'Unknown')
            o_class = next(iter(o_classes), 'Unknown')
            class_path.append((str(s_class), str(p), str(o_class)))
        return tuple(class_path)

    def collect_paths(self, seed_node, k):
        # Collect all paths from seed_node up to length k
        paths = []
        queue = [(seed_node, [])]
        while queue:
            current_node, path = queue.pop(0)
            if len(path) >= k:
                continue
            for neighbor in self.G.neighbors(current_node):
                for key, attr in self.G[current_node][neighbor].items():
                    edge_label = attr['label']
                    # Filter out paths that contain RDFS predicates if filter_rdfs is True
                    # Make it filter out paths that contain any of the specified strings in edge_label
                    # Check if any part of the path contains a filtered keyword
                    if self.filter_rdfs:
                        # Check if the current node, edge, or neighbor contains any filtered keyword
                        # if any(substring in str(current_node).lower() for substring in self.schema_keywords) or \
                        # any(substring in str(edge_label).lower() for substring in self.schema_keywords) or \
                        # any(substring in str(neighbor).lower() for substring in self.schema_keywords):
                        if any(substring in str(edge_label).lower() for substring in self.schema_keywords):
                            continue
                        
                    new_path = path + [(current_node, edge_label, neighbor)]
                    paths.append(new_path)
                    queue.append((neighbor, new_path))
                    
            # print('Collecting paths:', len(paths))
        return paths

    def get_label(self, uri):
        """Attempt to get the label of a URI from the RDF graph."""
        if uri in self.id_to_label:
            return self.id_to_label[uri]
        label = None
        if isinstance(uri, URIRef):
            # Try to get rdfs:label
            for _, _, lbl in self.rg.triples((uri, RDFS.label, None)):
                label = str(lbl)
                break
            if not label:
                # Try to get skos:prefLabel
                for _, _, lbl in self.rg.triples((uri, rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'), None)):
                    label = str(lbl)
                    break
            if not label:
                # Fallback to the last part of the URI
                label = uri.split('/')[-1]
        else:
            label = str(uri)
        # Store the label in the mapping
        self.id_to_label[uri] = label
        return label

    def get_label_triplet(self, uri):
        """Attempt to get the label of a URI from the RDF graph and return the label triple."""
        if uri in self.id_to_label:
            # Return cached label and triple (if we have both stored)
            return self.id_to_label[uri]
        
        label = None
        label_triple = None
        
        if isinstance(uri, URIRef):
            # Try to get rdfs:label
            for _, _, lbl in self.rg.triples((uri, RDFS.label, None)):
                label = str(lbl)
                label_triple = (uri, RDFS.label, lbl)
                break
            if not label:
                # Try to get skos:prefLabel
                for _, _, lbl in self.rg.triples((uri, rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'), None)):
                    label = str(lbl)
                    label_triple = (uri, rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'), lbl)
                    break
            if not label:
                # Fallback to the last part of the URI as a label
                label = uri.split('/')[-1]
        else:
            label = str(uri)
        
        # Cache the label and its triple
        self.id_to_label[uri] = (label, label_triple)
        
        return (label, label_triple)

    def format_instance_path_turtle(self, instance_path):
        formatted_path = []
        label_triples = set()  # To collect and output unique label triples
        
        for (s, p, o) in instance_path:
            # Get labels for subject, predicate, and object if available
            s_label, s_label_triple = self.get_label_triplet(s) if self.use_labels else (None, None)
            p_label, p_label_triple = self.get_label_triplet(p) if self.use_labels else (None, None)
            o_label, o_label_triple = self.get_label_triplet(o) if self.use_labels else (None, None)
            
            # Format the subject, predicate, and object in Turtle format
            s_uri = f"<{s}>" if isinstance(s, URIRef) else f'"{s}"'
            p_uri = f"<{p}>" if isinstance(p, URIRef) else f'"{p}"'
            o_uri = f"<{o}>" if isinstance(o, URIRef) else f'"{o}"'
            
            # Add the main triple to the formatted path
            triple = f"{s_uri} {p_uri} {o_uri} ."
            formatted_path.append(triple)
            
            # Collect label triples if they exist
            if s_label_triple:
                label_triples.add(s_label_triple)
            if p_label_triple:
                label_triples.add(p_label_triple)
            if o_label_triple:
                label_triples.add(o_label_triple)
        
        # Format the collected label triples in Turtle format
        label_triples_turtle = []
        for (subj, pred, obj) in label_triples:
            label_triples_turtle.append(f"<{subj}> <{pred}> \"{obj}\" .")
        
        # Combine the main path triples and the label triples
        return "\n".join(formatted_path) + '\n #LABELS:\n' + "\n".join(label_triples_turtle)

    def format_instance_path(self, instance_path):
        formatted_path = []
        for idx, (s, p, o) in enumerate(instance_path):
            s_label = self.get_label(s) if self.use_labels else str(s)
            p_label = self.get_label(p) if self.use_labels else str(p)
            o_label = self.get_label(o) if self.use_labels else str(o)
            if idx == 0:
                formatted_path.append(f"({s_label}) -[{p_label}]-> ({o_label})")
            else:
                formatted_path.append(f"-({p_label})-> ({o_label})")
        return " ".join(formatted_path)

    def format_class_path(self, class_path):
        formatted_path = []
        for idx, (s_class, p, o_class) in enumerate(class_path):
            s_label = s_class.split('/')[-1]
            o_label = o_class.split('/')[-1]
            p_label = p.split('/')[-1]
            if idx == 0:
                formatted_path.append(f"{s_label} -[{p_label}]-> {o_label}")
            else:
                formatted_path.append(f"-[{p_label}]-> {o_label}")
        return " ".join(formatted_path)

    def find_most_common_paths(self, k=2, top_n=5, sample_size=3):
        """
        Finds the most common paths in the graph for each class and returns the top N paths.

        Parameters:
        k (int): The maximum length of paths to be collected from each seed node. Default is 2.
        top_n (int): The number of top paths to return based on frequency. Default is 5.
        sample_size (int): The number of sample instance paths to store for each unique path. Default is 3.

        Returns:
        dict: A dictionary containing:
            - 'paths': A list of tuples where each tuple contains a path and its associated information (frequency and samples).
            - 'top_paths': A list of the top N paths based on frequency.
            - 'id_to_label': A mapping from ids to labels.
        """
        path_info = dict()
        for cls in self.classes:
            seed_nodes = self.get_seed_nodes(cls)
            for seed_node in seed_nodes:
                paths = self.collect_paths(seed_node, k)
                for path in paths:
                    path_ = tuple(path)
                    if self.use_class_paths:
                        path_ = self.map_instance_path_to_class_path(path)
                    # Initialize entry in path_info if not present
                    if path_ not in path_info:
                        path_info[path_] = {'frequency': 0, 'samples': []}
                    # Increment frequency
                    path_info[path_]['frequency'] += 1
                    # Store up to sample_size instance paths
                    if len(path_info[path_]['samples']) < sample_size:
                        instance_path_formatted = self.format_instance_path_turtle(path)
                        path_info[path_]['samples'].append(instance_path_formatted)
        # Now, sort the paths based on frequency
        sorted_paths = sorted(path_info.items(), key=lambda item: item[1]['frequency'], reverse=True)
        # Get the top N paths
        top_paths = sorted_paths[:top_n]
        # Prepare the output
        output = {
            'paths': sorted_paths,
            'top_paths': top_paths,
            'id_to_label': self.id_to_label  # Include the mapping from ids to labels
        }
        return output


