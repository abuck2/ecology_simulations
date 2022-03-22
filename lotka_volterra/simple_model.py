import numpy as np
import pandas as pd

class simple_simulation:
    def __init__(self):
        pass

    def run(self, species_parameters:list = [{"name":"species_1", "initial_pop":5, "carrying_capacity":100, "reproductive_rate" : 0.3},\
                {"name":"species_2", "initial_pop":15, "carrying_capacity":50, "reproductive_rate" : 0.6}], species_effects:dict = {},\
                steps:int = 20):
        
        population_size = {species["name"]:[species["initial_pop"]] for species in species_parameters}
        for step in range(0, steps):
            self.iterative_run(population_size, species_effects, species_parameters, step)
            

    def iterative_run(self, population_size, species_effects, species_parameters, step):
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
                
                competitor_species_data = [d for d in species_parameters if d['name'] == cause_species]
                n_other = population_size
                k_other = competitor_species_data["carrying_capacity"]
                r_other = competitor_species_data["reproductive_rate"]
                other_species.append((effect,n_other, r_other, k_other))
            
            carry, reprod = self.get_k_r(species)

            competition_factor = 1-(current_pop/carry)
            for index, elem in enumerate(other_species):
                competition_factor = competition_factor - (elem[0])
            
            new_pop = (reprod*current_pop)
            
   

    def iterative_plot(self):
        pass

    def general_plot(self):
        pass

   

if __name__=="__main__":
    sim = simple_simulation()
    sim.run(species_effects={"species_1":{"species_2":5}})