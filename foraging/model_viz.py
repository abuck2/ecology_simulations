from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter                                               
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

"""
chart = ChartModule([{"Label": "Rabbits",
                      "Color": "Red"},
                      {"Label":"Foxes",
                        "Color":"Black"},
                      {"Label":"Plants",
                        "Color":"Green"}],
                    data_collector_name='datacollector')
"""

chart = ChartModule([{"Label": "Rabbits",
                      "Color": "Red"},
                      {"Label":"Foxes",
                        "Color":"Black"}],
                    data_collector_name='datacollector')

model_params = {
    "height": 20,
    "width": 20,
    "R": 20,
    "P": 20,
    "F": 20,
    "p_reprod_rate": UserSettableParameter("slider", "Plants reproduction rate", 0.05, 0.01, 0.1, 0.01, 1),
    "r_reprod_rate": UserSettableParameter("slider", "Rabbits reproduction rate", 0.5, 0.3, 0.9, 0.1, 1),
    "f_reprod_rate": UserSettableParameter("slider", "Foxes reproduction rate", 0.3, 0.1, 0.7, 0.1, 1)
}



if __name__=="__main__":
    grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)#XcellsNumber, YCellsNumber, XPixels, YPixels
    server = ModularServer(ForagingModel,
                       [grid, chart],
                       "Foraging Model",
                       model_params)
    

    server.port = 8521 # The default
    server.launch()
