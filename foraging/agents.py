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
    - Move rabbits feeding to new method - Done
    - Add carrot ressources on the map?- Done
    - Datacollector at agent level - Check how to collect one species - ok
    - Make rabbits find plants - ok
    - Removes prints, add logger
    - Add reproduction:
        - Sexual for rabbits
        - shoots for plants
    - Add different kind of agent?
    - Comment
    - Readme
"""


class Plant(Agent):
    def __init__(self, unique_id, model, grow_time = 5):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        
        self.grow_time = grow_time
        self.size = 0
        self.eatable = False

    def step(self):
        self.grow()

    def grow(self):
        if self.size < self.grow_time:
            self.size+=1
        elif self.size == self.grow_time:
            self.eatable = True
        else : 
            raise ValueError("Plant size bigger than max size")

class Rabbit(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carrot = 7
        self.unique_id = unique_id
        self.health = 5

    def step(self):

        #Moving
        self.move()
        
        #extracting carrot
        self.extract_carrot()
        
        #eat
        self.feed()


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
    
    def feed(self):
        #Feeding - maybe move to another method
        if self.carrot == 0:
            print("Rabbit {} ate all the carrots...".format(self.unique_id))
            self.health -= 1
            # Kill the rabbit if he spend a few days without carrots
            if self.health == 0:
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                print("Rabbit {} is dead :'(".format(self.unique_id))

        elif self.carrot < 5:
            self.carrot -= 1
            self.health = 5
            print("Rabbit {} eats a carrot!!".format(self.unique_id))
        
        else :
            self.give_carrot()
    
    def give_carrot(self):
        #Rabbits in the same location
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates = [obj for obj in cellmates if isinstance(obj, Rabbit)] #Don't give carrot to plants
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            other.carrot += 1
            self.carrot -= 1
            print("Rabbit {} is giving a carrot to rabbit {}!!".format(self.unique_id, other.unique_id))

    def extract_carrot(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        plants_material = [obj for obj in cellmates if isinstance(obj, Plant)] #Don't make carrots from rabbits!!
        plants_material = [plant for plant in plants_material if plant.eatable == True] #carrot must be ready
        if len(plants_material) >= 1:
            other = self.random.choice(plants_material)
            self.model.grid.remove_agent(other)
            self.model.schedule.remove(other)
            print("Rabbit {} has found a carrot!!!!!".format(self.unique_id))
            self.carrot += 1
            print("Rabbit {} is giving a carrot to rabbit {}!!".format(self.unique_id, other.unique_id))

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
    









