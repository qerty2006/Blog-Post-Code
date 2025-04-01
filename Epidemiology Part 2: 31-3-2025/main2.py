from typing import Dict, List, Union, Callable
from virussim2 import VirusSimulation, Person, Population, Virus, Government
import os
import matplotlib.pyplot as plt
import time
import pandas as pd

# This main file allows testing a single configuration and they plot it with matplotlib

default_virus_config = {
    "name": "default", # name of the virus
    "recoveryOdds": 0.1, # recovery odds
    "deathOdds": 0.03, # death odds
    "incubation_period": 5, # incubation period
    "vaccine_time": 14, # time for vaccine to be effective
    "vaccine_exist": lambda day: day < 0, # function to check if vaccine exists
    
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
default_population_config = {
    "Population": 50000, # number of people
    "initial_infected": 10, # number of initially infected
    "connection_odds": 0.01, # odds of connection between 2 people
    "isolation_connection_odds": 0.01, # odds of connection between 2 people while isolated
    "immuno_odds": 0.04,
    "vaccinated_odds": .75,
    "asymptomatic_odds": 0.1,
    "mask_odds": 0.0,
    "immunovacodds": 0.25,
    
    "mask_threshold": 0.1,
    "mask_floor": 0.05,
    "mask_fail": 0.8,
    
    "isolate_threshold": 0.1,
    "isolate_floor": 0.05,
    "isolate_fail": 0.1,
    
    "vaccinate_threshold": 0.1,
    "vaccinate_floor": 0.05,
    "vaccinate_fail": 0.8,
}
default_government_config = {
    "vaccinate_threshold": 1, # Government triggers vaccination campaign at 1% infection
    "vaccinate_floor": 1, # Mandate deactivates at 0.5%
    "vaccinate_amount": 0.99, # wants everyone to be vaccinated
    "vaccinate_fail": 0.99, # Only 0.001% of unvaccinated people get vaccinated on a given day

    "mask_threshold": 1, # Government triggers mask mandate at 10% infection
    "mask_floor": 1, # Mandate deactivates at 0.5%
    "mask_amount": 0.99, # wants everyone to wear masks
    "mask_fail": 0.8, # Only 0.001% of unmasked people start wearing masks on a given day

    "isolate_threshold":1, # Government triggers isolation mandate at 10% infection
    "isolate_floor": 1, # Mandate deactivates at 0.5%
    "isolate_amount": 0.8, # wants almost everyone to be isolated
    "isolate_fail": 0.5, # Only 0.001% of healthy people start isolating on a given day
    "sick_isolate_fail": 0.01 # If sick, forced to isolate
}
test_sim_config = {
    "population": default_population_config,
    "government": default_government_config, 
    "virus": default_virus_config
}

test_sim_config["virus"]["deathOdds"] = 0.015
test_sim_config["virus"]["recovered_infection"] = 1
test_sim_config["virus"]["recovered_contraction"] = 1
test_sim_config["virus"]["recovered_recovery"] = 1
test_sim_config["virus"]["recovered_death"] = 1

sim = VirusSimulation(test_sim_config, preinstalled = False)

data = {
    "Day": [],
    "Healthy": [],
    "Infected": [],
    "Sick": [],
    "Recovered": [],
    "Dead": [],
    "Immuno": [],
    
    "Vaccinated": [],
    "Asymptomatic": [],
    "Isolated": [],
    "Masked": []
    
    
}
for i in range(1000):
    if not sim.step(debug=True): break
    data_keys = list(data.keys())
    sim_keys = ["Day", "end_healthy", "end_infected", "sick", "recovered", "dead", "immunocompromised", "vaccinated", "asymptomatic", "isolated", "masked"]    
    for j in range(len(data_keys)):
        data[data_keys[j]].append(sim.get_simulation_info()[sim_keys[j]])

df = pd.DataFrame(data)
plt.plot(df['Day'], df['Healthy'], label = 'Healthy')
plt.plot(df['Day'], df['Infected'], label = 'Infected')
plt.plot(df['Day'], df['Sick'], label = 'Sick')
plt.plot(df['Day'], df['Recovered'], label = 'Recovered')
plt.plot(df['Day'], df['Dead'], label = 'Dead')


plt.plot(df['Day'], df['Immuno'], label = 'Immunocompromised')
plt.plot(df['Day'], df['Vaccinated'], label = 'Vaccinated')
plt.plot(df['Day'], df['Asymptomatic'], label = 'Asymptomatic')

plt.plot(df['Day'], df['Isolated'], label = 'Isolated')
plt.plot(df['Day'], df['Masked'], label = 'Masked')

plt.xlabel('days')
plt.ylabel('number of people')
plt.legend()
plt.show()

