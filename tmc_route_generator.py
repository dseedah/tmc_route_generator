'''
@author: Dan Seedah
@credits: Dijkstra's algorithm for shortest paths: David Eppstein, UC Irvine, 4 April 2002,
          http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228
'''
import csv
import json
import time
from math import cos, asin, sqrt
from collections import defaultdict
from priority_dictionary import PriorityDictionary
from operator import itemgetter
from progress_bar import ProgressBar


class Graph():

    def __init__(self, edge_input_file):
        '''
        This will generate a graph similar to the example from
        Cormen, Leiserson, and Rivest (Introduction to Algorithms, 1st edition), page 528:
        G = {'s':{'u':10, 'x':5}, 'u':{'v':1, 'x':2}, 'v':{'y':4}, 'x':{'u':3, 'v':9, 'y':2}, 'y':{'s':7, 'v':6}} </pre>
        The shortest path from s to v is ['s', 'x', 'u', 'v'] and has length 9.
        '''
        self.edges = {}
        self.directionality = {}
        self.edges_temp = defaultdict(list)
        self.convertToGraph(edge_input_file)

    def add_edge(self, from_node, to_node, weight, from_dir, to_dir):
        self.edges_temp[from_node].append({
            to_node: weight
        })
        self.directionality[from_node] = from_dir

    def convertListDict(self):
        for d in self.edges_temp:
            self.edges[d] = {}
            for i in  self.edges_temp[d]:
                self.edges[d].update(i)

    def convertToGraph(self, edge_input_file):
        tmc_list = []

        # Open the file and attached to csv.DictReader
        csvFile = open(edge_input_file, 'r')
        reader = csv.DictReader(csvFile)
        # Skip the first row
        next(reader, None)
        # Iterate through each row in the reader and attach to network
        for row in reader:
            self.add_edge(row["start_node"],row["end_node"],row["distance"],row["from_dir"],row["to_dir"])

        self.convertListDict()
        print("Identified " + str(len(self.edges_temp)) + " Edges")


class NetworkEdgesGenerator():
    '''
    This will generate an output file containing the edges
    and their respective distances.
    '''
    tmc_list = []
    max_tmc_length = 15
    edges = []
    avoid_directions = {
        "N": ["S"], # N to S
        "S": ["N"], # S to N
        "E": ["W"], # E to W
        "W": ["E"]  # W to E
    }

    def __init__(self, tmc_file = 'TMC_Identification.csv',
                 edge_output_file = 'network_edges.csv'):
        self.convertCSVToJSON(tmc_file)
        self.createEdgesThenSaveToFile(edge_output_file)

    def convertCSVToJSON(self, tmc_file):
        # Open the file and attached to csv.DictReader
        csvFile = open(tmc_file, 'r')
        reader = csv.DictReader(csvFile,
                                fieldnames=("tmc", "road", "direction", "intersection", "state", "county",
                                                     "zip", "start_latitude", "start_longitude", "end_latitude",
                                                     "end_longitude", "miles", "road_order", "timezone_name",
                                                     "type", "country", "tmclinear", "frc", "border_set", "f_system", "urban_code",
                                                     "faciltype", "structype", "thrulanes", "route_numb", "route_sign",
                                                     "route_qual", "altrtename", "aadt", "aadt_singl", "aadt_combi", "nhs",
                                                     "nhs_pct", "strhnt_typ", "strhnt_pct", "truck", "isprimary",
                                                     "active_start_date", "active_end_date"))
        # Skip the first row
        next(reader, None)
        # Iterate through each row in the reader and attach to network
        for row in reader:
            new_dict = {
                "tmc": row["tmc"],
                "road": row["road"],
                "direction": row["direction"],
                "intersection": row["intersection"],
                "start_latitude": row["start_latitude"],
                "start_longitude": row["start_longitude"],
                "end_latitude": row["end_latitude"],
                "end_longitude": row["end_longitude"],
                "miles": row["miles"],
            }
            self.tmc_list.append(new_dict)
            if(float(row["miles"]) > self.max_tmc_length):
                max_tmc_length = row["miles"]

        print("Identified " + str(len(self.tmc_list)) + " TMCs")
        # Sort by TMC ID and return
        return sorted(self.tmc_list, key=itemgetter('tmc'), reverse=True)

    def euclidean_distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 12742 * asin(sqrt(a))

    def createEdgesThenSaveToFile(self, edge_output_file):
        i = 0
        num_of_iterations = len(self.tmc_list) * len(self.tmc_list)
        progressbar = ProgressBar(num_of_iterations)
        with open(edge_output_file, mode='w', newline='') as network_edges_file:
            writer = csv.writer(network_edges_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["start_node", "end_node", "distance", "from_dir", "to_dir"])
            for itmc in self.tmc_list:
                for jtmc in self.tmc_list:
                    if (itmc["tmc"] != jtmc["tmc"]):
                        dist = self.euclidean_distance(
                                float(itmc["start_latitude"]), float(itmc["start_longitude"]),
                                float(jtmc["start_latitude"]), float(jtmc["start_longitude"]))

                        if (dist <= self.max_tmc_length and
                            jtmc["direction"][0] not in self.avoid_directions[itmc["direction"][0]]):
                            writer.writerow(
                                [itmc["tmc"], jtmc["tmc"], dist, itmc["direction"][0], jtmc["direction"][0]])
                    i += 1
                    progressbar.print(i)

        print("Successfully created the edges and saved them to the file " + edge_output_file)

