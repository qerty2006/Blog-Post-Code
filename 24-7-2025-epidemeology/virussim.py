import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import os

class VirusSimulation:
    def __init__(self, config: dict, debug: bool = False) -> None:
        """
        Initialize a VirusSimulation object with the given configuration.

        Parameters
        ----------
        config : dict[str, Union[int, float, Callable[[int], int]]]
            A dictionary containing simulation parameters. The keys and their
            default values are:
            - 'N': int, default 1000
                The size of the population.
            - 'Pn': float, default 0.02
                The probability of a random connection between two people.
            - 'Pi': float, default 0.05
                The probability of a person being immunocompromised.
            - 'Pv': float, default 0.5
                The probability of a person being vaccinated.
            - 'Pa': float, default 0.3
                The probability of a person being asymptomatic.
            - 'Pm': float, default 0.4
                The probability of a person wearing a mask.
            - 'mask_effectiveness': float, default 0.5
                The effectiveness of masks in preventing transmission.
            - 'initial_infected': int, default 5
                The number of people initially infected.
            - 'Pu': float, default 0.3
                The probability of a person spreading the virus.
            - 'Pc': float, default 0.3
                The probability of a person catching the virus.
            - 'Pk': float, default 0.01
                The probability of a person dying from the virus.
            - 'Pr': float, default 0.1
                The probability of a person recovering from the virus.
            - 'Vaccine function': Callable[[int], int], default lambda x: 0
                The function to determine the number of vaccines given at each step.

        Initializes the simulation graph and statistics.
        """

        print("Initializing default simulation")
        self.N: int = config.get('N', 1000)
        self.Pn: float = config.get('Pn', 0.02)
        self.Pi: float = config.get('Pi', 0.05)
        self.Pv: float = config.get('Pv', 0.5)
        self.Pa: float = config.get('Pa', 0.3)
        self.Pm: float = config.get('Pm', 0.4)
        self.mask_effectiveness: float = config.get('mask_effectiveness', 0.5)
        self.initial_infected: int = config.get('initial_infected', 5)
        self.Pu: float = config.get('Pu', 0.3)
        self.Pc: float = config.get('Pc', 0.3)
        self.Pk: float = config.get('Pk', 0.01)
        self.Pr: float = config.get('Pr', 0.1)
        self.vacfunc: Callable[[int], int] = config.get('Vaccine function', lambda step: 0)
        self.Pn: float = config.get('Pn', 0.02)
        self.initialize_simulation(debug)
        self.stats: dict[str, list[int]] = {
            'healthy': [self.N - self.initial_infected],
            'sick': [self.initial_infected],
            'recovered': [0],
            'vaccinated': [0],
            'dead': [0]
        }
        self.steps: int = 0
        if debug:
            print(f"Simulation started with {self.N} people and {self.initial_infected} initial infections")
            print(f"Population: {self.N}")
            print(f"Initial infected: {self.initial_infected}")
            print(f"Probability of random connection: {self.Pn}")
            print(f"Probability of being immunocompromised: {self.Pi}")
            print(f"Probability of being vaccinated: {self.Pv}")
            print(f"Probability of being asymptomatic: {self.Pa}")
            print(f"Probability of wearing a mask: {self.Pm}")
            print(f"Mask effectiveness: {self.mask_effectiveness}")
            print(f"Probability of spreading the virus: {self.Pu}")
            print(f"Probability of catching the virus: {self.Pc}")
            print(f"Probability of dying: {self.Pk}")
            print(f"Probability of recovering: {self.Pr}")
            print(f"Vaccine function: {self.vacfunc}")

    def initialize_simulation(self, debug = False) -> None:
        """
        Initializes the simulation graph and attributes for each node.

        The graph is generated using the Erdos-Renyi model with the given
        parameters. Each node is then assigned the following attributes:
        - 'status': Literal['healthy', 'sick', 'recovered', 'dead']
        - 'immunocompromised': bool
        - 'asymptomatic': bool
        - 'vaccinated': bool
        - 'masked': bool

        The initial infected nodes are randomly selected.
        """
        if debug:
            print("Initializing simulation with the following parameters:")
            print(f"Population: {self.N}")
            print(f"Probability of random connection: {self.Pn}")
        self.graph = nx.erdos_renyi_graph(self.N, self.Pn)
        for node in self.graph.nodes():
            # add code hereto show initilaizing nodes:
            self.graph.nodes[node]['status'] = 'healthy'
            self.graph.nodes[node]['immunocompromised'] = random.random() < self.Pi
            self.graph.nodes[node]['asymptomatic'] = not self.graph.nodes[node]['immunocompromised'] and random.random() < self.Pa
            self.graph.nodes[node]['vaccinated'] = random.random() < self.Pv
            self.graph.nodes[node]['masked'] = random.random() < self.Pm
            #print(f"Node {node} is {self.graph.nodes[node]}")

        for node in random.sample(list(self.graph.nodes()), self.initial_infected):
            self.graph.nodes[node]['status'] = 'sick'
        if debug:
            print("Simulation initialized")

    def calculate_death_probability(self, node: int) -> float:
        """
        Calculates the probability of a given node dying.

        The probability of a node dying is its base probability (Pk) multiplied
        by 5 if it is immunocompromised and divided by 10 if it is vaccinated or
        asymptomatic. The result is then capped at 1.0.

        Parameters
        ----------
        node: int
            The node whose death probability is being calculated.

        Returns
        -------
        float
            The probability of the given node dying.
        """
        pk: float = self.Pk
        if self.graph.nodes[node]['immunocompromised']:
            pk *= 5
        if self.graph.nodes[node]['vaccinated']:
            pk /= 10
        if self.graph.nodes[node]['asymptomatic']:
            pk /= 10
        return min(pk, 1.0)

    def calculate_recovery_probability(self, node: int) -> float:
        """
        Calculates the probability of a given node recovering.

        The probability of a node recovering is its base probability (Pr)
        divided by 3 if it is immunocompromised and multiplied by 5 if it is
        vaccinated. The result is then capped at 1.0.

        Parameters
        ----------
        node: int
            The node whose recovery probability is being calculated.

        Returns
        -------
        float
            The probability of the given node recovering.
        """
        pr: float = self.Pr
        if self.graph.nodes[node]['immunocompromised']:
            pr /= 3
        if self.graph.nodes[node]['vaccinated']:
            pr *= 5
        return min(pr, 1.0)

    def step(self, step: int, debug: bool = False) -> bool:
        """
        Advances the simulation by one step.

        Parameters
        ----------
        step : int
            The current step number.
        debug : bool, optional
            Whether to print debug information. Defaults to False.

        Returns
        -------
        bool
            Whether there are still sick individuals.
        """
        x: int = self.vacfunc(step)
        new_infections: List[int] = []
        new_recoveries: List[int] = []
        new_deaths: List[int] = []
        new_vaccinations: List[int] = []

        for node in self.graph.nodes():
            if self.graph.nodes[node]['status'] == 'sick':
                if random.random() < self.calculate_death_probability(node):
                    new_deaths.append(node)
                elif random.random() < self.calculate_recovery_probability(node):
                    new_recoveries.append(node)
                else:
                    for neighbor in self.graph.neighbors(node):
                        if self.graph.nodes[neighbor]['status'] == 'healthy':
                            spread_prob: float = self.Pu
                            if self.graph.nodes[node]['vaccinated']:
                                spread_prob /= 2
                            if self.graph.nodes[node]['masked']:
                                if random.random() < self.mask_effectiveness:
                                    continue
                            if self.graph.nodes[neighbor]['masked']:
                                if random.random() < self.mask_effectiveness:
                                    continue
                            if random.random() < spread_prob and random.random() < self.Pc:
                                new_infections.append(neighbor)
        new_vaccinations = random.sample(
            [node for node in self.graph.nodes()
             if not (self.graph.nodes[node]['vaccinated'] and self.graph.nodes[node]['status'] != 'dead')],
            x)

        for node in new_deaths:
            self.graph.nodes[node]['status'] = 'dead'
        for node in new_recoveries:
            self.graph.nodes[node]['status'] = 'recovered'
        for node in new_infections:
            self.graph.nodes[node]['status'] = 'sick'
        for node in new_vaccinations:
            self.graph.nodes[node]['vaccinated'] = True

        current_status: Dict[str, int] = {
            'healthy': 0,
            'sick': 0,
            'recovered': 0,
            'dead': 0,
            'vaccinated': 0
        }
        for node in self.graph.nodes():
            current_status[self.graph.nodes[node]['status']] += 1
            if self.graph.nodes[node]['vaccinated']:
                current_status['vaccinated'] += 1

        self.stats['healthy'].append(current_status['healthy'])
        self.stats['sick'].append(current_status['sick'])
        self.stats['vaccinated'].append(current_status['vaccinated'])
        self.stats['recovered'].append(current_status['recovered'])
        self.stats['dead'].append(current_status['dead'])

        if debug:
            print(f"Day: {step}")
            print(f"{current_status['healthy']} less healthy")
            print(f"{current_status['sick']} more sick")
            print(f"{current_status['recovered']} more recovered")
            print(f"{current_status['dead']} more dead")
            print(f"{current_status['vaccinated']} more vaccinated")
        return current_status['sick'] > 0

    def run_simulation(self, max_steps: int = 100, iteration: int = 0, step: int = 0, debug: bool = False) -> Tuple[int, Dict[str, List[int]]]:
        """
        Run the simulation for the given number of steps.

        Parameters
        ----------
        max_steps : int
            The maximum number of steps to simulate
        iteration : int
            The iteration number (used for printing progress)
        step : int
            The current step number (used for printing progress)
        debug : bool
            Whether to print detailed progress information

        Returns
        -------
        Tuple[int, Dict[str, List[int]]]
            A tuple containing the final step number and the simulation statistics
        """
        while step < max_steps and self.step(step, debug):
            step += 1
            self.print_progress(step, iteration)
            time.sleep(0.01)  # Add a small delay to make the progress visible
        self.steps = step
        return step, self.stats

    def print_progress(self, day: int, iteration: int) -> None:
        """
        Print the current status of the simulation.

        Parameters
        ----------
        day : int
            The current day of the simulation
        iteration : int
            The current iteration number
        """
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
        print(f"Iteration: {iteration}")
        print(f"Day: {day}")
        print(f"Healthy: {self.stats['healthy'][-1]} ({self.stats['healthy'][-1]/self.N*100:.2f}%)")
        print(f"Sick: {self.stats['sick'][-1]} ({self.stats['sick'][-1]/self.N*100:.2f}%)")
        print(f"Vaccinnated: {self.stats['vaccinated'][-1]}" )
        print(f"Recovered: {self.stats['recovered'][-1]} ({self.stats['recovered'][-1]/self.N*100:.2f}%)")
        print(f"Dead: {self.stats['dead'][-1]} ({self.stats['dead'][-1]/self.N*100:.2f}%)")

    def plot_results(self) -> None:
        """
        Plot the results of the simulation.

        The results are plotted as four separate lines, one for each of the
        following categories: healthy, sick, recovered, and dead. The x-axis
        is the day of the simulation, and the y-axis is the number of people
        in each category.

        Returns
        -------
        None
        """
        plt.figure(figsize=(12, 8))
        x: List[int] = list(range(len(self.stats['healthy'])))
        
        plt.plot(x, self.stats['healthy'], label='Healthy', color='green')
        plt.plot(x, self.stats['sick'], label='Sick', color='red')
        plt.plot(x, self.stats['recovered'], label='Recovered', color='blue')
        plt.plot(x, self.stats['dead'], label='Dead', color='black')
        plt.plot(x, self.stats['vaccinated'], label='Vaccinated', color='purple')
        
        plt.xlabel('Days')
        plt.ylabel('Number of People')
        plt.title('Virus Spread Simulation')
        plt.legend()
        plt.grid(True)
        plt.show()

    def print_final_report(self, steps: int, stats: Dict[str, List[int]], config: Dict[str, Union[int, float]]) -> Dict[str, Union[int, float]]:
        """
        Print the final report of the simulation.

        Parameters
        ----------
        steps : int
            The number of steps the simulation took
        stats : Dict[str, List[int]]
            The simulation statistics
        config : Dict[str, Union[int, float]]
            The simulation configuration

        Returns
        -------
        Dict[str, Union[int, float]]
            The final simulation statistics
        """
        print("Final Report:")
        print(f"Simulation completed in {steps} days")
        print(f"Final Counts:")
        print(f"Healthy: {stats['healthy'][-1]}")
        print(f"Sick: {stats['sick'][-1]}")
        print(f"Vaccinated: {stats['vaccinated'][-1]}")
        print(f"Recovered: {stats['recovered'][-1]}")
        print(f"Deaths: {stats['dead'][-1]}")
        print(f"Percentage survived: {(stats['recovered'][-1] + stats['healthy'][-1]) / config['N'] * 100:.2f}%")
        print(f"Percentage died: {stats['dead'][-1] / config['N'] * 100:.2f}%")
        print(f"Percentage untouched: {stats['healthy'][-1] / config['N'] * 100:.2f}%")

        immunocompromised_survived = sum(1 for node in self.graph.nodes() if self.graph.nodes[node]['immunocompromised'] and self.graph.nodes[node]['status'] != 'dead')
        print(f"Percentage of immunocompromised people survived: {immunocompromised_survived / (sum(1 for node in self.graph.nodes() if self.graph.nodes[node]['immunocompromised']) or 1) * 100:.2f}%")
        vaccinated_survived = sum(1 for node in self.graph.nodes() if self.graph.nodes[node]['vaccinated'] and self.graph.nodes[node]['status'] != 'dead')
        print(f"Percentage of vaccinated people survived: {vaccinated_survived / (sum(1 for node in self.graph.nodes() if self.graph.nodes[node]['vaccinated']) or 1) * 100:.2f}%")
        unvaccinated_survived = sum(1 for node in self.graph.nodes() if not self.graph.nodes[node]['vaccinated'] and self.graph.nodes[node]['status'] != 'dead')
        print(f"Percentage of unvaccinated people survived: {unvaccinated_survived / (sum(1 for node in self.graph.nodes() if not self.graph.nodes[node]['vaccinated']) or 1) * 100:.2f}%")

        final_stats = {
            'healthy': stats['healthy'][-1],
            'sick': stats['sick'][-1],
            'recovered': stats['recovered'][-1],
            'dead': stats['dead'][-1],
            'percentage_survived': (stats['recovered'][-1] + stats['healthy'][-1]) / config['N'] * 100,
            'percentage_died': stats['dead'][-1] / config['N'] * 100,
            'percentage_untouched': stats['healthy'][-1] / config['N'] * 100,
            'percentage_immunocompromised_survived': immunocompromised_survived / (sum(1 for node in self.graph.nodes() if self.graph.nodes[node]['immunocompromised']) or 1) * 100,
            'percentage_vaccinated_survived': vaccinated_survived / (sum(1 for node in self.graph.nodes() if self.graph.nodes[node]['vaccinated']) or 1) * 100,
            'percentage_unvaccinated_survived': unvaccinated_survived / (sum(1 for node in self.graph.nodes() if not self.graph.nodes[node]['vaccinated']) or 1) * 100,
            'vaccinated': stats['vaccinated'][-1]
        }
        return final_stats

        
