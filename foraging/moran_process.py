import axelrod as axl
from pprint import pprint
import matplotlib.pyplot as plt

players = [axl.Alternator(), axl.TitForTat(), axl.Grudger(), axl.Cooperator(), axl.Cooperator(), axl.Cooperator(),
        axl.TitForTat(), axl.TitForTat(), axl.TitForTat(),
        axl.Random()]


#Basic process
mp = axl.MoranProcess(players, seed = 14)
populations = mp.play()

pprint(populations)
ax = mp.populations_plot()
plt.show() 

#Changing the mutation rate
mp = axl.MoranProcess(players, mutation_rate=0.1, seed=10)
for _ in mp:
    if len(mp.population_distribution()) == 1:
        break


#Evolutive process : might not converge
C = axl.Action.C
players = [axl.EvolvableFSMPlayer(num_states=2, initial_state=1, initial_action=C) for _ in range(5)]
mp = axl.MoranProcess(players, turns=10, mutation_method="atomic", seed=1)
population = mp.play()  

pprint(populations)
ax = mp.populations_plot()
plt.show() 
