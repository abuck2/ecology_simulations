from agents import Rabbit, Plant, Fox
from model import ForagingModel, compute_population_r, compute_population_p, compute_population_f
from mesa.batchrunner import BatchRunner
import matplotlib.pyplot as plt


def batch_run(graphics:bool, steps:int = 20):
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
            max_steps=steps,
            model_reporters={
                "Rabbits": compute_population_r,
                "Plants": compute_population_p,
                "Foxes" : compute_population_f}
        )

    batch_run.run_all()
    if graphics:
        run_data = batch_run.get_model_vars_dataframe()
        run_data.head()
        plt.scatter(run_data.R, run_data.Plants)
        plt.show()
        plt.scatter(run_data.R, run_data.Rabbits)
        plt.show()
        plt.scatter(run_data.R, run_data.Rabbits)
        plt.show()

def run(graphics:bool, steps:int, R:int, P:int, F:int, width:int, height:int):
    model = ForagingModel(R, P, F, width, height)
    for i in range(steps):
            model.step()
    data = model.datacollector.get_model_vars_dataframe()
    data.Rabbits.plot()
    data.Plants.plot()
    #data.Foxes.plot()
    plt.show()




if __name__=="__main__":
    #run(graphics=False, steps = 2000, R=15, P=10, F=1, width=30, height=30)
    #run(graphics=False, steps = 2000, R=50, P=150, F=30, width=30, height=30)
    run(graphics=False, steps = 20000, R=50, P=1500, F=60, width=30, height=30)

