import numpy as np
import pandas as pd

class simple_simulation:
    def __init__(self):
        pass

    def run(self, init_sizes:dict = {"species_1":5, "species_2":10}, species_effects:dict = {},\
                carrying_capacity:dict = {"species_1":100, "species_2":20}, reproductive_rate:dict = {"species_1":0.3, "species_2":0.6},\
                steps:int = 20):
        
        species_effects = self.complete_effects(species_effects, init_sizes)
        population_size = {k:[v] for k, v in init_sizes.items()}
        for step in range(0, steps):
            self.iterative_run(population_size, species_effects, carrying_capacity, reproductive_rate, step)
            

    def iterative_run(self, population_size, species_effects, carrying_capacity, reproductive_rate, step):
        #Use a try Except KeyError instead
        for species, population in population_size:
            current_pop = population[-1]
            other_species = []
            #Check how other species influence this one
            for cause_species in population_size.keys():
                try :
                    effect = species_effects[cause_species][species]
                except KeyError:
                    effect = 1

                k_other, r_other = self.get_k_r(cause_species, reproductive_rate, carrying_capacity, population_size)
                other_species.append((effect, r_other, k_other))
            
            carry, reprod = self.get_k_r(species)
            
            new_pop = (reprod*current_pop)
            
    def get_k_r(self, species, reproductive_rate, carrying_capacity, population_size):
        try :
            reprod = reproductive_rate[species]
        except KeyError:
            reprod = 0.3

        try :
            carry = carrying_capacity[species]
        except KeyError:
            carry = population_size[0]*1.5
        return carry, reprod

    def iterative_plot(self):
        pass

    def general_plot(self):
        pass

    def complete_effects(self, species_effects, init_sizes):
        """
        Deprecated
        """
        complete_effects = {}
        cause_species = list(species_effects.keys())

        #For each existing species, do we know how they affect others?
        for species_1, pop_size in init_sizes.items():
            #Yes
            if species_1 in cause_species:
                one_species_effect = species_effects[species_1]
                #Do we know its effect on every other species?
                for species_2, pop_size in init_sizes.items():
                    #We don't care about its effect on itself
                    if species_2 != species_1:
                        #If we don't have data on how species_1 affects species_2
                        if species_2 not in one_species_effect:
                            species_effects.update({species_1:{species_2:1}})

            #No
            else : 
                #Update dict with value 1 for all other species
                pass

if __name__=="__main__":
    sim = simple_simulation()
    sim.run(species_effects={"species_1":{"species_2":5}})