from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from model import *

#Agents representation
def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Color": "red",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    if isinstance(agent, Rabbit):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    elif isinstance(agent, Fox):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    else :
        portrayal["Color"] = "green"
    return portrayal


chart = ChartModule([{"Label": "Rabbits",
                      "Color": "Red"},
                      {"Label":"Foxes",
                        "Color":"Black"},
                      {"Label":"Plants",
                        "Color":"Green"}],
                    data_collector_name='datacollector')





if __name__=="__main__":
    grid = CanvasGrid(agent_portrayal, 30, 30, 500, 500)#XcellsNumber, YCellsNumber, XPixels, YPixels
    server = ModularServer(ForagingModel,
                       [grid, chart],
                       "Foraging Model",
                       {"R":20, "P":150, "F":2, "width":30, "height":30})
    server.port = 8521 # The default
    server.launch()
