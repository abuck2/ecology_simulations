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

"""
To add :
    - Move rabbits feeding to new method - Done
    - Add carrot ressources on the map?- Done
    - Datacollector at agent level - Check how to collect one species - ok
    - Make rabbits find plants - ok
    - Add reproduction - Done
        - Sexual for rabbits - Done
        - shoots for plants - Done
    - move cellmates in step function - Done
    - Add foxes - Done
    - add run.py
    - add stop condition if species get extinct
    - Comment
    - Readme
    - Remove useless libs
    - add the name=main from model to run.py
    - Removes prints, add logger -> check first if agents moved to different files
"""


class Plant(Agent):
    def __init__(self, unique_id, model, logger, grow_time:int = 5, reprod_rate:float = 0.05):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        
        
        #Plant characteristics
        #Steps to grow to maturity
        self.grow_time = grow_time
        #initial size
        self.size = 0
        self.eatable = False
        if reprod_rate < 1 and reprod_rate >=0:
            self.reprod_rate = reprod_rate
        else :
            raise ValueError("Plants reproduction rate must be between 0 and 1")


        self.logger = logger

    def step(self):
        #Growing
        self.grow()

        #asexual reproduction
        self.cuttings()

    def grow(self):
        if self.size < self.grow_time:
            self.size+=1
        elif self.size == self.grow_time:
            self.eatable = True
        else : 
            raise ValueError("Plant size bigger than max size")

    def cuttings(self):

        match = random.random()
        if self.reprod_rate > match:
            #Where does the cutting falls
            proximity = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=True
                )
            dispersion = self.random.choice(proximity)

            #Competition from other plants
            neighbours = self.model.grid.get_cell_list_contents([dispersion])
            neighbours = [obj for obj in neighbours if isinstance(obj, Plant)]
            competition_factor = 1-(1/float(len(neighbours)+1)) #0 if no plants present, 0.5 for 1, 0.66 for 2,...

            seed_resistance = random.random()
            if seed_resistance > competition_factor:
                new_id, all_ids = self.model.get_next_id() 
                a = Plant(new_id, self.model, self.logger)
                self.model.grid.place_agent(a, dispersion)
                self.model.schedule.add(a)
                #self.logger.info("PLant {} made an offshoot : {}".format(self.unique_id, a.unique_id))


class Rabbit(Agent):
    def __init__(self, unique_id:int, model, sex:bool, logger, reprod_rate:float=0.5):
        super().__init__(unique_id, model)
        self.carrot = 5
        self.health = 4
        
        self.unique_id = unique_id
        self.sex = sex
        if reprod_rate < 1 and reprod_rate >=0:
            self.reprod_rate = reprod_rate
        else :
            raise ValueError("Plants reproduction rate must be between 0 and 1")

        self.logger = logger

    def step(self):
        
        #Agents on the same cell
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        #Moving
        self.move()
        #extracting carrot
        self.extract_carrot(cellmates)
        #reproduce if possible
        self.sexual_reprod(cellmates)
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
            #self.logger.info("Rabbit {} eats a carrot!!".format(self.unique_id))
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

    def extract_carrot(self, cellmates):
        plants_material = [obj for obj in cellmates if isinstance(obj, Plant)] #Don't make carrots from rabbits!!
        plants_material = [plant for plant in plants_material if plant.eatable == True] #carrot must be ready
        if len(plants_material) >= 1:
            other = self.random.choice(plants_material)
            self.model.grid.remove_agent(other)
            self.model.schedule.remove(other)
            print("Rabbit {} has found a carrot!!!!!".format(self.unique_id))
            self.carrot += 1
            print("Rabbit {} is giving a carrot to rabbit {}!!".format(self.unique_id, other.unique_id))

    def sexual_reprod(self, cellmates):
        #Rabbits in the same location
        cellmates = [obj for obj in cellmates if isinstance(obj, Rabbit)] #Don't give carrot to plants
        if cellmates:
            for cellmate in cellmates:
                if cellmate.sex != self.sex:
                    match = random.random()
                    if self.reprod_rate > match:
                        sex = bool(random.getrandbits(1))
                        new_id, all_ids = self.model.get_next_id() 
                        a = Rabbit(new_id, self.model, sex, self.logger)
                        self.model.grid.place_agent(a, self.pos)
                        self.model.schedule.add(a)
                        print("HO WAW!! Rabbit {} and {} made baby {}!!".format(self.unique_id, cellmate.unique_id, a.unique_id))
                break #Only reproducing with on rabbit per turn 
class Fox(Agent):
    def __init__(self, unique_id:int, model, sex:bool, logger, reprod_rate:float=0.3):
        super().__init__(unique_id, model)
        self.max_health = 10
        self.health = 10
        
        self.unique_id = unique_id
        self.sex = sex
        if reprod_rate < 1 and reprod_rate >=0:
            self.reprod_rate = reprod_rate
        else :
            raise ValueError("Plants reproduction rate must be between 0 and 1")

        self.logger = logger

    def step(self):
        
        #Agents on the same cell
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        #Moving
        self.move()
        #reproduce if possible
        self.sexual_reprod(cellmates)
        #eating rabbits
        self.feed(cellmates)

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
    
    def feed(self, cellmates):
        
        eaten = self.eat_rabbit(cellmates)
        """ 
        if eaten :
            self.health = self.max_health
        else : 
            self.move()
            eaten = self.eat_rabbit
        """ 
        #self.logger.info("{} has eaten {}".format(self.unique_id, eaten))
        if eaten :
            self.health = self.max_health
        else:
            self.health -= 1
        
        # Kill the fox if he spend a few days without carrots
        if self.health == 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            #print("Fox {} is dead :'(".format(self.unique_id))
            self.logger.info("Fox {} is dead :'(".format(self.unique_id))

    def eat_rabbit(self, cellmates):
        rabbit = [obj for obj in cellmates if isinstance(obj, Rabbit)]
        #self.logger.info(rabbit)
        if rabbit:
            other = self.random.choice(rabbit)
            self.model.grid.remove_agent(other)
            self.model.schedule.remove(other)
            print("Fox {} has eaten rabbit {}".format(self.unique_id, other.unique_id))
            return True
        else : 
            return False

    def sexual_reprod(self, cellmates):
        """
        To adapt for foxes
        """
        #Foxes in the same location
        cellmates = [obj for obj in cellmates if isinstance(obj, Fox)]
        if cellmates:
            for cellmate in cellmates:
                if cellmate.sex != self.sex:
                    match = random.random()
                    if self.reprod_rate > match:
                        sex = bool(random.getrandbits(1))
                        new_id, all_ids = self.model.get_next_id() 
                        a = Fox(new_id, self.model, sex, self.logger)
                        try :
                            self.model.grid.place_agent(a, self.pos)
                        except Exception as e:
                            print(a, self.pos)
                            raise ValueError(e)


                        self.model.schedule.add(a)
                        print("HO WAW!! Rabbit {} and {} made baby {}!!".format(self.unique_id, cellmate.unique_id, a.unique_id))
                break #Only reproducing with on rabbit per turn 
