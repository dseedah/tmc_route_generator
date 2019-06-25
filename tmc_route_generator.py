'''
@author: Dan Seedah
@credits: Dijkstra's algorithm for shortest paths: David Eppstein, UC Irvine, 4 April 2002,
          http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228

'''
import csv
from math import cos, asin, sqrt
from collections import defaultdict
from dijkstra import shortestPath
from progress_bar import ProgressBar

class Graph():
    '''
    This will generate a graph similar to the example from
    Cormen, Leiserson, and Rivest (Introduction to Algorithms, 1st edition), page 528:
    G = {'s':{'u':10, 'x':5}, 'u':{'v':1, 'x':2}, 'v':{'y':4}, 'x':{'u':3, 'v':9, 'y':2}, 'y':{'s':7, 'v':6}} </pre>
    The shortest path from s to v is ['s', 'x', 'u', 'v'] and has length 9.
    '''
    edges = {}
    edges_temp = defaultdict(list)

    def __init__(self, edge_input_file):
        self.convertInputFileToList(edge_input_file)
        self.convertListToGraph()
        print("Identified ", len(self.edges), " nodes and their respective connectors")

    def convertInputFileToList(self, edge_input_file):
        csvFile = open(edge_input_file, 'r')
        reader = csv.DictReader(csvFile)
        next(reader, None)
        for row in reader:
            self.add_edge(row["start_node"],row["end_node"],row["distance"])

    def add_edge(self, from_node, to_node, distance):
        self.edges_temp[from_node].append({to_node: distance})

    def convertListToGraph(self):
        for d in self.edges_temp:
            self.edges[d] = {}
            for i in  self.edges_temp[d]:
                self.edges[d].update(i)


class ConvertTMCDataToDict():
    '''
    Converts a TMC_Identification.csv file to a Dictionary object
    '''
    tmc_ref_data = {}

    def __init__(self, tmc_file='TMC_Identification.csv', skip_header=True):
        csvFile = open(tmc_file, 'r')
        reader = csv.DictReader(csvFile, fieldnames=("tmc", "road", "direction", "intersection", "state", "county",
                                                    "zip", "start_latitude", "start_longitude", "end_latitude",
                                                    "end_longitude", "miles", "road_order", "timezone_name",
                                                    "type", "country", "tmclinear", "frc", "border_set", "f_system",
                                                    "urban_code","faciltype", "structype", "thrulanes", "route_numb",
                                                    "route_sign","route_qual", "altrtename", "aadt", "aadt_singl",
                                                    "aadt_combi", "nhs", "nhs_pct", "strhnt_typ", "strhnt_pct",
                                                    "truck", "isprimary", "active_start_date", "active_end_date"))
        if skip_header: next(reader, None)

        self.tmc_ref_data = {}
        for row in reader:
            self.tmc_ref_data[row["tmc"]] = {
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
        print("Identified ",len(self.tmc_ref_data.keys())," TMCs")

    def getTMCRefData(self):
        return self.tmc_ref_data


class NetworkEdgesGenerator():
    '''
    This will generate an output file containing the edges
    and their respective distances.
    '''
    tmc_ref_data = {}
    max_tmc_separation = 50
    edges = []
    avoid_directions = {
        "N": ["S"], # N to S
        "S": ["N"], # S to N
        "E": ["W"], # E to W
        "W": ["E"]  # W to E
    }
    tmc_file = ""
    edge_output_file = ""

    def __init__(self, tmc_file = 'TMC_Identification.csv',
                 edge_output_file = 'network_edges.csv', max_tmc_separation = 50):
        self.tmc_file = tmc_file
        self.edge_output_file = edge_output_file
        self.max_tmc_separation = max_tmc_separation
        tmc_converter = ConvertTMCDataToDict(tmc_file)
        self.tmc_ref_data = tmc_converter.getTMCRefData()

    def getTMCRefData(self):
        return self.tmc_ref_data

    def euclidean_distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 12742 * asin(sqrt(a))

    def createEdgesThenSaveToFile(self):
        counter = 0
        num_of_iterations = len(self.tmc_ref_data.keys())**2
        progressbar = ProgressBar(num_of_iterations)
        with open(self.edge_output_file, mode='w', newline='') as network_edges_file:
            writer = csv.writer(network_edges_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["start_node", "end_node", "distance", "from_dir", "to_dir"])
            tmc_list = self.tmc_ref_data.items()
            for i, itmc in tmc_list:
                for j, jtmc in tmc_list:
                    if (itmc["tmc"] != jtmc["tmc"]):
                        dist = self.euclidean_distance(
                                float(itmc["start_latitude"]), float(itmc["start_longitude"]),
                                float(jtmc["start_latitude"]), float(jtmc["start_longitude"]))
                        if (dist <= self.max_tmc_separation and
                            jtmc["direction"][0] not in self.avoid_directions[itmc["direction"][0]]):
                            writer.writerow(
                                [itmc["tmc"], jtmc["tmc"], dist, itmc["direction"][0], jtmc["direction"][0]])
                    counter += 1
                    progressbar.print(counter)

        print("Successfully created the edges and saved them to the file " + self.edge_output_file)
        return self.edge_output_file

class TMCRouteGenerator:
    networkdata = []
    edges = []
    graph = {}
    shortest_path = []
    complete_path = []
    tmc_ref_data = {}

    def start(self,
                 starting_tmc,
                 ending_tmc,
                 tmc_identification_file = "TMC_Identification.csv",
                 create_network_edges_file = True,
                 edge_output_file = "network_edges.csv"):

        self.starting_tmc = starting_tmc
        self.ending_tmc = ending_tmc
        self.tmc_identification_file = tmc_identification_file
        self.edge_input_file = edge_output_file
        netGen = NetworkEdgesGenerator(tmc_identification_file, edge_output_file)
        if create_network_edges_file :
            netGen.createEdgesThenSaveToFile()
        self.tmc_ref_data = netGen.getTMCRefData()
        self.graph = Graph(self.edge_input_file)
        self.shortest_path = shortestPath(self.graph.edges, self.starting_tmc, self.ending_tmc)
        self.completePath()

    def completePath(self):
        for tmc in self.shortest_path:
            if tmc not in self.complete_path : self.complete_path.append(tmc)
            if tmc ==  self.ending_tmc : break;
            self.findNextTMCOnPath(tmc)

    def findNextTMCOnPath(self, tmc):
        tmc_end_lat = self.tmc_ref_data[tmc]["end_latitude"]
        tmc_edges = sorted(self.graph.edges[tmc].items(), key=lambda kv: float(kv[1]))
        for node in tmc_edges:
            node_start_lat = self.tmc_ref_data[node[0]]["start_latitude"]
            if(float(tmc_end_lat) ==  float(node_start_lat))\
                    and node[0] not in self.complete_path:
                self.complete_path.append(node[0])
                self.findNextTMCOnPath(node[0])

    def getShortestPath(self):
        print("Shortest Path has", len(self.shortest_path), "TMCs: ", self.shortest_path)
        return self.shortest_path

    def getCompletePath(self):
        print("Complete Path has", len(self.complete_path), "TMCs: ", self.complete_path)
        return self.complete_path


if __name__ == '__main__':
    TMCRouter = TMCRouteGenerator()
    # Initial Run to generate network_edges.csv
    #TMCRouter.start("119+05606","119+05044","TMC_Identification.csv",True)
    # For subsequent runs, use this instead.
    TMCRouter.start("119+05606","119+05044","TMC_Identification.csv",False)
    print(TMCRouter.getShortestPath())
    print(TMCRouter.getCompletePath())