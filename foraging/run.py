from agents import Rabbit, Plant, Fox
from model import ForagingModel
from mesa.batchrunner import BatchRunner
import matplotlib.pyplot as plt



def compute_population_r(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Rabbit)])

def compute_population_p(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Plant)])

def compute_population_f(model):
    return len([agent for agent in model.schedule.agents if isinstance(agent, Fox)])

def average_rabbit_health(model):
    rabbits = [agent for agent in model.schedule.agents if isinstance(agent, Rabbit)]
    agent_health = [agent.health for agent in rabbits]
    return sum(agent_health) / len(agent_health)





def run(batch:bool, graphics:bool):
    if bool:
        #######
        #Run a batch of models
        #######
        #Parameters settings
        #Fixed grid size
        fixed_params = {
            "width": 10,
            "height": 10,
            "P" : 15,
            "F" : 5
            }
        #Variable number of rabbits
        variable_params = {"R": range(10, 30, 5)}

        #Batch running instanciation
        batch_run = BatchRunner(
                ForagingModel,
                variable_params,
                fixed_params,
                iterations=3,
                max_steps=60,
                model_reporters={
                    "Rabbits": compute_population_r,
                    "Plants": compute_population_p} #Reports gini coeff (defined above) at the end of each run (not after each step)
            )

        batch_run.run_all()
        if graphics:
            run_data = batch_run.get_model_vars_dataframe()
            run_data.head()
            plt.scatter(run_data.R, run_data.Plants)
            plt.show()
            plt.scatter(run_data.R, run_data.Rabbits)
            plt.show()

if __name__=="__main__":
    run(batch=True, graphics=True)
