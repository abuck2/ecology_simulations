import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class simple_simulation:
    def __init__(self):
        pass

    def run(self, species_parameters:list = [{"name":"species_1", "initial_pop":5, "carrying_capacity":100, "reproductive_rate" : 2},\
                    {"name":"species_2", "initial_pop":15, "carrying_capacity":100, "reproductive_rate" : 1}], \
                species_effects:list = [{"type":"competition", "from_species":"species_1", "on_species":"species_2", "intensity":0.1},\
                    {"type":"competition", "from_species":"species_2", "on_species":"species_1", "intensity":0.1},\
                    {"type":"predation", "from_species":"species_1", "on_species":"species_2", "intensity":0.1}],\
                steps:int = 20):
        
        #dict of species:pop
        population_size = {species["name"]:[species["initial_pop"]] for species in species_parameters}

        #Update population a t+1 iteratively
        for step in range(0, steps):
            self.iterative_run(population_size, species_effects, species_parameters, step)
            
        print(population_size)

        #Plot the data
        pop_data = pd.DataFrame(population_size)
        self.iterative_plot(pop_data) 
        self.general_plot(species_parameters, species_effects)   

    def iterative_run(self, population_size, species_effects, species_parameters, step):
        #Compute population a t+1
        #Use a try Except KeyError instead
        #Updates populations one by one
        for species, population in population_size.items():
            #Get latest population
            current_pop = population[-1]
            #Do not update extinct species
            if current_pop<=0:
                population_size[species].append(0)
                continue

            #Apply competition effects and add to the list of population at each step
            new_pop = self.apply_effects(species, current_pop, population_size, species_effects, species_parameters, step)
            population_size[species].append(new_pop)

            
        return population_size
    
    def apply_effects(self,species,  current_pop, population_size, species_effects, species_parameters, step):
        other_species = []
        #Check how other species influence this one
        relevant_competition = [effect for effect in species_effects if effect['on_species'] == species and effect["type"]=="competition"]
        print(relevant_competition)
        #Computer the effect of competition at time t for each competitor (aij*Nj/Ki)
        carrying_capacity = [data["carrying_capacity"] for data in species_parameters if data["name"] == species][0] #Ki
        reprod = [data["reproductive_rate"] for data in species_parameters if data["name"] == species][0] #r
        competition_effects_list = []
        for effect in relevant_competition:
            species_competitor = effect["from_species"] #aij
            population_competitor = population_size[species_competitor][-1] #Nj
            competition_effects = effect["intensity"]*population_competitor/carrying_capacity
            competition_effects_list.append(competition_effects)

        total_effect = 1-current_pop/carrying_capacity
        for competition_effect in competition_effects_list:
            total_effect = total_effect-competition_effect
            print(total_effect)

        new_pop = current_pop + current_pop*reprod*total_effect

        if new_pop < 0 :
            new_pop = 0
        return new_pop


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
            two_on_one = [comp_effect for comp_effect in species_effects if comp_effect["on_species"]==data_species_1["name"]\
                and comp_effect["from_species"]==data_species_2["name"]\
                and comp_effect["type"]=="competition"][0]["intensity"]
        except IndexError:
            two_on_one = 0

        #effect of one on two
        try : 
            one_on_two = [comp_effect for comp_effect in species_effects if comp_effect["on_species"]==data_species_2["name"]\
                and comp_effect["from_species"]==data_species_1["name"]\
                and comp_effect["type"]=="competition"][0]["intensity"]
        except IndexError:
            one_on_two = 0
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
        plt.xlabel(data_species_1["name"])
        plt.ylabel(data_species_2["name"])
        
        plt.show()

   

if __name__=="__main__":
    sim = simple_simulation()
    sim.run()