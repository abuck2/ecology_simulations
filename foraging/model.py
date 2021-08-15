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

from agents import Rabbit, Plant

"""
To add : 
    - Kill the rabbits when they can't eat?
    - Add carrot ressources on the map?
    - Add different kind of agent?
"""

#function to compute values for the datacollector
def compute_gini(model):
    rabbits = [agent for agent in model.schedule.agents if isinstance(agent, Rabbit)]
    agent_carrots = [agent.carrot for agent in rabbits]
    x = sorted(agent_carrots)
    N = model.num_agents
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)

def compute_population_r(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Rabbit)])

def compute_population_p(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Plant)])

def average_rabbit_health(model):
    rabbits = [agent for agent in model.schedule.agents if isinstance(agent, Rabbit)]
    agent_health = [agent.health for agent in rabbits]
    return sum(agent_health) / len(agent_health)


class ForagingModel(Model):
    def __init__(self, R, P, width, height):
        
        #Number of rabbits and plants
        self.num_agents = R
        self.num_plants = P
        
        #Create space
        self.grid = MultiGrid(width, height, True)
        
        #Activation of the agents every step is random
        self.schedule = RandomActivation(self)

        #running variable for the batch runner. Simulation stops if a certain condition is met
        #If set to True, obviously never stops
        self.running = True

        # Create Rabbits
        for i in range(self.num_agents):
            sex = bool(random.getrandbits(1))
            a = Rabbit(i, self, sex)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        
        # Create Plants
        for i in range(self.num_plants):
            a = Plant(i+self.num_agents, self)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            self.current_id = i+1
        
        #Initialize the data collector when model is initialized
        #self.datacollector = DataCollector(
        #        model_reporters={"Gini": compute_gini, "health":average_rabbit_health},  # the functions are defined above with computaion for the colleor
        #        agent_reporters={"Carrot": "carrot"}) #agent-level data
        self.datacollector = DataCollector(
                model_reporters={
                    "Rabbits": compute_population_r, 
                    "Plants":compute_population_p}) #agent-level data

    def step(self):
        #collect data
        self.datacollector.collect(self)
        #advance simulation one step
        self.schedule.step()

    def get_next_id(self):
        next_one = max([agent.unique_id for agent in self.schedule.agents])+1
        all_ids = [agent.unique_id for agent in self.schedule.agents]
        return next_one, all_ids

if __name__=="__main__":
    #######
    #Run a batch of models
    #######
    #Parameters settings
    #Fixed grid size
    fixed_params = {
        "width": 10,
        "height": 10,
        "P" : 15
        }
    #Variable number of rabbits
    variable_params = {"R": range(10, 30, 5)}

    #Batch running instanciation
    batch_run = BatchRunner(
            ForagingModel,
            variable_params,
            fixed_params,
            iterations=3,
            max_steps=60,
            model_reporters={
                "Rabbits": compute_population_r,
                "Plants": compute_population_p} #Reports gini coeff (defined above) at the end of each run (not after each step)
        )

    batch_run.run_all()
    
    run_data = batch_run.get_model_vars_dataframe()
    run_data.head()
    #plt.scatter(run_data.R, run_data.Plants)
    #plt.show()
    plt.scatter(run_data.R, run_data.Rabbits)
    plt.show()
    









