from mesa import Agent, Model
#Space grid
from mesa.space import MultiGrid
#Scheduler
from mesa.time import RandomActivation
#Data collection
from mesa.datacollection import DataCollector
#batches of multiple models -> run the model multiple time
from mesa.batchrunner import BatchRunner

import matplotlib.pyplot as plt
import numpy as np

"""
To add : 
    - Kill the rabbits when they can't eat?
    - Add carrot ressources on the map?
    - Add different kind of agent?
"""

#function to compute values for the datacollector
def compute_gini(model):
    agent_carrots = [agent.carrot for agent in model.schedule.agents]
    x = sorted(agent_carrots)
    N = model.num_agents
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)

def average_rabbit_health(model):
    agent_health = [agent.health for agent in model.schedule.agents]
    return sum(agent_health) / len(agent_health)

class Rabbit(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carrot = 7
        self.unique_id = unique_id
        self.health = 5

    def step(self):
        self.move()
        #print(self.unique_id)
        if self.carrot == 0:
            print("Rabbit {} ate all the carrots...".format(self.unique_id))
            self.health -= 1
            return 
        elif self.carrot < 5:
            self.carrot -= 1
            print("Rabbit {} eats a carrot!!".format(self.unique_id))
        else :
            self.give_carrot()
    
    def move(self):
        """
        Makes the rabbit moves to a neighbouring cell
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_carrot(self):
        #Rabbits in the same location
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            other.carrot += 1
            self.carrot -= 1
            print("Rabbit {} is giving a carrot to rabbit {}!!".format(self.unique_id, other.unique_id))

class ForagingModel(Model):
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        
        #Activation of the agents every step is random
        self.schedule = RandomActivation(self)

        #running variable for the batch runner. Simulation stops if a certain condition is met
        #If set to True, obviously never stops
        self.running = True

        # Create agents
        for i in range(self.num_agents):
            a = Rabbit(i, self)
            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        
        #Initialize the data collector when model is initialized
        self.datacollector = DataCollector(
                model_reporters={"Gini": compute_gini, "health":average_rabbit_health},  # the functions are defined above with computaion for the colleor
                agent_reporters={"Carrot": "carrot"}) #agent-level data

    def step(self):
        #collect data
        self.datacollector.collect(self)
        #advance simulation one step
        self.schedule.step()


if __name__=="__main__":
    #Run the model once for x steps
    all_carrots = []
    model = ForagingModel(10, 5, 5)
    for i in range(15):
        model.step()
    
    """
    #Get agent-level data from DataCollector
    agent_nr = 9
    carrots_data = model.datacollector.get_agent_vars_dataframe()
    print(carrots_data)
    end_c = carrots_data.xs(agent_nr, level="AgentID")["Carrot"]
    end_c.hist(bins=range(carrots_data.Carrot.max()+1))
    plt.show()
    """ 
    """
    #Rising social inequalities in virtual rabbits (get model-level data from DataCollector)
    gini = model.datacollector.get_model_vars_dataframe()["health"]
    gini.plot()
    plt.show()
    """
    #######
    #Run a batch of models
    #######
    #Parameters settings
    #Fixed grid size
    fixed_params = {
        "width": 10,
        "height": 10
        }
    #Variable number of rabbits
    variable_params = {"N": range(10, 500, 10)}

    #Batch running instanciation
    batch_run = BatchRunner(
            ForagingModel,
            variable_params,
            fixed_params,
            iterations=3,
            max_steps=10,
            model_reporters={"Gini": compute_gini} #Reports gini coeff (defined above) at the end of each run (not after each step)
        )

    batch_run.run_all()
    
    run_data = batch_run.get_model_vars_dataframe()
    run_data.head()
    plt.scatter(run_data.N, run_data.Gini)
    plt.show()
    