if __name__ == "__main__":
    config = {
        'N': 20000, # Number of people in the population
        'Pn': 0.035, # Probability of a random connection between two people
        'Pi': 0.04, # Probability of a person being immunocompromised
        'Pv': 1.0, # Probability of a person initially vaccinated
        'Pa': 0.25, # Probability of a person being asymptomatic
        'Pm': 0.0, # Probability of a person wearing a mask
        'mask_effectiveness': 0.8, # Effectiveness of masks
        'initial_infected': 10, # Number of initially infected people
        'Pu': 0.95, # Probability of a person spreading the virus
        'Pc': 0.95, # Probability of a person catching the virus
        'Pk': 0.015, # Probability of a person dying
        'Pr': 0.05, # Probability of a person recovering
        'Vaccine function': lambda step: 0
    }
    total_stats = {
        'healthy': [],
        'sick': [],
        'vaccinated': [],
        'recovered': [],
        'dead': [],
        'percentage_survived': [],
        'percentage_died': [],
        'percentage_untouched': [],
        'percentage_immunocompromised_survived': [],
        'percentage_vaccinated_survived': [],
        'percentage_unvaccinated_survived': [],
        
    }
    for i in range(1):
        print("Initializing simulation")
        sim = VirusSimulation(config)
        print(f"Simulation started with {config['N']} people and {config['initial_infected']} initial infections")
        steps, stats = sim.run_simulation(max_steps=1000, iteration=i, debug=True)
        print(f"Simulation completed in {steps} days")
        final_stats = sim.print_final_report()
        for key, value in final_stats.items():
            total_stats[key].append(value)
    os.system('cls' if os.name == 'nt' else 'clear') # Clear console
    for key, value in total_stats.items():
        if "percentage" in key:
            print(f"{key}: {sum(value)/len(value):.2f}%")
        else:
            print(f"{key}: {sum(value)/len(value):.2f}")    
    print("Simulation completed")

