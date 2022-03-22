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


class Plant(Agent):
    
    def __init__(self, unique_id, model, logger, grow_time:int = 5, reprod_rate:float = 0.05):
        """Initialization of a plant class

        Args:
            unique_id (int): id of a plant instance
            model (mesa model): Model to which the agent beong
            logger (logger): a logger for the plants agent
            grow_time (int, optional): Time for a new plant to become edible (in nbr of steps). Defaults to 5.
            reprod_rate (float, optional): Base reproduction rate, not taking into account competition or terrain. Defaults to 0.05.

        Raises:
            ValueError: Error if values are out of bound
        """
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
        """Actions take by a plant every step (grow, and try to reproduce asexually)
        """
        #Growing
        self.grow()

        #asexual reproduction
        self.cuttings()

    def grow(self):
        """Every step, increments the plant growth by one until plant is eatabl

        Raises:
            ValueError: Error only for testing
        """
        if self.size < self.grow_time:
            self.size+=1
        elif self.size == self.grow_time:
            self.eatable = True
        else : 
            raise ValueError("Plant size bigger than max size")

    def cuttings(self):
        """Plant reproduction, a plant reproduces if the following conditions are met : 
            - The base reproduction rate is the likelihood for a new plant to start growing
            - If a new plant starts growing, they will start in a random neighbouring case of the mother plant
            - The new plant will suffer from competition of plants in the same case and might not grow
            - Depending on the terrain, a plant might or might not manage to grow
        """

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
            conditions = [obj for obj in neighbours if isinstance(obj, Terrain)]
            neighbours = [obj for obj in neighbours if isinstance(obj, Plant)]
            print(conditions)
            competition_factor = 1-(1/float(len(neighbours)+1)) #0 if no plants present, 0.5 for 1, 0.66 for 2,...

            seed_resistance = random.random()
            if seed_resistance > competition_factor and conditions[0].altitude > 0 :
            #if seed_resistance > competition_factor :
                new_id, all_ids = self.model.get_next_id() 
                a = Plant(new_id, self.model, self.logger, reprod_rate = self.model.p_reprod_rate)
                self.model.grid.place_agent(a, dispersion)
                self.model.schedule.add(a)
                #self.logger.info("PLant {} made an offshoot : {}".format(self.unique_id, a.unique_id))


class Rabbit(Agent):
    def __init__(self, unique_id:int, model, sex:bool, logger, reprod_rate:float=0.5, max_health:int=4):
        """Initialization of a Rabbit

        Args:
            unique_id (int): unique id of a rabbit instace
            model (mesa model): Model of the obkject
            sex (bool): Sex of the rabbits, for reproduction, two rabbits of opposite seepx must meet
            logger (logger): Logger for the object
            reprod_rate (float, optional): Base reproduction rate. Defaults to 0.5.
            max_health (int, optional): Number of steps a rabbit can spend without eating. Defaults to 4.

        Raises:
            ValueError: error if reproduction rate is out of bounds
        """ 
        super().__init__(unique_id, model)
        self.carrot = 5
        self.health = max_health
        
        self.unique_id = unique_id
        self.sex = sex
        if reprod_rate < 1 and reprod_rate >=0:
            self.reprod_rate = reprod_rate
        else :
            raise ValueError("Rabbits reproduction rate must be between 0 and 1")

        self.logger = logger

    def step(self):
        """Actions performed by rabbits every step
            - The rabbit move one case
            - The rabbit tries to find a carrot
            - The rabbit tries to reproduce
            - The rabbit tries to eat
            
        Rabbits play nice with eachother, a rabbit can give another rabbit a carrot if he has a lot of them
        
        """
        
        #Agents on the same cell #shoud be move avec self.move()
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
        """The rabbit will tries to eat a carrot. If he can't eat, the counter will decrease until he starves
        """
        if self.carrot == 0:
            self.logger.info("Rabbit {} ate all the carrots...".format(self.unique_id))
            self.health -= 1
            # Kill the rabbit if he spend a few days without carrots
            if self.health == 0:
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                self.logger.info("Rabbit {} is dead :'(".format(self.unique_id))

        elif self.carrot < 5:
            self.carrot -= 1
            self.health = 5
            #self.logger.info("Rabbit {} eats a carrot!!".format(self.unique_id))
            self.logger.info("Rabbit {} eats a carrot!!".format(self.unique_id))
        
        else :
            self.give_carrot()
    
    def give_carrot(self):
        """A rabbit can try to give another rabbit a carrot
        """
        #Rabbits in the same location
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates = [obj for obj in cellmates if isinstance(obj, Rabbit)] #Don't give carrot to plants
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            other.carrot += 1
            self.carrot -= 1
            self.logger.info("Rabbit {} is giving a carrot to rabbit {}!!".format(self.unique_id, other.unique_id))

    def extract_carrot(self, cellmates):
        """A rabbit can look for plants where he is, and make them into carrots

        Args:
            cellmates (list): List of object in the same position as the rabbit instance
        """
        plants_material = [obj for obj in cellmates if isinstance(obj, Plant)] #Don't make carrots from rabbits!!
        plants_material = [plant for plant in plants_material if plant.eatable == True] #carrot must be ready
        if len(plants_material) >= 1:
            other = self.random.choice(plants_material)
            self.model.grid.remove_agent(other)
            self.model.schedule.remove(other)
            self.logger.info("Rabbit {} has found a carrot!!!!!".format(self.unique_id))
            self.carrot += 1
            self.logger.info("Rabbit {} is giving a carrot to rabbit {}!!".format(self.unique_id, other.unique_id))

    def sexual_reprod(self, cellmates):
        """A rabbit can try to reproduce if an opposite-sex rabbit is on the same case as him
        Args:
            cellmates (list): List of object in the same position as the rabbit instance
        """
        #Rabbits in the same location
        cellmates = [obj for obj in cellmates if isinstance(obj, Rabbit)] #Don't give carrot to plants
        if cellmates:
            for cellmate in cellmates:
                if cellmate.sex != self.sex:
                    match = random.random()
                    if self.reprod_rate > match:
                        sex = bool(random.getrandbits(1))
                        new_id, all_ids = self.model.get_next_id() 
                        a = Rabbit(new_id, self.model, sex, self.logger, 
                                reprod_rate = self.model.r_reprod_rate, max_health = self.model.r_max_health)
                        self.model.grid.place_agent(a, self.pos)
                        self.model.schedule.add(a)
                        self.logger.info("HO WAW!! Rabbit {} and {} made baby {}!!".format(self.unique_id, cellmate.unique_id, a.unique_id))
                break #Only reproducing with on rabbit per turn 
            
