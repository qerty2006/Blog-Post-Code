from typing import Dict, List, Union, Callable
from virussim2 import VirusSimulation, Person, Population, Virus, Government
import os
import matplotlib.pyplot as plt
import networkx as nx

test_virus_config = {
    "name": "default",
    "recoveryOdds": 0.1,
    "deathOdds": 0.01,
    "incubation_period": 5,
    "vaccine_time": 14,
    "vaccine_exist": lambda x: True,
    "infectious": [0.3, 0.2, 0.1],
    "contract": [0.9, 0.95, 0.1],
    "effectiveness": [0.7, 0.95, 0.1],

    "asymptomatic_infection": 1,
    "asymptomatic_contraction": 1,
    "asymptomatic_recovery": 0.1,
    "asymptomatic_death": 0.01,

    "immuno_infection": 1,
    "immuno_contraction": 1,
    "immuno_recovery": 0.1,
    "immuno_death": 0.01,

    "vaccine_infection": 1,
    "vaccine_contraction": 1,
    "vaccine_recovery": 0.1,
    "vaccine_death": 0.01,

    "recovered_infection": 1,
    "recovered_contraction": 1,
    "recovered_recovery": 0.1,
    "recovered_death": 0.1,
}

test_population_config = {
    "Population": 50000,
    "initial_infected": 10,
    "connection_odds": 0.01,
    "isolation_connection_odds": 0.005,
    "immuno_odds": 0.1,
    "vaccinated_odds": 0.0,
    "immunovacodds": 0.05,
    "asymptomatic_odds": 0.1,
    "mask_odds": 0.0,
    
    "mask_threshold": 0.1,
    "mask_floor": 0.05,
    "mask_fail": 0.1,
    
    "isolate_threshold": 0.1,
    "isolate_floor": 0.05,
    "isolate_fail": 0.1,
    
    "vaccinate_threshold": 0.1,
    "vaccinate_floor": 0.05,
    "vaccinate_fail": 0.1,
}

test_government_config = {
    "vaccinate_threshold": 0.1,
    "vaccinate_floor": 0.05,
    "vaccinate_amount": 0.1,
    "vaccinate_fail": 0.1,

    "mask_threshold": 0.1,
    "mask_floor": 0.05,
    "mask_amount": 0.1,
    "mask_fail": 0.1,

    "isolate_threshold": 0.1,
    "isolate_floor": 0.05,
    "isolate_amount": 0.1,
    "isolate_fail": 0.1,
}

test_sim_config = {
    "virus": test_virus_config,
    "population": test_population_config,
    "government": test_government_config,
}

sim = VirusSimulation(test_sim_config)

print(sim)

plot_data = {
    "infected": [],
    "recovered": [],
    "dead": [],
    "vaccinated": [],
    "isolated": [],
    "masked": [],
    "immunocompromised": [],
    "asymptomatic": []
}
while sim.step() and sim.population.days < 1000:
    #clear console
    os.system('cls' if os.name == 'nt' else 'clear')
    print(sim)
    plot_info = sim.getplotinfo()
    for key, value in plot_info.items():
        plot_data[key].append(value)

os.system('cls' if os.name == 'nt' else 'clear')
print(sim)

import matplotlib.pyplot as plt

# Plot the collected data
plt.figure(figsize=(12, 8))
days = list(range(len(plot_data["infected"])))

plt.plot(days, plot_data["infected"], label='Infected', color='red')
plt.plot(days, plot_data["recovered"], label='Recovered', color='blue')
plt.plot(days, plot_data["dead"], label='Dead', color='black')
plt.plot(days, plot_data["vaccinated"], label='Vaccinated', color='purple')
plt.plot(days, plot_data["isolated"], label='Isolated', color='orange')
plt.plot(days, plot_data["masked"], label='Masked', color='green')
plt.plot(days, plot_data["immunocompromised"], label='Immunocompromised', color='brown')
plt.plot(days, plot_data["asymptomatic"], label='Asymptomatic', color='pink')

plt.xlabel('Days')
plt.ylabel('Number of People')
plt.title('Virus Spread Simulation Over Time')
plt.legend()
plt.grid(True)
plt.show()

