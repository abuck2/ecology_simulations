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

"""
To add :
    - Move rabbits feeding to new method - Done
    - Add carrot ressources on the map?- Done
    - Datacollector at agent level - Check how to collect one species - ok
    - Make rabbits find plants - ok
    - Add reproduction:
        - Sexual for rabbits:
            - Add a sex for each agent
        - shoots for plants
    - move cellmates in step function
    - Removes prints, add logger
    - Add different kind of agent?
    - Comment
    - Readme
    - Remove useless libs
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
    def __init__(self, unique_id:int, model, sex:bool):
        super().__init__(unique_id, model)
        self.carrot = 7
        self.health = 5
        
        self.unique_id = unique_id
        self.sex = sex
        self.reprod_rate = 0.4 #they fuck like bunnies

    def step(self):

        #Moving
        self.move()
        
        #extracting carrot
        self.extract_carrot()
        
        #reproduce if possible
        self.sexual_reprod()
        
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

    def sexual_reprod(self):
        #Rabbits in the same location
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates = [obj for obj in cellmates if isinstance(obj, Rabbit)] #Don't give carrot to plants
        if cellmates:
            for cellmate in cellmates:
                if cellmate.sex != self.sex:
                    match = random.random()
                    if self.reprod_rate > match:
                        sex = bool(random.getrandbits(1))
                        new_id, all_ids = self.model.get_next_id() 
                        a = Rabbit(new_id, self.model, sex)
                        self.model.grid.place_agent(a, self.pos)
                        self.model.schedule.add(a)
                        print("HO WAW!! Rabbit {} and {} made baby {}!!".format(self.unique_id, cellmate.unique_id, a.unique_id))
                break #Only reproducing with on rabbit per turn 