class Fox(Agent):
    def __init__(self, unique_id:int, model, sex:bool, logger, reprod_rate:float=0.3, max_health:int = 10):
        """Initialize a fox instance

        Args:
            unique_id (int): Unique if of the object
            model (mesa model): instance of a mesa model
            sex (bool): Sex of a fox instance
            logger (logger): logger for the fox instance
            reprod_rate (float, optional): Foxes reproduction probability. Defaults to 0.3.
            max_health (int, optional): Number of steps a fox can spend without eating. Defaults to 10.

        Raises:
            ValueError: Foxes reproduction rate must be between 0 and 1
        """
        super().__init__(unique_id, model)
        self.max_health = max_health
        self.health = self.max_health
        
        self.unique_id = unique_id
        self.sex = sex
        if reprod_rate < 1 and reprod_rate >=0:
            self.reprod_rate = reprod_rate
        else :
            raise ValueError("Foxes reproduction rate must be between 0 and 1")

        self.logger = logger

    def step(self):
        """Actions taken by a fox each step
            - Move one case
            - Try to reproduce with an opposite-sex fox
            - Tries to eat a rabbit
        """
        
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
        Makes the fox moves to a neighbouring cell
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
    
    def feed(self, cellmates):
        """
        Tries to eat a rabbit
        """ 
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
            #self.logger.info("Fox {} is dead :'(".format(self.unique_id))
            self.logger.info("Fox {} is dead :'(".format(self.unique_id))

    def eat_rabbit(self, cellmates):
        """Method to kill a rabbit 

        Args:
            cellmates (list): list of instance on the same cell

        Returns:
            bool: True if the fox killed a rabbit
        """
        rabbit = [obj for obj in cellmates if isinstance(obj, Rabbit)]
        #self.logger.info(rabbit)
        if rabbit:
            other = self.random.choice(rabbit)
            self.model.grid.remove_agent(other)
            self.model.schedule.remove(other)
            self.logger.info("Fox {} has eaten rabbit {}".format(self.unique_id, other.unique_id))
            return True
        else : 
            return False

    def sexual_reprod(self, cellmates):
        """
        Tries to reproduce. See the method in rabbit class
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
                        a = Fox(new_id, self.model, sex, self.logger, reprod_rate = self.model.f_reprod_rate, 
                                max_health = self.model.f_max_health)
                        try :
                            self.model.grid.place_agent(a, self.pos)
                        except Exception as e:
                            self.logger.warning(a, self.pos)
                            raise ValueError(e)


                        self.model.schedule.add(a)
                        self.logger.info("HO WAW!! Rabbit {} and {} made baby {}!!".format(self.unique_id, cellmate.unique_id, a.unique_id))
                break #Only reproducing with on rabbit per turn


class Terrain():
    """Terrain characteristics
    """
    def __init__(self, model, altitude, unique_id):
        self.unique_id = unique_id
        self.altitude = altitude

    def step(self):
        pass
