from mesa import Agent, Model
from mesa.space import MultiGrid
#Scheduler
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt
import numpy as np

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

        # Create agents
        for i in range(self.num_agents):
            a = Rabbit(i, self)

            self.schedule.add(a)

            #Agent is activated in a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        #advance simulation one step
        self.schedule.step()


if __name__=="__main__":
    #empty_model = ForagingModel(10)
    #empty_model.step()
    

    all_carrots = []
    for j in range(100):
        # Run the model
        model = ForagingModel(10, 5, 5)
        for i in range(10):
            model.step()

