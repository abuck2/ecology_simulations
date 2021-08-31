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
        portrayal["Layer"] = 1
    elif isinstance(agent, Fox):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    elif isinstance(agent, Plant):
        portrayal["Color"] = "green"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.5 #Add rivers even if debug = False
    else :
        portrayal["r"] = 0
    return portrayal

def agent_portrayal_with_altitude(agent):
    # Potrayal
    portrayal = {"Shape": "circle",
                 "Color": "red",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    if isinstance(agent, Rabbit):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0.7
    elif isinstance(agent, Fox):
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.7
    elif isinstance(agent, Plant):
        portrayal["Color"] = "green"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.7
    elif isinstance(agent, Terrain):
        if agent.altitude > 0:
            portrayal["Shape"] = "rect"
            portrayal["Color"] = altitude_shade(agent.altitude)
            portrayal["Layer"] = 0
            portrayal["h"] = 1
            portrayal["w"] = 1
        else :
            #it's water
            portrayal["Shape"] = "rect"
            portrayal["h"] = 1
            portrayal["w"] = 1
            portrayal["Color"] = "blue"
            portrayal["Layer"] = 0

    return portrayal

def altitude_shade(altitude):
    #Approx returns an HTML code for a shade of grey depending on altitude, I stay in decimal base because I'm lazy
    html_shade = "#"+str(int(100 -(altitude)))*3
    return html_shade





def foraging_visualisation(species_to_display:list = ["rabbits", "foxes"], size:list = [20,20], debug:bool = False):
    
    if len(size) != 2 :
        raise ValueError("Size argument must be a list of two elements [height, width]")

    species_disp = []
    if "rabbits" in species_to_display : 
        species_disp.append({"Label": "Rabbits", "Color": "Red"})
    if "foxes" in species_to_display : 
        species_disp.append({"Label": "Foxes", "Color": "Yellow"})
    if "plants" in species_to_display : 
        species_disp.append({"Label": "Plants", "Color": "Green"})
    if not species_disp:
        raise ValueError("No species selected to display")
    if not debug :
        chart = ChartModule(species_disp,
                        data_collector_name='datacollector')
    else : 
        debug_display = [{"Label":"plants_reprod", "Color" : "Red"}]
        chart = ChartModule(debug_display,
                        data_collector_name='datacollector')

    model_params = {
        "height": size[0],
        "width": size[1],
        "R": 20,
        "P": 20,
        "F": 20,
        "p_reprod_rate": UserSettableParameter("slider", "Plants reproduction rate", 0.05, 0.01, 0.1, 0.01, 1), #Default, min, max, increment
        "r_reprod_rate": UserSettableParameter("slider", "Rabbits reproduction rate", 0.5, 0.3, 0.9, 0.1, 1),
        "f_reprod_rate": UserSettableParameter("slider", "Foxes reproduction rate", 0.3, 0.1, 0.7, 0.1, 1),
        "r_max_health": UserSettableParameter("slider", "Rabbits starving tolerance (steps)", 6, 2, 10, 1, 1),
        "f_max_health": UserSettableParameter("slider", "Foxes starving tolerance (steps)", 10, 5, 20, 1, 1)
    }
    if debug :
        grid = CanvasGrid(agent_portrayal_with_altitude, size[0], size[1], 500, 500)#XcellsNumber, YCellsNumber, XPixels, YPixels
    else : 
        grid = CanvasGrid(agent_portrayal, size[0], size[1], 500, 500)#XcellsNumber, YCellsNumber, XPixels, YPixels

    server = ModularServer(ForagingModel,
                       [grid, chart],
                       "Foraging Model",
                       model_params)
    

    server.port = 8521 # The default
    server.launch()



if __name__=="__main__":
    foraging_visualisation(debug = True)
