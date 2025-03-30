from typing import Dict, List, Union, Callable
from virussim2 import VirusSimulation, Person, Population, Virus, Government
import os
import matplotlib.pyplot as plt
import time

test_virus_config = {
    "name": "default", # name of the virus
    "recoveryOdds": 0.1, # recovery odds
    "deathOdds": 0.03, # death odds
    "incubation_period": 5, # incubation period
    "vaccine_time": 14, # time for vaccine to be effective
    "vaccine_exist": lambda day: day > 60, # function to check if vaccine exists
    
    "infectious": [0.3, 0.2, 0.1], # infectiousness by various means
    "contract": [0.9, 0.95, 0.1], # contraction by various means
    "effectiveness": [0.7, 0.95, 0.1], # effectiveness of masking for various means

    "asymptomatic_infection": 0.75, # Modifier for the asymptomatic infection rate, typically less likely to spread (<1)
    "asymptomatic_contraction": 1, # Modifier for the asymptomatic contraction rate, typically no effect on contraction (=1)
    "asymptomatic_recovery": 10, # Modifier for the asymptomatic recovery rate, typically more likely to recover (>1)
    "asymptomatic_death": 0.01, # Modifier for the asymptomatic death rate, typically less likely to die (<1)

    "immuno_infection": 1.2, # Modifier for the immunocompromised infection rate, typically more likely to spread (>1)
    "immuno_contraction": 1.6, # Modifier for the immunocompromised contraction rate, typically more likely to contract (>1)
    "immuno_recovery": 0.1, # Modifier for the immunocompromised recovery rate, typically less likely to recover (<1)
    "immuno_death": 5, # Modifier for the immunocompromised death rate, typically more likely to die (>1)

    "vaccine_infection": 0.75, # Modifier for the vaccinated infection rate, typically less likely to spread (<1)
    "vaccine_contraction": 0.8, # Modifier for the vaccinated contraction rate, typically less likely to contract (<1)
    "vaccine_recovery": 5, # Modifier for the vaccinated recovery rate, typically more likely to recover (>1) 
    "vaccine_death": 0.1, # Modifier for the vaccinated death rate, typically less likely to die (<1)

    "recovered_infection": 0.75, # Modifier for the recovered infection rate, typically less likely to spread (<1) 
    "recovered_contraction": 0.8, # Modifier for the recovered contraction rate, typically less likely to contract (<1)
    "recovered_recovery": 2, # Modifier for the recovered recovery rate, typically more likely to recover (>1)
    "recovered_death": 0.5, # Modifier for the recovered death rate, typically less likely to die (<1)
}
test_population_config = {
    "Population": 50000, # number of people
    "initial_infected": 10, # number of initially infected
    "connection_odds": 0.01, # odds of connection between 2 people
    "isolation_connection_odds": 0.1, # odds of connection between 2 people while isolated
    "immuno_odds": 0.04,
    "vaccinated_odds": 0.0,
    "asymptomatic_odds": 0.1,
    "mask_odds": 0.0,
    "immunovacodds": 0.5,
    
    "mask_threshold": 0.1,
    "mask_floor": 0.05,
    "mask_fail": 0.1,
    
    "isolate_threshold": 0.1,
    "isolate_floor": 0.05,
    "isolate_fail": 0.1,
    
    "vaccinate_threshold": 0.1,
    "vaccinate_floor": 0.05,
    "vaccinate_fail": 0.99,
}
test_government_config = {
    "vaccinate_threshold": 0.1,
    "vaccinate_floor": 0.07,
    "vaccinate_amount": 0.99,
    "vaccinate_fail": 0.1,

    "mask_threshold": 0.1,
    "mask_floor": 0.07,
    "mask_amount": 0.9,
    "mask_fail": 0.1,

    "isolate_threshold": 0.1,
    "isolate_floor": 0.07,
    "isolate_amount": 0.8,
    "isolate_fail": 0.1,
}

test_sim_config = {
    "virus": test_virus_config,
    "population": test_population_config,
    "government": test_government_config,
}


def runstatssim(test_virus_config, test_population_config, test_government_config, iters = 10, debug = False):
    virus = Virus(test_virus_config)
    government = Government(test_government_config)
    config = []
    for i in range(iters):
        population = Population(test_population_config)
        config.append([virus,population,government])

    results = []
    for i in range(iters):
        sim = VirusSimulation(config[i], preinstalled = True)
        sim.bigsim(max_steps = 1000, debug = debug)
        results.append(sim.get_simulation_info())
        print(sim)

    return results

def getaverages(results):
    averages = {}
    for key in results[0].keys():
        total = 0
        for sim in results:
            total += sim[key]
        averages[key] = round(total/len(results), 2)
        print(f"{key}: {averages[key]}")
    return averages

default_averages = getaverages(runstatssim(test_virus_config, test_population_config, test_government_config, iters = 3, debug = True))

#send into csv via datafram
import pandas as pd

df = pd.DataFrame.from_dict(default_averages, orient='index')
df.to_csv('default_config.csv')

