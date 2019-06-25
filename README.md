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
`TMCRouter = TMCRouteGenerator()`

To define your start and ending TMCs and generate network_edges.csv
`TMCRouter.start("119+05606","119+05044","TMC_Identification.csv",True)`

For subsequent runs where `network_edges.csv` file has already been generated from your TMC_Identification.csv file,
then use this instead:

`TMCRouter.start("119+05606","119+05044","TMC_Identification.csv",False)`

To get list of TMCs, run either of the following:
```
print(TMCRouter.getShortestPath())
print(TMCRouter.getCompletePath())
```

Final output is a list of TMCs as in the example below:
`['119+05585', '119P05586', '119+05588', ...]`

![Screenshot](https://github.com/dseedah/tmc_route_generator/blob/master/screenshot.png)
