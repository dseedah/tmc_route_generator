# TMC Route Generator
A method for generating an optimal route given multi-directional GIS point data, for example, from the NPMRDS TMC Identification File.

TMCs are multi-directional roadway segments defined by INRIX and used in databases such as NPMRDS. 
Currently, the data is published such that the routes are in no particular order (e.g. using TMC Ids).
This algorithm 'walks' the desired path based on your specified Origin/Destination TMCs, 
and prints out all TMCs on that path.


## Prerequisites
1. Python 3
2. TMC_Identification.csv (this is obtained from the NPMRDS website or INRIX) 

## Getting Started
Edit tmc_route_generator.py and define your start and ending TMCs.

`RoutePath = TMCRouteGenerator("119+05585","119+05578","TMC_Identification.csv",True)`

If a network_edges.csv file has already been generated from your TMC_Identification.csv file,
then use this instead:

`RoutePath = TMCRouteGenerator("119+05585","119+05578",None,False)`

Final output is a list of TMCs as in the example below:
`['119+05585', '119P05586', '119+05588', ...]`

![Screenshot](https://github.com/dseedah/tmc_route_generator/blob/master/screenshot.png)
