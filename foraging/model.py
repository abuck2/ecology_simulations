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

from agents import Rabbit, Plant, Fox

#function to compute values for the datacollector

def compute_population_r(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Rabbit)])

def compute_population_p(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Plant)])

def compute_population_f(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Fox)])

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
            p_reprod_rate:float=0.05, r_reprod_rate:float=0.5, f_reprod_rate:float=0.3):
        
        #Number of rabbits and plants
        self.num_agents = R
        self.num_plants = P
        self.num_foxes = F

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
            a = Rabbit(i, self, sex, rabbits_logger, r_reprod_rate)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        
        # Create Plants
        for i in range(self.num_plants):
            a = Plant(i+self.num_agents, self, plants_logger, reprod_rate = p_reprod_rate)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        
        # Create Foxes
        for i in range(self.num_foxes):
            current_id = self.num_agents+self.num_plants+i
            sex = bool(random.getrandbits(1))
            a = Fox(current_id, self, sex, fox_logger, f_reprod_rate)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        
        
        #Initialize the data collector when model is initialized
        #self.datacollector = DataCollector(
        #        model_reporters={"Gini": compute_gini, "health":average_rabbit_health},  # the functions are defined above with computaion for the colleor
        #        agent_reporters={"Carrot": "carrot"}) #agent-level data
        self.datacollector = DataCollector(
                model_reporters={
                    "Rabbits": compute_population_r, 
                    "Plants":compute_population_p,
                    "Foxes":compute_population_f}) #agent-level data

    def step(self):
        #collect data
        self.datacollector.collect(self)
        #advance simulation one step
        self.schedule.step()

    def get_next_id(self):
        next_one = max([agent.unique_id for agent in self.schedule.agents])+1
        all_ids = [agent.unique_id for agent in self.schedule.agents]
        return next_one, all_ids

