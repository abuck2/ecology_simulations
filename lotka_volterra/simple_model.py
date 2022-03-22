import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class simple_simulation:
    def __init__(self):
        pass

    def run(self, species_parameters:list = [{"name":"species_1", "initial_pop":5, "carrying_capacity":100, "reproductive_rate" : 2},\
                {"name":"species_2", "initial_pop":15, "carrying_capacity":50, "reproductive_rate" : 1}], species_effects:dict = {},\
                steps:int = 20):
        
        population_size = {species["name"]:[species["initial_pop"]] for species in species_parameters}
        for step in range(0, steps):
            self.iterative_run(population_size, species_effects, species_parameters, step)
            
        print(population_size)
        pop_data = pd.DataFrame(population_size)
        self.iterative_plot(pop_data) 
        self.general_plot(species_parameters, species_effects)   

    def iterative_run(self, population_size, species_effects, species_parameters, step):
        #Use a try Except KeyError instead
        for species, population in population_size.items():
            
            current_pop = population[-1]
            if current_pop<=0:
                population_size[species].append(0)
                continue

            other_species = []
            #Check how other species influence this one
            for cause_species, competitor_pop in population_size.items():
                try :
                    effect = species_effects[cause_species][species]
                except KeyError:
                    effect = 1
                
                competitor_species_data = [d for d in species_parameters if d['name'] == cause_species][0]
                n_other = competitor_pop[-1]
                k_other = competitor_species_data["carrying_capacity"]
                r_other = competitor_species_data["reproductive_rate"]
                other_species.append({"effect":effect,"pop":n_other, "rep":r_other, "carrying":k_other})
            
            species_data = [d for d in species_parameters if d['name'] == species][0]
            carry = species_data["carrying_capacity"]
            reprod = species_data["reproductive_rate"]
            competition_factor = 1-(current_pop/carry)
            
            for index, elem in enumerate(other_species):
                competition_factor = competition_factor - (elem["effect"]*elem["pop"]/carry)
            
            new_pop = reprod*current_pop*competition_factor
            if new_pop < 0 :
                new_pop = 0
            population_size[species].append(new_pop)
        return population_size
   

    def iterative_plot(self, pop_data):
        sns.lineplot(data=pop_data)
        plt.show()

    def general_plot(self, species_parameters, species_effects):
        """
        x-axis represents sepcies 2, y-axis represents species 1
        """
        data_species_1 = species_parameters[0]
        data_species_2 = species_parameters[1]

        #effect of two on one
        try : 
            two_on_one = species_effects[data_species_2["name"]][data_species_1["name"]]
        except KeyError:
            two_on_one = 1

        #effect of one on two
        try : 
            one_on_two = species_effects[data_species_1["name"]][data_species_2["name"]]
        except KeyError:
            one_on_two = 1

        point1 = [0, data_species_1["carrying_capacity"]/two_on_one]
        point2 = [data_species_1["carrying_capacity"], 0]
        x_values = [point1[0], point2[0]]
        y_values = [point1[1], point2[1]]
        plt.plot(x_values, y_values)
        plt.annotate("Ki/aij", point1)
        plt.annotate("Ki", point2)
        
        point3 = [data_species_2["carrying_capacity"]/one_on_two, 0]
        point4 = [0, data_species_2["carrying_capacity"]]
        x_values = [point3[0], point4[0]]
        y_values = [point3[1], point4[1]]
        plt.plot(x_values, y_values)
        plt.annotate("Kj/aji", point3)
        plt.annotate("Kj", point4)
        
        plt.show()

   

if __name__=="__main__":
    sim = simple_simulation()
    sim.run(species_effects={"species_1":{"species_2":1}})