class TMCRouteGenerator:
    networkdata = []
    edges = []

    def __init__(self, starting_tmc, ending_tmc,
                 tmc_identification_file = "TMC_Identification.csv",
                 create_network_edges_file = True,
                 edge_output_file = "network_edges.csv"):
        '''
        :param starting_tmc:
        :param ending_tmc:
        :param tmc_identification_file:
        :param create_network_graph:
        :param edge_output_file:
        '''
        self.starting_tmc = starting_tmc
        self.ending_tmc = ending_tmc
        self.tmc_identification_file = tmc_identification_file
        self.edge_input_file = edge_output_file
        if create_network_edges_file :
            graph_file = NetworkEdgesGenerator(tmc_identification_file, edge_output_file)
        self.createNetworkGraph()

    def createNetworkGraph(self):
        graph = self.convertEdgeFileToGraph()
        initialPath = self.shortestPath(graph.edges, self.starting_tmc, self.ending_tmc)
        print(initialPath)

    def convertEdgeFileToGraph(self):
        graph = Graph(self.edge_input_file)
        return graph

    def shortestPath(self, G, start, end):
        D, P = self.Dijkstra(G, start, end)
        Path = []
        while 1:
            Path.append(end)
            if end == start: break
            end = P[end]
        Path.reverse()
        return Path

    def Dijkstra(self, G, start, end=None):
        D = {}  # dictionary of final distances
        P = {}  # dictionary of predecessors
        Q = PriorityDictionary()  # est.dist. of non-final vert.
        Q[start] = 0

        for v in Q:
            D[v] = Q[v]
            if v == end: break

            for w in G:
                try:
                    #if (graph.directions[next_node] in self.nondirectionalities[graph.directions[current_node]]):
                    #    continue
                    vwLength = D[v] + float(G[v][w])
                    if w in D:
                        if vwLength < D[w]:
                            raise (ValueError, "Dijkstra: found better path to already-final vertex")
                    elif w not in Q or vwLength < Q[w]:
                        Q[w] = vwLength
                        P[w] = v
                except KeyError:
                    continue
        return (D, P)

# Initial Run to generate network_edges.csv
RoutePath = TMCRouteGenerator("119+05585","119+05578","TMC_Identification.csv",True)

# For subsequent runs, use this instead.
# RoutePath = TMCRouteGenerator("119+05585","119+05578",None,False)