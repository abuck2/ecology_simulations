from mesa import Agent, Model
#Space grid
from mesa.space import MultiGrid
#Scheduler
from mesa.time import RandomActivation
#Data collection
from mesa.datacollection import DataCollector
#batches of multiple models -> run the model multiple time
from mesa.batchrunner import BatchRunner

import random
import matplotlib.pyplot as plt
import numpy as np
import logging
from scipy.ndimage import gaussian_filter #to smoothe the map

from agents import Rabbit, Plant, Fox, Terrain

#function to compute values for the datacollector

def compute_population_r(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Rabbit)])

def compute_population_p(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Plant)])

def compute_population_f(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Fox)])

def compute_population_t(model):
    #Should be fixed
    return len([agent for agent in model.schedule.agents if isinstance(agent, Terrain)])

def average_rabbit_health(model):
    rabbits = [agent for agent in model.schedule.agents if isinstance(agent, Rabbit)]
    agent_health = [agent.health for agent in rabbits]
    return sum(agent_health) / len(agent_health)


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)    


class ForagingModel(Model):
    def __init__(self, R, P, F, width, height, 
            p_reprod_rate:float = 0.05, r_reprod_rate:float = 0.5, f_reprod_rate:float = 0.3,
            r_max_health:int = 4, f_max_health:int = 10):
        
        #Number of rabbits and plants
        self.num_agents = R
        self.num_plants = P
        self.num_foxes = F
        
        
        #set as model attributes for vizualisation purposes
        self.p_reprod_rate = p_reprod_rate
        self.r_reprod_rate = r_reprod_rate
        self.f_reprod_rate = f_reprod_rate
        self.r_max_health = r_max_health
        self.f_max_health = f_max_health
        #Create space
        self.grid = MultiGrid(width, height, True)
        
        #Activation of the agents every step is random
        self.schedule = RandomActivation(self)

        #running variable for the batch runner. Simulation stops if a certain condition is met
        #If set to True, obviously never stops
        self.running = True

        #Initialize loggers 
        setup_logger('rabbits_logger', "logs/rabbits_agents.log")
        setup_logger('plants_logger', "logs/plants_agents.log")
        setup_logger('fox_logger', "logs/fox_agents.log")
        setup_logger('model_logger', "logs/model.log")
        rabbits_logger = logging.getLogger('rabbits_logger')
        plants_logger = logging.getLogger('plants_logger')
        fox_logger = logging.getLogger('fox_logger')
        model_logger = logging.getLogger('model_logger')

        # Create Rabbits
        for i in range(self.num_agents):
            sex = bool(random.getrandbits(1))
            a = Rabbit(i, self, sex, rabbits_logger, reprod_rate = self.r_reprod_rate, max_health = r_max_health)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        
        # Create Plants
        for i in range(self.num_plants):
            a = Plant(i+self.num_agents, self, plants_logger, reprod_rate = self.p_reprod_rate)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        
        # Create Foxes
        for i in range(self.num_foxes):
            current_id = self.num_agents+self.num_plants+i
            sex = bool(random.getrandbits(1))
            a = Fox(current_id, self, sex, fox_logger, reprod_rate = self.f_reprod_rate, max_health = f_max_health)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
       
        #Generate a map
        self.generate_map(width, height, current_id+1)
        
        #Initialize the data collector when model is initialized
        #self.datacollector = DataCollector(
        #        model_reporters={"Gini": compute_gini, "health":average_rabbit_health},  # the functions are defined above with computaion for the colleor
        #        agent_reporters={"Carrot": "carrot"}) #agent-level data
        self.datacollector = DataCollector(
                model_reporters={
                    "Rabbits":compute_population_r, 
                    "Plants":compute_population_p,
                    "Foxes":compute_population_f,
                    "plants_reprod": lambda model : model.p_reprod_rate,
                    "foxes_reprod": lambda model : model.f_reprod_rate,
                    "rabbits_reprod": lambda model : model.r_reprod_rate
                    }) #agent-level data

    def step(self):
        #collect data
        self.datacollector.collect(self)
        #advance simulation one step
        self.schedule.step()

    def get_next_id(self):
        next_one = max([agent.unique_id for agent in self.schedule.agents])+1
        all_ids = [agent.unique_id for agent in self.schedule.agents]
        return next_one, all_ids

    def generate_map(self, width, height, current_id):
        #Altitude needs to be kinda smooth, not just completely random - Maybe use a convolutional matrix
        #implement movement dependant on altitude for rabbits and foxes (and plants for rivers)
        #show in nicely in viz - In shades of grey + rivers, fill the whole cell
        # plant : don't germinate in water
        map_size = width*height
        list_altitudes = random.choices(list(range(-30, 100)), k=map_size)
        array_altitude = np.array(list_altitudes).reshape(width, height)
        array_altitude = gaussian_filter(array_altitude, sigma=0.8, truncate = 1.5)

        for x in range(0, width):
            for y in range(0, height):
                local_altitude = array_altitude[x, y]
                a = Terrain(self, local_altitude, current_id+(width*y)+x)
                self.grid.place_agent(a, (x, y))
                #Probably useless?
                self.schedule.add(a)
        
